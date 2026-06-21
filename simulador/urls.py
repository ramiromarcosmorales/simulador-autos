from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/dolar/', views.api_dolar, name='api_dolar'),
    path('api/solicitudes/', views.SolicitudListAPIView.as_view(), name='api_solicitudes'),
    path('panel/solicitudes/', views.panel_solicitudes, name='panel_solicitudes'),
]
