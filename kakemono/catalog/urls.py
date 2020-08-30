from django.urls import path

from . import views

urlpatterns = [
    path('wsg/<int:thread_id>/', views.index, name='index'),
    path('wsg/', views.index, name='index'),
]
