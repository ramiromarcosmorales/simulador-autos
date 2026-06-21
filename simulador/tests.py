from django.test import TestCase
from datetime import date, timedelta
from simulador.forms import SimulacionForm, obtener_cuota

class SimuladorFormTestCase(TestCase):
    def setUp(self):
        # 25 years ago
        self.adult_dob = date.today() - timedelta(days=25*365)
        # 15 years ago
        self.minor_dob = date.today() - timedelta(days=15*365)

    def test_valid_form(self):
        # Calculate minimum income required for Plan 100% (or any plan)
        cuota = obtener_cuota('Plan 100%')
        valid_income = int(cuota * 4) + 10000

        data = {
            'nombre': 'John Doe',
            'email': 'john@example.com',
            'dni': '12345678',
            'telefono': '1122334455',
            'fecha_nacimiento': self.adult_dob,
            'nombre_garante': 'Jane Guarantor',
            'fecha_nacimiento_garante': self.adult_dob,
            'ingresos_garante': valid_income,
            'modelo': 'Auron City',
            'plan': 'Plan 100%'
        }
        form = SimulacionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_user_under_18_raises_error(self):
        cuota = obtener_cuota('Plan 100%')
        valid_income = int(cuota * 4) + 10000
        
        data = {
            'nombre': 'Minor User',
            'email': 'minor@example.com',
            'dni': '12345678',
            'telefono': '1122334455',
            'fecha_nacimiento': self.minor_dob,
            'nombre_garante': 'Jane Guarantor',
            'fecha_nacimiento_garante': self.adult_dob,
            'ingresos_garante': valid_income,
            'modelo': 'Auron City',
            'plan': 'Plan 100%'
        }
        form = SimulacionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento', form.errors)
        self.assertEqual(form.errors['fecha_nacimiento'][0], 'El usuario debe ser mayor de 18 años.')

    def test_garante_under_18_raises_error(self):
        cuota = obtener_cuota('Plan 100%')
        valid_income = int(cuota * 4) + 10000
        
        data = {
            'nombre': 'Adult User',
            'email': 'adult@example.com',
            'dni': '12345678',
            'telefono': '1122334455',
            'fecha_nacimiento': self.adult_dob,
            'nombre_garante': 'Minor Guarantor',
            'fecha_nacimiento_garante': self.minor_dob,
            'ingresos_garante': valid_income,
            'modelo': 'Auron City',
            'plan': 'Plan 100%'
        }
        form = SimulacionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento_garante', form.errors)
        self.assertEqual(form.errors['fecha_nacimiento_garante'][0], 'El garante debe ser mayor de 18 años.')

    def test_insufficient_guarantor_income_raises_error(self):
        cuota = obtener_cuota('Plan 100%')
        # Less than 4x cuota
        insufficient_income = int(cuota * 4) - 10000
        
        data = {
            'nombre': 'Adult User',
            'email': 'adult@example.com',
            'dni': '12345678',
            'telefono': '1122334455',
            'fecha_nacimiento': self.adult_dob,
            'nombre_garante': 'Jane Guarantor',
            'fecha_nacimiento_garante': self.adult_dob,
            'ingresos_garante': insufficient_income,
            'modelo': 'Auron City',
            'plan': 'Plan 100%'
        }
        form = SimulacionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingresos_garante', form.errors)
        self.assertTrue(form.errors['ingresos_garante'][0].startswith('Ingreso insuficiente.'))
