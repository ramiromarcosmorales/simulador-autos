from django.db import models


class Solicitud(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    dni = models.CharField(max_length=10)
    telefono = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nombre_garante = models.CharField(max_length=100)
    fecha_nacimiento_garante = models.DateField(null=True, blank=True)
    ingresos_garante = models.DecimalField(max_digits=12, decimal_places=2)
    modelo = models.CharField(max_length=50)
    plan = models.CharField(max_length=50)
    cuota_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    importe_adjudicacion = models.DecimalField(max_digits=12, decimal_places=2)
    importe_retiro = models.DecimalField(max_digits=12, decimal_places=2)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.nombre} - {self.modelo} ({self.plan})"
