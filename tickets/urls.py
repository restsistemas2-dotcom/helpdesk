from django.urls import path
from . import views
from .views import crear_admin

urlpatterns = [
    path('', views.lista_tickets, name='lista_tickets'),
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('crear-admin/', crear_admin),
]
