# Usage

## Quickstart

### 1. Configure Languages from the Database

```python
# settings.py
from django_dev_toolkit.languages import get_languages_settings

LANGUAGES = get_languages_settings()
LANGUAGE_CODE = 'es'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### 2. Use MessageRenderer in Views

```python
from django_dev_toolkit.renderers import MessageRenderer

# Render form validation errors
return JsonResponse({
    'error': MessageRenderer('error', form.errors).render()
}, status=400)

# Render a success message
return JsonResponse({
    'message': MessageRenderer('success', "Verification code sent.").render()
}, status=202)
```

### 3. Protect Guest-Only Views

```python
from django_dev_toolkit.decorators import no_session_required

@no_session_required
def login_view(request):
    ...
```

### 4. Auto-Translate Your Project

```bash
python manage.py translate
python manage.py translate --lang es
python manage.py translate --workers 10 --delay 0.1
```

---

## Architecture Overview

`django-dev-toolkit` is organized around a single principle: **each utility should do exactly one thing, be independently importable, and impose no side effects on unrelated parts of your project.**

```
django_dev_toolkit/
├── renderers.py          # MessageRenderer — template-driven JSON responses
├── languages.py          # Language helpers and get_languages_settings()
├── validators.py         # validate_images() — multi-layer image validation
├── decorators.py         # @no_session_required
├── signals.py            # Auto-regenerate languages.json on Language changes
├── models.py             # Language model (code, name, is_rtl, country_code)
├── admin.py              # Admin registration for Language model
├── apps.py               # AppConfig — connects signals on ready()
├── convert_image.py      # Image format conversion utilities
├── templatetags/
│   ├── lang_flags.py     # |language_info filter
│   └── permissions.py    # Permission-based template helpers
├── management/commands/
│   └── translate.py      # Async translate management command
├── templates/
│   └── messages/django/  # Default message partials (_error, _success, etc.)
└── static/vendor/
    └── flag-icons/        # Bundled SVG flag icon set (4x3)
```

**Design goals:**

- No monolithic `utils.py`. Every module has a defined responsibility.
- Settings are optional. Sensible defaults ship out of the box; override only what you need.
- Zero coupling between modules. Import only what your view, command, or form requires.
- Template-driven output. The renderer delegates to your templates — not hardcoded HTML strings.

---

## Module Reference

### MessageRenderer

`django_dev_toolkit.renderers.MessageRenderer`

The `MessageRenderer` produces rendered HTML fragments from Django templates, suitable for injection into JavaScript-controlled UIs via JSON responses. It supports four message types: `error`, `success`, `warning`, and `info`.

#### How It Works

1. You instantiate `MessageRenderer(message_type, content)`.
2. The content is normalized: strings pass through, `dict` objects (such as `form.errors`) are flattened to a single string, and lists are joined.
3. `.render()` calls Django's `render_to_string`, resolving the template path from `MESSAGE_URL_TEMPLATES`.
4. The rendered HTML string is returned, ready to be embedded in a `JsonResponse`.

#### Content Normalization

| Input type           | Behavior                                         |
| -------------------- | ------------------------------------------------ |
| `str`              | Passed through as-is                             |
| `dict`             | All error lists flattened and joined with spaces |
| `list` / `tuple` | Items joined with spaces                         |
| Other                | Converted via `str()`                          |

#### Basic Usage

```python
from django_dev_toolkit.renderers import MessageRenderer

# From a string message
MessageRenderer('success', "Profile updated successfully.").render()

# From Django form errors (dict)
MessageRenderer('error', form.errors).render()

# From a custom list
MessageRenderer('warning', ["Field A is required.", "Field B is invalid."]).render()
```

#### In Views

```python
from django.http import JsonResponse
from django_dev_toolkit.renderers import MessageRenderer

@login_required
@require_POST
def change_profile_image(request):
    form = ChangeProfilePhotoForm(request.POST, request.FILES, user=request.user)

    if not form.is_valid():
        return JsonResponse(
            {'error': MessageRenderer('error', form.errors).render()},
            status=400
        )

    form.save()
    return JsonResponse({'profile_image_url': request.user.profile_image.url}, status=200)
```

```python
@login_required
@require_POST
def change_email_view(request):
    form = ChangeEmailForm(request.POST, user=request.user)

    if not form.is_valid():
        return JsonResponse(
            {"error": MessageRenderer('error', form.errors).render()},
            status=400
        )

    send_email_change_code.delay(user_id=request.user.pk, new_email=form.cleaned_data["email"])

    return JsonResponse({
        "message": MessageRenderer(
            'success',
            "A 6-digit verification code was sent to your new email address."
        ).render()
    }, status=202)
```

#### Template Resolution

The renderer constructs the template path as:

```
{MESSAGE_URL_TEMPLATES}/_{message_type}.html
```

With the default setting `MESSAGE_URL_TEMPLATES = 'partials/messages/django'`, the resolved paths are:

```
partials/messages/django/_error.html
partials/messages/django/_success.html
partials/messages/django/_warning.html
partials/messages/django/_info.html
```

The toolkit ships default templates at `django_dev_toolkit/templates/messages/django/`. To customize them, create matching paths inside your project's `templates/` directory. Django's template loader will find yours first.

#### Default Template Structure

```html
<!-- templates/partials/messages/django/_success.html -->
<div class="alert alert-success" role="alert">
  {{ content }}
</div>
```

```html
<!-- templates/partials/messages/django/_error.html -->
<div class="alert alert-danger" role="alert">
  {{ content }}
</div>
```

#### HTMX Integration

```javascript
// JavaScript — inject the rendered HTML directly into the DOM
fetch('/api/change-email/', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      document.getElementById('message-container').innerHTML = data.error;
    } else {
      document.getElementById('message-container').innerHTML = data.message;
    }
  });
```

#### HTMX Out-of-Band Swaps

With HTMX you can return the rendered fragment as part of a normal HTML response using `hx-swap-oob`:

```html
<div id="message-container" hx-swap-oob="true">
  {{ rendered_message }}
</div>
```

#### Alpine.js Integration

```html
<div x-data="{ message: '', type: '' }">
  <div x-show="message" :class="`alert alert-${type}`" x-html="message"></div>
</div>

<script>
  fetch('/api/endpoint/', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
      Alpine.store('notifications').show(data.error || data.message);
    });
</script>
```

> **Note:** Always set `MESSAGE_URL_TEMPLATES` explicitly in production. The default path ships with the package for development convenience, but your production templates directory should own this presentation layer.

---

### Language System

`django_dev_toolkit.languages`

The language system bridges Django's `LANGUAGES` setting with a database-driven `Language` model. This allows you to add, remove, or modify supported languages through the Django admin without redeploying.

#### Language Model

```python
class Language(models.Model):
    code         = models.CharField(max_length=10, unique=True)  # e.g. 'es', 'vi', 'he'
    name         = models.CharField(max_length=100)              # e.g. 'Spanish'
    is_rtl       = models.BooleanField(default=False)            # Right-to-left script
    country_code = models.CharField(max_length=10, blank=True)   # For flag display, e.g. 'es'
```

#### get_languages_settings()

Reads from a cached JSON file at `{BASE_DIR}/resources/languages/languages.json` and returns a list of `(code, name)` tuples suitable for Django's `LANGUAGES` setting.

```python
# settings.py
from django_dev_toolkit.languages import get_languages_settings

LANGUAGES = get_languages_settings()
```

If the JSON file does not exist (e.g. on first install), the function falls back to `[('es', 'Spanish'), ('en', 'English')]` and logs a warning.

#### generate_languages_file()

Called automatically by signals when any `Language` record is created, modified, or deleted. Can also be invoked manually:

```python
from django_dev_toolkit.languages import generate_languages_file
generate_languages_file()
```

This writes `resources/languages/languages.json`:

```json
[
  { "code": "es", "name": "Spanish", "is_rtl": false, "country_code": "es" },
  { "code": "vi", "name": "Vietnamese", "is_rtl": false, "country_code": "vn" },
  { "code": "he", "name": "Hebrew", "is_rtl": true, "country_code": "il" }
]
```

#### get_language_info(lang_code)

Returns display metadata for a given language code — useful for UI components:

```python
from django_dev_toolkit.languages import get_language_info

get_language_info('vi')
# {'name': 'Vietnamese', 'flag_code': 'vn'}
```

Falls back to `{'name': lang_code, 'flag_code': 'un'}` if the language is not found.

#### RTL Support

The `is_rtl` field signals right-to-left layout requirements. Use it in your templates:

```html
{% load lang_flags %}
{% with info=request.LANGUAGE_CODE|language_info %}
  <html lang="{{ request.LANGUAGE_CODE }}" dir="{% if info.is_rtl %}rtl{% else %}ltr{% endif %}">
{% endwith %}
```

#### Locale Configuration

```python
# settings.py
LANGUAGE_CODE = 'es'       # Default/source language
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

Your locale directory structure should be:

```
locale/
├── es/LC_MESSAGES/django.po
├── vi/LC_MESSAGES/django.po
├── he/LC_MESSAGES/django.po
└── ...
```

---

### Translation Command

`python manage.py translate`

An async, placeholder-safe auto-translation system backed by Google Translate. Designed for projects with many languages where manual translation is not practical for initial scaffolding.

#### How It Works

1. For each configured language (excluding the source language), `makemessages` is called to extract all untranslated strings into `.po` files.
2. Each `.po` file is scanned for corruption. Entries with mismatched or missing placeholders are reset before translation begins.
3. Untranslated entries are batched and dispatched to Google Translate using bounded async concurrency (`asyncio.Semaphore`).
4. **Placeholder protection:** Before translation, format specifiers like `%(name)s`, `{variable}`, `%s`, `%%` are replaced with neutral Unicode tokens (e.g. `░0░`). After translation, they are restored. This prevents Google Translate from mangling Python string formatting.
5. Translated entries are validated: every named placeholder in `msgid` must appear in `msgstr`. Entries that fail validation after 3 attempts are skipped and reported as errors.
6. Whitespace mirroring: leading and trailing whitespace from the source string is applied to the translation.
7. After all languages are processed, `compilemessages` is called to produce `.mo` files.

#### Placeholder Protection in Detail

The regex used to identify placeholders:

```
%\([^)]+\)[sd%]   →  %(name)s  %(count)d
%[sd%]            →  %s  %d
%%                →  literal percent
\{[^}]*\}         →  {variable}  {}
```

Protected strings are translated with tokens in place:

```
"Hello, %(name)s!"  →  "Hola, ░0░!"  (after restore: "Hola, %(name)s!")
```

Validation checks that all named identifiers present in `msgid` also appear in `msgstr`.

#### Commands

```bash
# Translate all configured languages
python manage.py translate

# Translate a single language
python manage.py translate --lang es

# Control concurrency (default: 10 workers)
python manage.py translate --workers 20

# Control delay between requests (default: 0.1s)
python manage.py translate --delay 0.5

# Skip makemessages (translate only, no extraction)
python manage.py translate --skip-make

# Combined
python manage.py translate --lang vi --workers 5 --delay 0.2
```

#### Options Reference

| Option          | Type      | Default       | Description                                     |
| --------------- | --------- | ------------- | ----------------------------------------------- |
| `--lang`      | `str`   | all languages | Limit translation to a single locale            |
| `--workers`   | `int`   | `10`        | Max concurrent async translation requests       |
| `--delay`     | `float` | `0.1`       | Seconds to wait between individual translations |
| `--skip-make` | flag      | `False`     | Skip `makemessages` extraction step           |

#### Progress Display

The command renders a live progress bar to stdout:

```
[2/5] vi  Vietnamese
  File   /app/locale/vi/LC_MESSAGES/django.po
  Total  143 strings

  [########################################]  100%  143/143  errors 0
  Saved   143 translated
```

#### Corruption Repair

Before translating, `_repair_po()` inspects all existing entries. An entry is considered corrupt if:

- Its `msgstr` is missing named placeholders that exist in `msgid`.
- Its `msgstr` has a leading newline but `msgid` does not (or vice versa).

Corrupt entries are reset to `msgstr = ""` so they will be re-translated on the next run. The number of repaired entries is reported.

#### Retry Logic

Each entry gets up to 3 translation attempts. On failure or validation mismatch, the worker sleeps briefly before retrying. After 3 failures, the entry is counted as an error and skipped — the `.po` file is still saved with all successful translations.

#### Performance Considerations

- With `--workers 10` and `--delay 0.1`, expect approximately 50–80 strings per minute per language via the free Google Translate endpoint.
- For large projects (500+ strings, 10+ languages), consider running `--skip-make` after initial extraction to avoid repeated file scanning.
- The semaphore-based concurrency model prevents overwhelming the translation API while maximizing throughput.

> **Warning:** The `translate` command uses the `googletrans` library which relies on an unofficial Google Translate endpoint. For production-grade translation pipelines, integrate with DeepL, LibreTranslate, or another authenticated provider and replace the `translator.translate()` call in `_translate_entries`.

---

### Validators

`django_dev_toolkit.validators.validate_images`

A multi-layer image validator that goes beyond extension checking. Designed to prevent malicious uploads, oversized files, and format spoofing.

#### Validation Pipeline

1. **Object check** — Verifies the input has a `name` attribute.
2. **Instance check** — Requires `InMemoryUploadedFile` or `TemporaryUploadedFile`.
3. **Extension present** — Rejects files with no extension.
4. **Extension allowed** — Checks against `VALID_EXTENSIONS_IMAGES`.
5. **SVG blocked** — SVG is always rejected at configuration time (XSS risk).
6. **Size check** — Rejects if `image.size > MAX_FILE_SIZE_IMAGES`.
7. **PIL verify** — Opens the image and calls `.verify()` to detect corruption.
8. **Format detection** — Reads the actual image format reported by PIL.
9. **Format allowed** — Checks the real format against `VALID_EXTENSIONS_IMAGES`.
10. **Extension/format match** — Catches files with mismatched names (e.g., a JPEG renamed to `.png`). The `jpg`/`jpeg` alias is handled correctly.
11. **Dimension check** — Rejects images exceeding `MAX_WIDTH_IMAGES` × `MAX_HEIGHT_IMAGES`.

#### Usage in a Form

```python
from django import forms
from django_dev_toolkit.validators import validate_images

class ProfilePhotoForm(forms.Form):
    photo = forms.ImageField()

    def clean_photo(self):
        image = self.cleaned_data.get('photo')
        validate_images(image)
        return image
```

#### Usage in a Model Field

```python
from django.db import models
from django_dev_toolkit.validators import validate_images

class UserProfile(models.Model):
    avatar = models.ImageField(
        upload_to='avatars/',
        validators=[validate_images]
    )
```

#### Configuration

```python
# settings.py
VALID_EXTENSIONS_IMAGES = ['jpg', 'jpeg', 'png', 'webp']  # SVG always rejected
MAX_FILE_SIZE_IMAGES = 5 * 1024 * 1024                     # 5 MB
MAX_WIDTH_IMAGES = 8000                                     # pixels
MAX_HEIGHT_IMAGES = 8000                                    # pixels
```

> **Security note:** Never add `svg` to `VALID_EXTENSIONS_IMAGES`. The validator raises `ValueError` at startup if SVG is present in the list. SVG files can contain embedded JavaScript and must not be served as user-uploaded content without a dedicated sanitization pipeline.

---

### Decorators

`django_dev_toolkit.decorators`

#### @no_session_required

Redirects authenticated users away from views intended for unauthenticated visitors (login, registration, password reset). Uses `INDEX_URL` from settings as the redirect target.

```python
from django_dev_toolkit.decorators import no_session_required

@no_session_required
def login_view(request):
    ...

@no_session_required
def register_view(request):
    ...
```

**Implementation:**

```python
def no_session_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(getattr(settings, 'INDEX_URL', '/'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

Set the redirect target in settings:

```python
INDEX_URL = 'blog:index'   # Named URL pattern
# or
INDEX_URL = '/'            # Absolute path
```

---

### Template Tags

`django_dev_toolkit.templatetags`

#### lang_flags — `language_info` filter

Resolves a language code to display metadata from the database.

```python
# Load in template
{% load lang_flags %}

# Usage
{% with info=lang_code|language_info %}
  <span class="fi fi-{{ info.flag_code }}"></span>
  {{ info.name }}
{% endwith %}
```

Returns a dict:

```python
{'name': 'Vietnamese', 'flag_code': 'vn'}
```

Falls back to `{'name': lang_code, 'flag_code': 'un'}` if the language is not in the database.

#### Flag Icons

The toolkit ships a complete SVG flag icon set at `django_dev_toolkit/static/vendor/flag-icons/`. Include the CSS in your base template:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'vendor/flag-icons/css/flag-icons.min.css' %}">
```

Use a flag with the `fi fi-{country_code}` class:

```html
<span class="fi fi-es"></span>   <!-- Spain -->
<span class="fi fi-vn"></span>   <!-- Vietnam -->
<span class="fi fi-il"></span>   <!-- Israel -->
```

#### Language Switcher Example

```html
{% load i18n lang_flags %}
{% get_current_language as LANGUAGE_CODE %}
{% get_available_languages as LANGUAGES %}

<ul class="language-switcher">
  {% for code, name in LANGUAGES %}
    {% with info=code|language_info %}
      <li class="{% if code == LANGUAGE_CODE %}active{% endif %}">
        <a href="{% url 'set_language' %}?language={{ code }}&next={{ request.path }}">
          <span class="fi fi-{{ info.flag_code }}"></span>
          {{ info.name }}
        </a>
      </li>
    {% endwith %}
  {% endfor %}
</ul>
```

---

### Signals

`django_dev_toolkit.signals`

Three signals are connected automatically when the app is ready (via `AppConfig.ready()`):

| Signal                          | Trigger             | Action                                         |
| ------------------------------- | ------------------- | ---------------------------------------------- |
| `pre_save` on `Language`    | Before save         | Snapshots current state to `_original_state` |
| `post_save` on `Language`   | After create/update | Calls `generate_languages_file()`            |
| `post_delete` on `Language` | After delete        | Calls `generate_languages_file()`            |

This ensures that `resources/languages/languages.json` is always in sync with the database. No manual regeneration is needed after admin changes.
