
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('edit/<username>', views.edit_profile, name='edit_profile'),
]