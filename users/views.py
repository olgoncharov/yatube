from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.core.mail import send_mail


from .forms import UserForm, UserProfileForm


def sign_up(request):
    """Страница регистрации нового пользователя."""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, files=request.FILES or None)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user_profile = profile_form.save(commit=False)
            user_profile.user = user
            user_profile.save()

            return redirect(reverse('login'))

        context = {'forms': [user_form, profile_form]}
        return render(request, 'signup.html', context)

    context = {'forms': [UserForm(), UserProfileForm()]}
    return render(request, 'signup.html', context)