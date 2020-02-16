from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.new_post, name='new_post'),
    path('group/<slug:slug>/', views.group_posts, name='group-posts'),
    path('', views.index, name='index')
]