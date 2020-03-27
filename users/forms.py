from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms
from yatube.widgets import ImageWidget
from .models import UserProfile


User = get_user_model()


class NewUserForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ExistingUserForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('foto', 'birthday', 'sex')
        widgets = {
            'birthday': forms.SelectDateWidget,
            'foto': ImageWidget(width=200, height=200, role='avatar'),
        }
