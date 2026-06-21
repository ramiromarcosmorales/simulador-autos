from django.contrib import admin

from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'dni', 'fecha_nacimiento', 'nombre_garante', 'fecha_nacimiento_garante', 'modelo', 'plan', 'cuota_mensual', 'fecha_solicitud')
    list_filter = ('modelo', 'plan')
    search_fields = ('nombre', 'email', 'dni', 'nombre_garante')
    readonly_fields = ('fecha_solicitud',)
