from . import views

from django.urls import path
urlpatterns=[
    path('getdata',views.getdata,name='store'),
    path('',views.home,name=''),


]