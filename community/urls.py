from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index),
    path('lend/', views.lend),
    path('borrow/', views.borrow),
    path('chats/', views.chats),
    path('create-offering-for-demand/<int:id>/', views.create_offering),
    path('deal/<str:id>/ongoing/', views.dealing),
    path('deal/<str:id>/closing/', views.closing_deal),
    path('deal/<int:id>/closed/', views.deal),
]
