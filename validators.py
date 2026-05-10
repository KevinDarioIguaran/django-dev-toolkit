from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils.translation import gettext_lazy as _
from django.conf import settings

MAX_FILE_SIZE_IMAGES = getattr(settings, 'MAX_FILE_SIZE_IMAGES', 5 * 1024 * 1024)
VALID_EXTENSIONS_IMAGES = getattr(settings, 'VALID_EXTENSIONS_IMAGES', ['jpg', 'jpeg', 'png', 'webp'])
MAX_WIDTH_IMAGES = getattr(settings, 'MAX_WIDTH_IMAGES', 8000)
MAX_HEIGHT_IMAGES = getattr(settings, 'MAX_HEIGHT_IMAGES', 8000)

VALID_EXTENSIONS_IMAGES = [ext.lower() for ext in VALID_EXTENSIONS_IMAGES]

if 'svg' in VALID_EXTENSIONS_IMAGES:
    raise ValueError("SVG no está permitido por razones de seguridad.")


def validate_images(image):
    """
    Validate images uploaded to Django.

    1. Verify that the object is a file uploaded via Django.
    2. Check that the file has a name and extension.
    3. Validate that the extension is within the allowed range in the configuration.
    4. Verify that the size is not None and does not exceed the maximum allowed.
    5. Open the image with PIL to check that it is not corrupted.
    6. Detect the actual file format.
    7. Validate that the actual format is allowed.
    8. Check that the extension matches the actual format (prevents fake files).
    9. Validate that the dimensions do not exceed the configured limits.
    
    If any validation fails, throw a ValidationError with a message.

    If everything is correct, the function does not return anything.
    """
    if not image:
        return

    if not hasattr(image, "name"):
        raise ValidationError(_("Archivo no válido."))

    if not isinstance(image, (InMemoryUploadedFile, TemporaryUploadedFile)):
        raise ValidationError(
            _("%(name)s: Tipo de archivo no permitido.") % {"name": image.name}
        )

    if '.' not in image.name:
        raise ValidationError(
            _("%(name)s: El archivo no tiene extensión.") % {"name": image.name}
        )

    ext = image.name.rsplit('.', 1)[-1].lower()

    if ext not in VALID_EXTENSIONS_IMAGES:
        raise ValidationError(
            _("%(name)s: Extensión no permitida (%(exts)s).") % {
                "name": image.name,
                "exts": ', '.join(VALID_EXTENSIONS_IMAGES),
            }
        )

    if image.size is None or image.size > MAX_FILE_SIZE_IMAGES:
        raise ValidationError(
            _("%(name)s: Excede el tamaño máximo permitido (%(max)s MB).") % {
                "name": image.name,
                "max": MAX_FILE_SIZE_IMAGES // (1024 * 1024),
            }
        )

    try:
        with Image.open(image) as img:
            img.verify()

        image.seek(0)

        with Image.open(image) as img:
            img.load()
            format_real = img.format.lower() if img.format else ""

            if format_real not in VALID_EXTENSIONS_IMAGES:
                raise ValidationError(
                    _("%(name)s: Formato no permitido (%(fmt)s).") % {
                        "name": image.name,
                        "fmt": format_real.upper(),
                    }
                )

            if ext != format_real:
                if not (ext == 'jpg' and format_real == 'jpeg'):
                    raise ValidationError(
                        _("%(name)s: La extensión no coincide con el formato real (%(fmt)s).") % {
                            "name": image.name,
                            "fmt": format_real.upper(),
                        }
                    )

            if img.width > MAX_WIDTH_IMAGES or img.height > MAX_HEIGHT_IMAGES:
                raise ValidationError(
                    _("%(name)s: Dimensiones demasiado grandes (%(w)sx%(h)s).") % {
                        "name": image.name,
                        "w": img.width,
                        "h": img.height,
                    }
                )

    except ValidationError:
        raise

    except (UnidentifiedImageError, IOError, OSError):
        raise ValidationError(
            _("%(name)s: Archivo inválido o corrupto.") % {"name": image.name}
        )

    finally:
        try:
            image.seek(0)
        except Exception:
            pass