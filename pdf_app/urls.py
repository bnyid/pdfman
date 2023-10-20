from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('merge-pdf/', views.merge_pdf, name='merge_pdf'),
    path('serve-pdf/', views.serve_pdf, name='serve_pdf'),
]
