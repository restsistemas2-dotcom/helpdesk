from django.urls import path
from . import views
from .views import crear_admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('tickets/', views.lista_tickets, name='lista_tickets'),
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('crear-admin/', crear_admin),
]
