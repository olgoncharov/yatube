from django.db import models
from django.contrib.auth import get_user_model


SEX_CHOICES = [
    ('M', 'Мужской'),
    ('F', 'Женский'),
]


User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    foto = models.ImageField(upload_to='users/', blank=True, null=True, verbose_name='Аватар')
    birthday = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    sex = models.CharField(blank=True, null=True, max_length=1, choices=SEX_CHOICES, verbose_name='Пол')
