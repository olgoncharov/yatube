from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404

from .models import Follow


User = get_user_model()


def get_user_profile(username):
    """
    Возвращает объект пользователя с дополнительными полями:
        count_of_posts: integer, количество постов пользователя
        count_of_following: integer, количество подписчиков пользователя
        count_of_followers: integer, количество подписок пользователя
    """
    return get_object_or_404(
        User.objects.annotate(
            count_of_posts=Count('posts', distinct=True),
            count_of_following=Count('following', distinct=True),
            count_of_follower=Count('follower', distinct=True)
        ),
        username=username)


def check_following(user, author):
    """Функция проверяет, подписан ли пользователь на автора."""
    if user.is_authenticated:
        return Follow.objects.filter(user=user, author=author).exists()
    return False