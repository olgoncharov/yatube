from django import forms
from .models import Post, Comment
from yatube.widgets import ImageWidget
from django.conf import settings
import os


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        widgets = {
            'text': forms.Textarea(),
            'image': ImageWidget(width=320, height=200),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(),
        }