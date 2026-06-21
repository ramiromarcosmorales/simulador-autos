from django import forms
from datetime import date

MODELOS_CHOICES = [
    ('', 'Seleccioná un vehículo'),
    ('Auron City', 'Auron City'),
    ('Velkar Nova', 'Velkar Nova'),
    ('Oryex Prime', 'Oryex Prime'),
    ('Zenthor', 'Zenthor'),
]

PLAN_CHOICES = [
    ('', 'Seleccioná un plan'),
    ('Plan 70/30', 'Plan 70/30'),
    ('Plan 60/40', 'Plan 60/40'),
    ('Plan 100%', 'Plan 100%'),
]

PRECIO_BASE = 8500000
CUOTAS = 84
TASA_ANUAL = 14.50

def obtener_cuota(plan):
    if plan == 'Plan 70/30':
        porcentaje_financiado = 0.70
    elif plan == 'Plan 60/40':
        porcentaje_financiado = 0.60
    elif plan == 'Plan 100%':
        porcentaje_financiado = 1.0
    else:
        porcentaje_financiado = 0.70

    monto_financiado = PRECIO_BASE * porcentaje_financiado
    tasa_mensual = (TASA_ANUAL / 100) / 12

    if tasa_mensual > 0:
        cuota_mensual = (monto_financiado * tasa_mensual) / (1 - (1 + tasa_mensual) ** (-CUOTAS))
    else:
        cuota_mensual = monto_financiado / CUOTAS
    return cuota_mensual


class SimulacionForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresá tu nombre completo',
        }),
        label='Nombre',
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'felipe@email.com',
        }),
        label='Email',
    )
    dni = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '11111111',
        }),
        label='DNI',
    )
    telefono = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1155667788',
        }),
        label='Teléfono',
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='Fecha de Nacimiento',
    )
    nombre_garante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo del garante',
        }),
        label='Nombre del Garante',
    )
    fecha_nacimiento_garante = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='Fecha de Nacimiento del Garante',
    )
    ingresos_garante = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1500000',
        }),
        label='Ingresos Mensuales',
    )
    modelo = forms.ChoiceField(
        choices=MODELOS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'selectModelo',
        }),
        label='Modelo',
    )
    plan = forms.ChoiceField(
        choices=PLAN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'selectPlan',
        }),
        label='Plan',
    )

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '')
        if not dni.isdigit():
            raise forms.ValidationError('El DNI debe contener solo números.')
        return dni

    def clean(self):
        cleaned_data = super().clean()
        today = date.today()

        # Validación edad usuario (mínimo 18 años)
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            edad_usuario = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad_usuario < 18:
                self.add_error('fecha_nacimiento', 'El usuario debe ser mayor de 18 años.')

        # Validación edad garante (mínimo 18 años)
        fecha_nacimiento_garante = cleaned_data.get('fecha_nacimiento_garante')
        if fecha_nacimiento_garante:
            edad_garante = today.year - fecha_nacimiento_garante.year - ((today.month, today.day) < (fecha_nacimiento_garante.month, fecha_nacimiento_garante.day))
            if edad_garante < 18:
                self.add_error('fecha_nacimiento_garante', 'El garante debe ser mayor de 18 años.')

        # Validación de ingresos mínimos del garante (neto > 4 veces la cuota)
        ingresos_garante = cleaned_data.get('ingresos_garante')
        plan = cleaned_data.get('plan')
        if ingresos_garante is not None and plan:
            cuota = obtener_cuota(plan)
            ingreso_minimo = cuota * 4
            if ingresos_garante < ingreso_minimo:
                ingreso_minimo_str = f"{ingreso_minimo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                self.add_error('ingresos_garante', f'Ingreso insuficiente. El ingreso mínimo requerido para el garante es de ${ingreso_minimo_str}.')

        return cleaned_data
