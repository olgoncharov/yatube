from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Наименование')
    slug = models.SlugField(unique=True, verbose_name='Адрес', help_text='Уникальный адрес группы, часть URL')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='groups', blank=True, null=True, verbose_name='Картинка')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(max_length=2000, verbose_name='Текст')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Сообщество'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name='Иллюстрация')

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Публикация')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    text = models.TextField(max_length=200, verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'@{self.author.username} ({self.created:%Y-%m-%d %H:%M}: {self.text}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        unique_together = ('user', 'author')
