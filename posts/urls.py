from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.PostCreate.as_view(), name='new_post'),
    path('group/<slug:slug>/', views.GroupView.as_view(), name='group-posts'),
    path('', views.index, name='index'),
    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:post_id>/', views.post_view, name='post'),
    path('<username>/<int:post_id>/edit/', views.PostUpdate.as_view(), name='post_edit'),
    path('<username>/<int:post_id>/delete/', views.PostDelete.as_view(), name='post_delete'),
    path('<username>/<int:post_id>/comment/', views.AddComment.as_view(), name='add_comment')
]