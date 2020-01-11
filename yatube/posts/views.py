from django.shortcuts import render
from .models import Post
from django.http import HttpResponse

def index(request):
    latest = Post.objects.order_by('-pub_date')[:10]
    output = []
    for item in latest:
        output.append(item.text)

    return HttpResponse('\n'.join(output))