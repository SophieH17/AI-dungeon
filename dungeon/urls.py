from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/txt/', views.download_txt, name='download_txt'),
    path('download/csv/', views.download_csv, name='download_csv'),
]