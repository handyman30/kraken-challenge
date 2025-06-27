from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_readings, name='search_readings'),
    path('reading/<int:reading_id>/', views.reading_detail, name='reading_detail'),
] 