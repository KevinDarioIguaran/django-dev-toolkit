# Settings Reference

### MESSAGE_URL_TEMPLATES

**Type:** `str`
**Default:** `'partials/messages/django'`

Base template directory for `MessageRenderer`. The renderer appends `/_<type>.html` to this path.

```python
MESSAGE_URL_TEMPLATES = 'messages/django'
```

### DEFAULT_PROFILE_IMAGE_URL

**Type:** `str`
**Default:** `'/static/assets/images/default_profile.webp'`

URL for the fallback avatar displayed when a user has no uploaded profile image.

```python
DEFAULT_PROFILE_IMAGE_URL = os.getenv(
    "DEFAULT_PROFILE_IMAGE_URL",
    "/static/assets/images/default_profile.webp"
)
```

Always serve this from your CDN or static root in production. Do not expose a path that reveals your directory structure.

---

### VALID_EXTENSIONS_IMAGES

**Type:** `list[str]`
**Default:** `['jpg', 'jpeg', 'png', 'gif', 'webp']`

Allowed file extensions for image uploads. SVG is explicitly prohibited and will raise `ValueError` at startup if included.

```python
VALID_EXTENSIONS_IMAGES = os.getenv(
    "VALID_EXTENSIONS_IMAGES",
    "jpg,jpeg,png,gif,webp"
).split(",")
```

**Production recommendation:** Remove `gif` if animated images are not required. Limit to `['jpg', 'jpeg', 'png', 'webp']` for most web applications.

---

### MAX_FILE_SIZE_IMAGES

**Type:** `int` (bytes)
**Default:** `5242880` (5 MB)

Maximum allowed file size for image uploads. Checked before PIL validation to avoid loading oversized files into memory.

```python
MAX_FILE_SIZE_IMAGES = int(os.getenv("MAX_FILE_SIZE_IMAGES", 5 * 1024 * 1024))
```

---

### DATA_UPLOAD_MAX_MEMORY_SIZE

**Type:** `int` (bytes)
**Default:** `10485760` (10 MB)

Django's built-in limit for in-memory form data. Should be set to at least `MAX_FILE_SIZE_IMAGES` to avoid Django rejecting valid uploads before they reach your validator.

```python
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("DATA_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024))
```

---

### FILE_UPLOAD_MAX_MEMORY_SIZE

**Type:** `int` (bytes)
**Default:** `2097152` (2 MB)

Files smaller than this are held in memory. Larger files are written to a temp file. Tune based on your server's available RAM.

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("FILE_UPLOAD_MAX_MEMORY_SIZE", 2 * 1024 * 1024))
```
