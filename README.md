# django-dev-toolkit

---

A modular toolkit for Django developers. Reusable utilities for i18n automation, message rendering, image validation, decorators, template tags, multilingual support, and production-grade logging all organized as clean, composable building blocks.

> Built for teams who care about architecture. Designed to eliminate boilerplate without sacrificing control.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Documentation](#documentation)
- [License](#license)

---

## Features

| Category                | Capabilities                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------- |
| **Rendering**     | `MessageRenderer` — type-safe, template-driven JSON message rendering for AJAX and HTMX        |
| **i18n**          | `get_languages_settings()` — database-driven language configuration for Django's `LANGUAGES` |
| **Translation**   | `translate` management command — async, placeholder-safe auto-translation via Google Translate |
| **Validation**    | `validate_images` — deep image validation: extension, size, format, dimensions, corruption     |
| **Decorators**    | `@no_session_required` — redirect authenticated users away from guest-only views               |
| **Template Tags** | `language_info` filter — resolve language name and flag from a language code                   |
| **Signals**       | Auto-regenerate `languages.json` on any `Language` model change                               |                                                                                              |
| **Logging**       | Structured, rotating logs with dedicated security audit channel                                   |

---

## Requirements

- Python >= 3.10
- Django >= 4.2
- Pillow (for image validation)
- polib (for translation management)
- googletrans >= 4.0 (for `translate` command)

---

## Documentation

Detailed documentation is available in the `docs/` directory:

- **[Installation](docs/installation.md)** - How to install and configure django-dev-toolkit
- **[Settings](docs/settings.md)** - Quickstart guide, architecture overview, and module reference
- **[Examples ](docs/examples.md)** - Basic examples of use

---

## License

Unlicense License

---

*django-dev-toolkit is not affiliated with the Django Software Foundation.*
