"""
URL configuration for prueba_tecnica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from server.api import router as safeguard_router

# 🧩 Crear la API principal
api = NinjaAPI(
    title="Informes de Resguardo API",
    description="Microservicio para generar informes de resguardo de maquinaria forestal.",
    version="1.0.0",
)

# 🔗 Agregar el router de la app
api.add_router("/", safeguard_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),  # ✅ Ruta principal para los endpoints
]
