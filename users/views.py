from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import NewUserForm, ExistingUserForm, UserProfileForm
from .models import User


def sign_up(request):
    """Страница регистрации нового пользователя."""
    if request.method == 'POST':
        user_form = NewUserForm(request.POST)
        profile_form = UserProfileForm(request.POST, files=request.FILES or None)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user_profile = profile_form.save(commit=False)
            user_profile.user = user
            user_profile.save()

            return redirect(reverse('login'))

        context = {'forms': [user_form, profile_form]}
        return render(request, 'user_edit.html', context)

    context = {'forms': [NewUserForm(), UserProfileForm()]}
    return render(request, 'user_edit.html', context)


def edit_profile(request, username):
    """Страница редактирования профиля."""
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        user_form = ExistingUserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.profile, files=request.FILES or None)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', username)

        context = {'forms': [user_form, profile_form]}
        return render(request, 'user_edit.html', context)

    if request.user != user:
        return redirect('profile', username)

    user_form = ExistingUserForm(instance=user)
    try:
        profile_form = UserProfileForm(instance=user.profile)
    except User.profile.RelatedObjectDoesNotExist:
        profile_form = UserProfileForm()

    context = {'forms': [user_form, profile_form]}
    return render(request, 'user_edit.html', context)
