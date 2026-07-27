from django.db import models
from django.utils.translation import gettext_lazy as _

    
class Language(models.Model):
    code   = models.CharField(max_length=10, unique=True, db_index=True, verbose_name=_('Código'))
    name   = models.CharField(max_length=100, db_index=True, verbose_name=_('Nombre'))
    is_rtl = models.BooleanField(default=False, verbose_name=_('RTL'))
    is_ui  = models.BooleanField(default=True, verbose_name=_('UI'), help_text=_('Visible in language switcher'))
    country_code = models.CharField(max_length=10, verbose_name=_('Código'), blank=True, null=True)
    class Meta:
        verbose_name        = _('Idioma')
        verbose_name_plural = _('Idiomas')
        ordering            = ['name']

    def __str__(self):
        return self.name