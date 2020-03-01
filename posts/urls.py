from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('follow/', views.FollowView.as_view(), name='follow_index'),
    path('new/', views.PostCreate.as_view(), name='new_post'),
    path('group/<slug:slug>/', views.GroupView.as_view(), name='group-posts'),
    path('<username>/', views.ProfileView.as_view(), name='profile'),
    path('<username>/follow', views.profile_follow, name='profile_follow'),
    path('<username>/unfollow', views.profile_unfollow, name='profile_unfollow'),
    path('<username>/<int:post_id>/', views.PostView.as_view(), name='post'),
    path('<username>/<int:post_id>/edit/', views.PostUpdate.as_view(), name='post_edit'),
    path('<username>/<int:post_id>/delete/', views.PostDelete.as_view(), name='post_delete'),
    path('<username>/<int:post_id>/comment/', views.CommentCreate.as_view(), name='add_comment'),
]