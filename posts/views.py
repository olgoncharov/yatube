from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Post, Group
from .forms import PostForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    """Главная страница сойта."""
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """Страница сообщества с постами."""
    group = get_object_or_404(Group, slug=slug)
    paginator = Paginator(group.posts.all().order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {
        'group': group,
        'page': page,
        'paginator': paginator,
    })


@login_required
def new_post(request):
    """Страница создания нового поста."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post.objects.create(author=request.user, **form.cleaned_data)
            return redirect('index')
        return render(request, 'post_edit.html', {'form': form})

    form = PostForm()
    return render(request, 'post_edit.html', {'form': form})


def profile(request, username):
    """Страница профиля пользователя."""
    author = get_user_profile(username)
    paginator = Paginator(author.posts.all(), 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'paginator': paginator,
    })


def post_view(request, username, post_id):
    """Страница просмотра поста."""
    author = get_user_profile(username)
    post = get_object_or_404(Post, pk=post_id)

    return render(request, 'post.html', {
        'author': author,
        'post': post,
    })


@login_required
def post_edit(request, username, post_id):
    """Страница редактирования поста."""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        # если пользователь пытается редактировать чужой пост - перенаправляем его на страницу просмотра поста
        return redirect('post', username=username, post_id=post_id)

    if request.method == 'POST':
        if 'button' in request.POST and request.POST['button'] == 'Delete':
            # удаляем пост и перенаправляем на страницу профиля
            post.delete()
            return redirect('profile', username=username)

        form = PostForm(request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            # сохраняем пост и перенаправляем на страницу просмотра поста
            form.save()
            return redirect('post', username=username, post_id=post_id)

        # оставляем пользователя на странице, если он ввел невалидные данные и пытается сохранить изменения
        return render(request, 'post_edit.html', {'form': form})

    return render(request, 'post_edit.html', {
        'post': post,
        'form': PostForm(instance=post)
    })


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


def get_user_profile(username):
    return get_object_or_404(
        User.objects.annotate(count_of_posts=Count('posts')),
        username=username)