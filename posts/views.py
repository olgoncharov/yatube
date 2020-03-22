from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow
from .utils import get_user_profile, check_following


User = get_user_model()


class IndexView(ListView):
    """Главная страница сайта."""
    paginate_by = 10
    template_name = 'index.html'

    def get_queryset(self):
        return Post.objects.select_related('author', 'group').order_by('-pub_date').all()


class FollowView(LoginRequiredMixin, ListView):
    """Страница постов авторов, на которых подписан пользователь."""
    paginate_by = 10
    template_name = 'follow.html'

    def get_queryset(self):
        return (
            Post.objects.select_related('author', 'group')
            .order_by('-pub_date')
            .filter(author__following__user=self.request.user)
        )


class GroupView(ListView):
    """Страница сообщества с постами."""
    template_name = 'group.html'
    paginate_by = 10

    def get_queryset(self):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return group.posts.select_related('author', 'group').order_by('-pub_date').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(Group, slug=self.kwargs['slug'])
        return context


class GroupListView(ListView):
    """Страница со списком сообществ."""
    model = Group
    template_name = 'group_list.html'
    paginate_by = 30


class PostCreate(LoginRequiredMixin, CreateView):
    """Страница создания нового поста."""
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    """Страница редактирования поста."""
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'post_edit.html'

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            # если пользователь пытается редактировать чужой пост - перенаправляем его на страницу просмотра поста
            return redirect('post', **kwargs)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post', kwargs=self.kwargs)


class PostDelete(LoginRequiredMixin, DeleteView):
    """Контроллер удаления поста. """
    model = Post
    pk_url_kwarg = 'post_id'
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.author:
            return redirect('post', **kwargs)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profile', args=[self.kwargs['username']])


class ProfileView(ListView):
    """Страница профиля пользователя."""
    template_name = 'profile.html'
    paginate_by = 5

    def get_queryset(self):
        author = get_user_profile(self.kwargs['username'])
        self.kwargs['author'] = author
        return author.posts.select_related('author', 'group').order_by('-pub_date').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['author'] = self.kwargs['author']
        context['following'] = check_following(self.request.user, context['author'])
        return context


class PostView(TemplateView):
    """Страница просмотра поста."""
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_user_profile(self.kwargs['username'])
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comments = post.comments.select_related('author', 'author__profile').order_by('created').all()
        new_comment_form = CommentForm()

        context['author'] = author
        context['following'] = context['following'] = check_following(self.request.user, context['author'])
        context['post'] = post
        context['comments'] = comments
        context['new_comment_form'] = new_comment_form

        return context


class CommentCreate(LoginRequiredMixin, CreateView):
    """Контроллер для создания комментария. """
    http_method_names = ['post']
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post', kwargs=self.kwargs)


@login_required
def profile_follow(request, username):
    """Контроллер для подписки на автора."""
    author = get_object_or_404(User, username=username)
    if author == request.user:
        # подписаться на самого себя нельзя
        return redirect('profile', username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        # подписаться несколько раз на одного пользователя нельзя
        return redirect('profile', username=username)

    follow = Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Контроллер для отписки от автора."""
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    """Страница ошибки при обращении к несуществующему адресу."""
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    """Страница, выводимая при возникновении ошибки на сервере."""
    return render(request, "misc/500.html", status=500)
