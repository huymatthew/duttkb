from django.urls import path
from . import views

urlpatterns = [
    path('tkb_download/', views.tkb_download, name='tkb_download'),
]