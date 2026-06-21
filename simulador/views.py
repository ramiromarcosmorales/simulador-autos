from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decimal import Decimal
import logging
import requests

from .forms import SimulacionForm
from .models import Solicitud

logger = logging.getLogger(__name__)

# mapeo cada modelo con sus imgs
IMAGENES_MODELOS = {
    'Auron City': 'auron.webp',
    'Velkar Nova': 'velkar.webp',
    'Oryex Prime': 'oryex.png',
    'Zenthor': 'zenthor.png',
}

# valores fijos del simulador
PRECIO_BASE = 8500000
CUOTAS = 84
TASA_ANUAL = 14.50
IMPORTE_RETIRO = 500000


def calcular_simulacion(modelo, plan):
    # porcentajes según el plan elegido
    if plan == 'Plan 70/30':
        porcentaje_adjudicacion = 0.30
        porcentaje_financiado = 0.70
    elif plan == 'Plan 60/40':
        porcentaje_adjudicacion = 0.40
        porcentaje_financiado = 0.60
    elif plan == 'Plan 100%':
        porcentaje_adjudicacion = 0.0
        porcentaje_financiado = 1.0
    else:
        porcentaje_adjudicacion = 0.30
        porcentaje_financiado = 0.70

    adjudicacion = PRECIO_BASE * porcentaje_adjudicacion
    monto_financiado = PRECIO_BASE * porcentaje_financiado
    tasa_mensual = (TASA_ANUAL / 100) / 12

    # fórmula de amortización francesa: cuota = (monto * tasa) / (1 - (1 + tasa)^-n)
    if tasa_mensual > 0:
        cuota_mensual = (monto_financiado * tasa_mensual) / (1 - (1 + tasa_mensual) ** (-CUOTAS))
    else:
        cuota_mensual = monto_financiado / CUOTAS

    # valores numéricos para guardar en la db
    valores = {
        'cuota_mensual_raw': cuota_mensual,
        'adjudicacion_raw': adjudicacion,
        'retiro_raw': IMPORTE_RETIRO,
        'tasa_raw': TASA_ANUAL,
    }

    # valores formateados para mostrar en el informe
    resultado = {
        'modelo': modelo,
        'imagen': IMAGENES_MODELOS.get(modelo, 'hero-car.png'),
        'precio': f"{PRECIO_BASE:,.0f}".replace(",", "."),
        'plan': plan,
        'cuotas': CUOTAS,
        'adjudicacion': f"{adjudicacion:,.0f}".replace(",", "."),
        'retiro': f"{IMPORTE_RETIRO:,.0f}".replace(",", "."),
        'tasa': f"{TASA_ANUAL:.2f}".replace(".", ","),
        'cuota_mensual': f"{cuota_mensual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    }
    return resultado, valores


def index(request):
    if request.method == 'POST':
        form = SimulacionForm(request.POST)

        if form.is_valid():
            modelo = form.cleaned_data['modelo']
            plan = form.cleaned_data['plan']
            resultado, valores = calcular_simulacion(modelo, plan)

            # guardo la solicitud en la BD
            Solicitud.objects.create(
                nombre=form.cleaned_data['nombre'],
                email=form.cleaned_data['email'],
                dni=form.cleaned_data['dni'],
                telefono=form.cleaned_data['telefono'],
                fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                nombre_garante=form.cleaned_data['nombre_garante'],
                fecha_nacimiento_garante=form.cleaned_data.get('fecha_nacimiento_garante'),
                ingresos_garante=Decimal(str(form.cleaned_data['ingresos_garante'])),
                modelo=modelo,
                plan=plan,
                cuota_mensual=Decimal(str(round(valores['cuota_mensual_raw'], 2))),
                importe_adjudicacion=Decimal(str(round(valores['adjudicacion_raw'], 2))),
                importe_retiro=Decimal(str(valores['retiro_raw'])),
                tasa_interes=Decimal(str(valores['tasa_raw'])),
            )

            # envío el correo de confirmación al cliente
            try:
                nombre_cliente = form.cleaned_data['nombre']
                email_cliente = form.cleaned_data['email']
                asunto = 'Confirmación de tu simulación - Plan de Ahorro Automotriz'

                # texto plano como fallback
                cuerpo_texto = (
                    f"Estimado/a {nombre_cliente},\n\n"
                    f"Tu solicitud de simulación fue procesada con éxito. "
                    f"A continuación encontrás el resumen de tu plan:\n\n"
                    f"Vehículo elegido: {modelo}\n"
                    f"Plan seleccionado: {plan}\n"
                    f"Cantidad de cuotas: {CUOTAS}\n"
                    f"Importe de Adjudicación: $ {resultado['adjudicacion']}\n"
                    f"Importe de Retiro (Patentamiento): $ {resultado['retiro']}\n"
                    f"Tasa de Interés: {resultado['tasa']}% anual\n"
                    f"Cuota Mensual Final: $ {resultado['cuota_mensual']}\n\n"
                    f"Ante cualquier consulta, no dudes en contactarnos. "
                    f"Estamos a tu disposición.\n\n"
                    f"© 2026 Plan de Ahorro Automotriz · Todos los derechos reservados"
                )

                logo_url = 'https://i.imgur.com/8tTcsyy.png'
                cuerpo_html = f'''
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f0f0;padding:30px 0;font-family:Arial,Helvetica,sans-serif;">
  <tr>
    <td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <!-- header -->
        <tr>
          <td align="center" style="background-color:#151424;padding:30px 20px;">
            <img src="{logo_url}" alt="Plan de Ahorro Automotriz" style="height:45px;margin-bottom:10px;display:block;max-width:180px;" />
            <p style="color:#ffffff;font-size:14px;margin:0;letter-spacing:1px;">Plan de Ahorro Automotriz</p>
          </td>
        </tr>
        <!-- cuerpo -->
        <tr>
          <td style="padding:35px 40px;">
            <p style="font-size:16px;color:#222222;margin:0 0 20px 0;">Estimado/a <strong>{nombre_cliente}</strong>,</p>
            <p style="font-size:14px;color:#444444;line-height:1.6;margin:0 0 25px 0;">Tu solicitud de simulación fue procesada con éxito. A continuación encontrás el resumen de tu plan:</p>
            <!-- bloque 1: datos del plan -->
            <div style="background-color:#f9f9f9;padding:16px;border-radius:6px;margin-bottom:24px;">
              <p style="margin:4px 0;font-size:14px;color:#444444;"><span style="color:#555555;">Vehículo:</span> <strong style="color:#222222;">{modelo}</strong></p>
              <p style="margin:4px 0;font-size:14px;color:#444444;"><span style="color:#555555;">Plan:</span> <strong style="color:#222222;">{plan}</strong></p>
              <p style="margin:4px 0;font-size:14px;color:#444444;"><span style="color:#555555;">Cuotas:</span> <strong style="color:#222222;">{CUOTAS} meses</strong></p>
            </div>
            <!-- bloque 2: detalle financiero -->
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e0e0;border-radius:6px;overflow:hidden;margin-bottom:25px;">
              <tr>
                <th style="background-color:#151424;color:#ffffff;padding:12px 16px;text-align:left;font-size:13px;">Concepto</th>
                <th style="background-color:#151424;color:#ffffff;padding:12px 16px;text-align:right;font-size:13px;">Valor</th>
              </tr>
              <tr style="background-color:#f5f5f5;">
                <td style="padding:12px 16px;font-size:14px;color:#333333;border-bottom:1px solid #e8e8e8;">Importe de Adjudicación</td>
                <td style="padding:12px 16px;font-size:14px;color:#333333;text-align:right;border-bottom:1px solid #e8e8e8;font-weight:bold;">$ {resultado['adjudicacion']}</td>
              </tr>
              <tr style="background-color:#ffffff;">
                <td style="padding:12px 16px;font-size:14px;color:#333333;border-bottom:1px solid #e8e8e8;">Importe de Retiro (Patentamiento)</td>
                <td style="padding:12px 16px;font-size:14px;color:#333333;text-align:right;border-bottom:1px solid #e8e8e8;font-weight:bold;">$ {resultado['retiro']}</td>
              </tr>
              <tr style="background-color:#f5f5f5;">
                <td style="padding:12px 16px;font-size:14px;color:#333333;border-bottom:1px solid #e8e8e8;">Tasa de Interés</td>
                <td style="padding:12px 16px;font-size:14px;color:#333333;text-align:right;border-bottom:1px solid #e8e8e8;font-weight:bold;">{resultado['tasa']}% anual</td>
              </tr>
              <tr style="background-color:#ffffff;">
                <td style="padding:14px 16px;font-size:15px;color:#151424;font-weight:bold;">Cuota Mensual Final</td>
                <td style="padding:14px 16px;font-size:20px;color:#A75345;text-align:right;font-weight:bold;">$ {resultado['cuota_mensual']}</td>
              </tr>
            </table>
            <p style="font-size:14px;color:#444444;line-height:1.6;margin:0;">Ante cualquier consulta, no dudes en contactarnos. Estamos a tu disposición.</p>
          </td>
        </tr>
        <!-- footer -->
        <tr>
          <td align="center" style="background-color:#151424;padding:20px;">
            <p style="color:#ffffff;font-size:12px;margin:0;">&copy; 2026 Plan de Ahorro Automotriz &middot; Todos los derechos reservados</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
'''

                send_mail(
                    asunto,
                    cuerpo_texto,
                    settings.DEFAULT_FROM_EMAIL,
                    [email_cliente],
                    html_message=cuerpo_html,
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Error al enviar correo a {form.cleaned_data['email']}: {e}")

            # si es AJAX devuelvo JSON, si no renderizo normalmente
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'informe': resultado})

            return render(request, 'simulador/index.html', {
                'form': form,
                'resultado': resultado,
            })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errores = {campo: errores[0] for campo, errores in form.errors.items()}
                return JsonResponse({'status': 'error', 'errores': errores}, status=400)

            return render(request, 'simulador/index.html', {
                'form': form,
                'resultado': None,
            })

    form = SimulacionForm()
    return render(request, 'simulador/index.html', {'form': form, 'resultado': None})


def api_dolar(request):
    # consulto la cotización del dólar oficial en tiempo real
    try:
        response = requests.get(
            'https://dolarapi.com/v1/dolares/oficial',
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        venta = data.get('venta', 0)
        return JsonResponse({'venta': venta})
    except (requests.RequestException, ValueError, KeyError):
        return JsonResponse(
            {'error': 'No se pudo obtener la cotización del dólar.'},
            status=503,
        )


@login_required(login_url='/admin/login/')
def panel_solicitudes(request):
    # solo accesible para usuarios staff
    if not request.user.is_staff:
        return redirect('/admin/login/')

    solicitudes = Solicitud.objects.all().order_by('-fecha_solicitud')
    return render(request, 'simulador/panel.html', {'solicitudes': solicitudes})


# API REST
from rest_framework.generics import ListAPIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser
from .serializers import SolicitudSerializer


class SolicitudListAPIView(ListAPIView):
    queryset = Solicitud.objects.all().order_by('-fecha_solicitud')
    serializer_class = SolicitudSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser]
