import asyncio
import re
import sys

import polib
from googletrans import Translator

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


PLACEHOLDER_RE = re.compile(r'%\([^)]+\)[sd%]|%[sd%]|%%|\{[^}]*\}')
PLACEHOLDER_TOKEN = "\u2593{}\u2593"
BAR_WIDTH = 40


def _protect_placeholders(text: str) -> tuple[str, list[str]]:
    """Replace format specifiers with neutral Unicode tokens before translation."""
    placeholders: list[str] = []

    def replacer(m: re.Match) -> str:
        placeholders.append(m.group(0))
        return PLACEHOLDER_TOKEN.format(len(placeholders) - 1)

    return PLACEHOLDER_RE.sub(replacer, text), placeholders


def _restore_placeholders(text: str, placeholders: list[str]) -> str:
    """Restore original format specifiers after translation."""
    for i, original in enumerate(placeholders):
        text = text.replace(PLACEHOLDER_TOKEN.format(i), original)
    return text


def _extract_placeholder_names(text: str) -> set[str]:
    """Return all named placeholder identifiers found in *text*."""
    names: set[str] = set()
    for m in re.finditer(r'%\(([^)]+)\)[sd%]', text):
        names.add(m.group(1))
    for m in re.finditer(r'\{([^}]+)\}', text):
        names.add(m.group(1))
    return names


def _translation_is_valid(msgid: str, msgstr: str) -> bool:
    """
    Return True when *msgstr* contains every named placeholder present in
    *msgid*. Strings without named placeholders are always considered valid.
    """
    if not msgstr.strip():
        return False
    required = _extract_placeholder_names(msgid)
    return required.issubset(_extract_placeholder_names(msgstr)) if required else True


def _sync_whitespace(msgid: str, msgstr: str) -> str:
    """Mirror the leading and trailing whitespace of *msgid* onto *msgstr*."""
    prefix = re.match(r'^[ \t\r\n]+', msgid)
    suffix = re.search(r'[ \t\r\n]+$', msgid)
    if prefix:
        msgstr = prefix.group(0) + msgstr.lstrip('\r\n\t ')
    if suffix:
        msgstr = msgstr.rstrip('\r\n\t ') + suffix.group(0)
    return msgstr


def _repair_po(po: polib.POFile) -> int:
    """
    Reset every entry whose *msgstr* has mismatched placeholders or leading
    newlines compared with its *msgid*. Returns the number of entries modified.
    """
    fixed = 0
    for entry in po:
        if entry.msgstr and not _translation_is_valid(entry.msgid, entry.msgstr):
            entry.msgstr = ""
            fixed += 1
            continue

        if entry.msgid and entry.msgstr:
            id_nl = entry.msgid.startswith('\n')
            str_nl = entry.msgstr.startswith('\n')
            if id_nl and not str_nl:
                entry.msgstr = '\n' + entry.msgstr
                fixed += 1
            elif not id_nl and str_nl:
                entry.msgstr = entry.msgstr.lstrip('\n')
                fixed += 1
    return fixed


def _render_bar(done: int, total: int, errors: int) -> str:
    """Return a progress bar string for the current translation state."""
    filled = int(BAR_WIDTH * done / total) if total else BAR_WIDTH
    bar = "#" * filled + "-" * (BAR_WIDTH - filled)
    pct = int(100 * done / total) if total else 100
    return f"  [{bar}] {pct:3d}%  {done}/{total}  errors {errors}"


class Command(BaseCommand):
    """Create and auto-translate .po files using Google Translate."""

    help = "Create and translate .po files using Google Translate"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--lang", type=str, help="Target a single locale (e.g. --lang es)")
        parser.add_argument("--delay", type=float, default=0.1)
        parser.add_argument("--skip-make", action="store_true")
        parser.add_argument("--workers", type=int, default=10)

    def handle(self, *args, **options) -> None:
        asyncio.run(self._handle_async(*args, **options))

    async def _handle_async(self, *args, **options) -> None:
        target_lang = options.get("lang")
        delay = options["delay"]
        concurrency = options["workers"]

        all_languages = (
            [(target_lang, dict(settings.LANGUAGES).get(target_lang, target_lang))]
            if target_lang
            else list(settings.LANGUAGES)
        )
        languages = [(c, n) for c, n in all_languages if c != settings.LANGUAGE_CODE]

        if not options["skip_make"]:
            for lang_code, _ in languages:
                self.stdout.write(self.style.HTTP_INFO(f"  [{lang_code}] makemessages "), ending="")
                self.stdout.flush()
                try:
                    call_command(
                        "makemessages",
                        locale=[lang_code],
                        ignore_patterns=[
                            "venv/*", ".git/*", "node_modules/*", "static/*",
                            "staticfiles/*", "media/*", "logs/*",
                            "library/pipelines/*", "resources/*", ".venv/*",
                            "*.pyc", "__pycache__/*",
                        ],
                        verbosity=0,
                    )
                    self.stdout.write(self.style.SUCCESS("done"))
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"  FAILED  {exc}"))

        self.stdout.write(self.style.HTTP_INFO("\nTranslating\n"))

        for idx, (lang_code, lang_name) in enumerate(languages, start=1):
            self.stdout.write(
                self.style.HTTP_INFO(f"[{idx}/{len(languages)}] {lang_code}  {lang_name}")
            )

            po_path = self._find_po(lang_code)
            if not po_path:
                self.stdout.write(self.style.ERROR("  .po file not found"))
                continue

            po = polib.pofile(str(po_path))

            repaired = _repair_po(po)
            if repaired:
                self.stdout.write(self.style.WARNING(f"  {repaired} corrupt entries repaired"))
                po.save()

            untranslated = po.untranslated_entries()
            if not untranslated:
                self.stdout.write(self.style.SUCCESS("  Nothing to translate\n"))
                continue

            self.stdout.write(self.style.MIGRATE_LABEL(f"  File   {po_path}"))
            self.stdout.write(self.style.MIGRATE_LABEL(f"  Total  {len(untranslated)} strings\n"))

            ok, errors = await self._translate_entries(
                untranslated, settings.LANGUAGE_CODE, lang_code, delay, concurrency
            )
            po.save()

            sys.stdout.write("\r" + " " * (BAR_WIDTH + 30) + "\r")
            self.stdout.write(self.style.SUCCESS(f"  Saved   {ok} translated"))
            if errors:
                self.stdout.write(self.style.ERROR(f"  Errors  {errors} skipped"))
            self.stdout.write("")

        self.stdout.write(self.style.HTTP_INFO("\nCompiling .mo files\n"))
        try:
            call_command("compilemessages", ignore=["venv"], verbosity=1)
            self.stdout.write(self.style.SUCCESS("Done"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"compilemessages failed  {exc}"))

    async def _translate_entries(
        self,
        entries: list,
        src: str,
        dest: str,
        delay: float,
        concurrency: int,
    ) -> tuple[int, int]:
        """
        Translate *entries* from *src* to *dest* with bounded concurrency,
        rendering a live progress bar while work is in flight.
        Returns ``(translated_count, error_count)``.
        """
        semaphore = asyncio.Semaphore(concurrency)
        translator = Translator()
        translated_count = 0
        error_count = 0
        valid = [e for e in entries if e.msgid.strip()]
        total = len(valid)
        done = 0

        def redraw() -> None:
            bar = _render_bar(done, total, error_count)
            sys.stdout.write("\r" + bar)
            sys.stdout.flush()

        async def translate_one(entry) -> None:
            nonlocal translated_count, error_count, done
            async with semaphore:
                for attempt in range(3):
                    try:
                        protected, placeholders = _protect_placeholders(entry.msgid)
                        result = await translator.translate(protected, src=src, dest=dest)
                        translated = _restore_placeholders(result.text, placeholders)

                        if not _translation_is_valid(entry.msgid, translated):
                            if attempt < 2:
                                await asyncio.sleep(0.5)
                                continue
                            error_count += 1
                            done += 1
                            redraw()
                            return

                        entry.msgstr = _sync_whitespace(entry.msgid, translated)
                        translated_count += 1
                        done += 1
                        redraw()
                        if delay > 0:
                            await asyncio.sleep(delay)
                        return

                    except Exception:
                        if attempt < 2:
                            await asyncio.sleep(1)
                            continue
                        error_count += 1
                        done += 1
                        redraw()
                        return

        redraw()
        await asyncio.gather(*[translate_one(e) for e in valid])
        return translated_count, error_count

    def _find_po(self, lang_code: str):
        """Return the path to the django.po file for *lang_code*, or None."""
        for locale_path in settings.LOCALE_PATHS:
            path = locale_path / f"{lang_code}/LC_MESSAGES/django.po"
            if path.exists():
                return path
        return None