from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    return render(request, 'index.html', {'posts': latest})

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
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})