import io
import logging
from PIL import Image, ImageOps
import pyvips

logger = logging.getLogger(__name__)


def convert_image_to_webp(image_file, quality=80, max_size=None):
    """
    Convierte una imagen a formato WebP 
    
    Este proceso asume que la imagen ya fue validada previamente (extensión,
    tamaño, dimensiones, formato real, etc.), por lo que se enfoca en procesarla
    de forma eficiente.


    1. Reinicia el puntero del archivo para evitar errores de lectura.
    2. Abre la imagen con Pillow.
    3. Corrige la orientación usando datos EXIF.
    4. Normaliza el modo de color (RGB o RGBA).
    5. Re-encodea la imagen a PNG en memoria para eliminar metadata y contenido oculto.
    6. Carga la imagen en pyvips para procesamiento eficiente.
    7. Redimensiona proporcionalmente si se especifica max_size.
    8. Convierte a WebP con el nivel de calidad indicado.

    Devuelve un objeto BytesIO listo para guardar en Django.

    Beneficios de seguridad:
    - Elimina metadata (EXIF, payload oculto).
    - Evita archivos maliciosos persistentes.
    - Estandariza el formato final.

    Si ocurre un error, lanza RuntimeError.
    """

    try:
        image_file.seek(0)

        img = Image.open(image_file)
        img = ImageOps.exif_transpose(img)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        temp_buffer = io.BytesIO()
        img.save(temp_buffer, format="PNG")
        temp_bytes = temp_buffer.getvalue()
        temp_buffer.close()

        vips_image = pyvips.Image.new_from_buffer(temp_bytes, "", access="sequential")

        if max_size:
            max_dim = max(vips_image.width, vips_image.height)
            if max_dim > max_size:
                scale = max_size / max_dim
                vips_image = vips_image.resize(scale)

        webp_bytes = vips_image.write_to_buffer(".webp", Q=quality)

        return io.BytesIO(webp_bytes)

    except Exception as e:
        logger.error(f"Image conversion failed: {e}")
        raise RuntimeError("Error converting image") from e