from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView

from .forms import PostForm, CommentForm
from .models import Post, Group

User = get_user_model()


def index(request):
    """Главная страница сойта."""
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


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
    """Контроллер удаления поста."""
    model = Post
    pk_url_kwarg = 'post_id'
    http_method_names = ['post',]

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.author:
            return redirect('post', **kwargs)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profile', args=[self.kwargs['username']])


class GroupView(TemplateView):
    """Страница сообщества с постами."""
    template_name = 'group.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = get_object_or_404(Group, slug=kwargs['slug'])
        paginator = Paginator(group.posts.all().order_by('-pub_date'), 10)
        page_number = kwargs.get('page')
        page = paginator.get_page(page_number)
        context['group'] = group
        context['page'] = page
        context['paginator'] = paginator

        return context


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
    comments = post.comments.order_by('created').all()
    new_comment_form = CommentForm()

    return render(request, 'post.html', {
        'author': author,
        'post': post,
        'comments': comments,
        'new_comment_form': new_comment_form,
    })


class AddComment(CreateView, LoginRequiredMixin):
    http_method_names = ['post']
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post', kwargs=self.kwargs)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


def get_user_profile(username):
    return get_object_or_404(
        User.objects.annotate(count_of_posts=Count('posts')),
        username=username)