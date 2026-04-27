from django.urls import path
from . import views
from .views import crear_admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('tickets/', views.lista_tickets, name='lista_tickets'),
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('ajax/subcategorias/', views.cargar_subcategorias, name='cargar_subcategorias'),
    path('crear-admin/', crear_admin),
    path('logout/', LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
