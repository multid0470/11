from django.urls import path
from . import views
from django.contrib import admin
from .views import generate_from_github

urlpatterns = [
    path('docs/', views.some_view), 
    path('admin/', admin.site.urls),
    path('api/generate-from-github/', generate_from_github, name='generate_from_github'), # Пример
]




