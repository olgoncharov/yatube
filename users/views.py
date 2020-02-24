from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.mail import send_mail


from .forms import CreationForm


class SignUp(CreateView):
    """Страница регистрации нового пользователя."""
    form_class = CreationForm
    success_url = '/auth/login/'
    template_name = 'signup.html'

    def form_valid(self, form):
        send_mail(
            'Подтверждение регистрации',
            f'Дорогой Вы наш {form.cleaned_data["username"]}, поздравляем Вас с регистрацией',
            'yatube-noreply@yatube.ru',
            [form.cleaned_data['email']],
            fail_silently=False
        )
        return super().form_valid(form)

