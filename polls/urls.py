from . import views

from django.urls import path
urlpatterns=[
    path('getdata',views.getdata,name='store'),
    path('junction',views.getJunctionState,name='junctionState'),
    path('',views.home,name=''),
]