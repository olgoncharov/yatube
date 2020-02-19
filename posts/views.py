from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model


User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:12]
    return render(request, 'group.html', {'posts': posts, 'group': group})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post.objects.create(author=request.user, **form.cleaned_data)
            return redirect('post', username=request.user.username, post_id=post.pk)
        return render(request, 'post_edit.html', {'form': form})

    form = PostForm()
    return render(request, 'post_edit.html', {'form': form})


def profile(request, username):
    context = get_profile_statistics(username)
    context['paginator'] = Paginator(context['posts'], 5)
    page_number = request.GET.get('page')
    context['page'] = context['paginator'].get_page(page_number)

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    context = get_profile_statistics(username)
    context['post'] = get_object_or_404(Post, pk=post_id)

    return render(request, 'post.html', context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    if request.method == 'POST':
        if request.POST['button'] == 'Delete':
            post.delete()
            return redirect('profile', username=username)

        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)

        return render(request, 'post_edit.html', {'form': form})

    return render(request, 'post_edit.html', {'form': PostForm(instance=post)})


def get_profile_statistics(username):
    info = dict()
    info['owner'] = get_object_or_404(User, username=username)
    info['posts'] = Post.objects.order_by('-pub_date').filter(author=info['owner'])
    info['count_of_posts'] = info['posts'].count()

    return info
