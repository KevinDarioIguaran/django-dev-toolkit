from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext as _

from django_dev_toolkit.convert_image import convert_image_to_webp
from django_dev_toolkit.validators import validate_images


class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    photo = models.ImageField(upload_to='products/originals/', blank=True, null=True)
    photo_webp = models.ImageField(upload_to='products/webp/', blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.photo:
            image = getattr(self.photo, 'file', self.photo)
            validate_images(image)
        super().clean()

    def save(self, *args, **kwargs):
        if self.photo:
            self.photo.seek(0)
            try:
                webp_buffer = convert_image_to_webp(self.photo, quality=85, max_size=1200)
                filename = f"{Path(self.photo.name).stem}.webp"
                self.photo_webp.save(filename, ContentFile(webp_buffer.getvalue()), save=False)
            except Exception as error:
                raise ValidationError(_("Could not convert the image: %(error)s") % {'error': error}) from error
        else:
            self.photo_webp = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

