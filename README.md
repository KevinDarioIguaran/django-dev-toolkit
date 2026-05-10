# django-dev-toolkit

---

A modular Django toolkit providing reusable components for common backend needs such as i18n automation, message rendering, image validation, decorators, template tags, multilingual support, and structured logging.

Designed to reduce boilerplate while keeping explicit control over system behavior.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Documentation](#documentation)
- [License](#license)

---

## Features

| Category         | Capabilities |
|----------------|--------------|
| **Rendering**   | `MessageRenderer` — type-safe, template-driven JSON message rendering for AJAX and HTMX |
| **i18n**        | `get_languages_settings()` — database-driven language configuration for Django's `LANGUAGES` |
| **Translation** | `translate` management command — async, placeholder-safe auto-translation via Google Translate *(dev only)* |
| **Validation**  | `validate_images` — deep image validation: extension, size, format, dimensions, corruption |
| **Decorators**  | `@no_session_required` — redirect authenticated users away from guest-only views |
| **Template Tags** | `language_info` filter — resolve language name and flag from a language code |
| **Signals**     | Auto-regenerates `languages.json` on `Language` model changes (post_save) |
| **Logging**     | Structured logging with rotation and dedicated security audit channel |

---

## Requirements

- Python >= 3.10
- Django >= 4.2
- Pillow (image validation)
- polib (translation management)
- googletrans >= 4.0 *(development only, not recommended for production)*

---

## Documentation

Detailed documentation is available in the `docs/` directory:

- **[Installation](docs/installation.md)** — How to install and configure django-dev-toolkit  
- **[Settings](docs/settings.md)** — Quickstart guide, architecture overview, and module reference  
- **[Examples](docs/examples.md)** — Basic usage examples  

---

## License

This project is licensed under the Unlicense.

---

*django-dev-toolkit is not affiliated with the Django Software Foundation.*