from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('detail/<str:id>', views.detail, name='detail'),
]
