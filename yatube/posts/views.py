from django.shortcuts import render
from .models import Post
from django.http import HttpResponse

def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    return render(request, 'index.html', {'posts': latest})