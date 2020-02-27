from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.cache.backends import locmem


User = get_user_model()


class TestPosts(TestCase):
    """Набор тестов для проверки работы с постами."""

    def setUp(self):
        self.client = Client()

        # пользователь, от имени которого будут создаваться и редактироваться посты
        self.author = User.objects.create(
            username='alesha_popovich',
            first_name='Алёша',
            last_name='Попович',
            email='alex@popov.ru'
        )
        self.author.set_password('bogatyr')
        self.author.save()

        # пользователь, от имени которого будет тестироваться редактирование чужих постов
        self.not_author = User.objects.create(
            username='tugarin',
            first_name='Тугарин',
            last_name='Змей',
            email='tugarin@snake.ru'
        )

        # текст поста при создании
        self.post_text = 'А и сильные, могучие богатыри на славной Руси. Не скакать врагам по нашей земле,' \
                         'не топтать их коням землю Русскую, не затмить им солнце наше красное.'

        # текст поста после редактирования
        self.post_text_update = 'Век стоит Русь - не шатается. И века простоит - не шелохнётся!'

        # сообщество, к которому будет принадлежать пост
        self.group = Group.objects.create(
            title='Русские богатыри',
            slug='russian_heroes'
        )

        # графический файл
        data = BytesIO()
        Image.new('RGB', (100, 100)).save(data, 'PNG')
        data.seek(0)
        self.image_file = SimpleUploadedFile('image.png', data.getvalue())

        # неграфический файл
        self.non_image_file = SimpleUploadedFile('non_image.txt', b'some text')

    def testCreation(self):
        """Тестирует поведение при создании нового поста."""
        new_post_url = reverse('new_post')
        Post.objects.all().delete()

        self.client.force_login(self.author)

        # авторизованный пользователь имеет возможность создать новый пост
        response = self.client.get(new_post_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(new_post_url, {
            'text': self.post_text,
            'group': self.group.pk
        })

        # проверяем, что пост появился в базе данных
        posts = Post.objects.filter(author=self.author, text=self.post_text, group=self.group)
        self.assertEqual(posts.count(), 1)

        post_url = reverse('post', args=[self.author.username, posts[0].pk])

        # после создания поста мы перенаправлены на главную страницу
        self.assertRedirects(response, reverse('index'))

        # после создания пост появляется на главной странице сайта, на странице сообщества и на странице профиля
        cache.clear()
        url_list = [
            reverse('index'),
            reverse('profile', args=[self.author.username]),
            reverse('group-posts', args=[self.group.slug]),
        ]
        for url in url_list:
            response = self.client.get(url)
            self.assertIn('page', response.context)
            self.assertEqual(len(response.context['page']), 1)
            self.assertEqual(response.context['page'][0], posts[0])
            self.assertContains(response, self.post_text)

        # убедимся, что и на странице просмотра поста он содержится
        response = self.client.get(reverse('post', args=[self.author.username, posts[0].pk]))
        self.assertIn('post', response.context)
        self.assertEqual(response.context['post'], posts[0])
        self.assertContains(response, self.post_text)

        self.client.logout()

        # невторизованный пользователь при попытке зайти на страницу создания поста перенаправляется
        # на страницу авторизации
        response = self.client.get(new_post_url)
        expected_url = f'{reverse("login")}?next={new_post_url}'
        self.assertRedirects(response, expected_url)

        response = self.client.post(new_post_url, {
            'text': self.post_text,
            'group': self.group.pk
        })
        self.assertRedirects(response, expected_url)

    def testEdit(self):
        """Тестирует поведение при редактировании существующего поста."""
        test_post, created = Post.objects.get_or_create(author=self.author, text=self.post_text, group=self.group)
        post_edit_url = reverse('post_edit', args=[self.author.username, test_post.pk])
        post_view_url = reverse('post', args=[self.author.username, test_post.pk])

        self.client.force_login(self.author)

        # авторизованный пользователь может отредактировать свой пост
        # изменим текст и очистим поле сообщество
        response = self.client.post(post_edit_url, {
            'text': self.post_text_update,
            'group': '',
            'button': 'Update',
        })

        # после чего он будет перенаправлен на страницу просмотра поста
        self.assertRedirects(response, post_view_url)

        # проверим, что поля поста изменились
        test_post.refresh_from_db()
        self.assertEqual(test_post.text, self.post_text_update)
        self.assertIsNone(test_post.group)

        # текст поста изменился на главной странице и странице профиля
        cache.clear()
        url_list = [
            reverse('index'),
            reverse('profile', args=[self.author.username]),
        ]
        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, self.post_text_update)

        # а со страницы сообщества пост исчез
        response = self.client.get(reverse('group-posts', args=[self.group.slug]))
        self.assertEqual(len(response.context['page']), 0)
        self.assertNotContains(response, self.post_text_update)

        self.client.logout()

        # неавторизованный пользователь при попытке редактирования поста перенаправляется на страницу авторизации
        response = self.client.get(post_edit_url)
        expected_url = f'{reverse("login")}?next={post_edit_url}'
        self.assertRedirects(response, expected_url)

        self.client.force_login(self.not_author)

        # пользователь не может редактировать чужие посты - он перенаправляется на страницу просмотра поста
        response = self.client.get(post_edit_url)
        self.assertRedirects(response, post_view_url)

    def testError404(self):
        """Тестирует поведение при обращении к странице несуществующего поста."""
        Post.objects.all().delete()

        response = self.client.get(reverse('post', args=[self.author.username, 1]))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')

    def testImages(self):
        """Тестирует работу с иллюстрациями к постам."""
        Post.objects.all().delete()
        self.client.force_login(self.author)

        response = self.client.post(reverse('new_post'), {
            'text': self.post_text,
            'group': self.group.pk,
            'image': self.image_file,
        })

        # убеждаемся, что пост появился в базе данных
        self.assertEqual(Post.objects.count(), 1)

        test_post = Post.objects.get()

        # Все страницы, на которых содержится пост должны иметь тег <img>
        cache.clear()
        url_list = [
            reverse('index'),
            reverse('profile', args=[self.author.username]),
            reverse('post', args=[self.author.username, test_post.pk]),
            reverse('group-posts', args=[self.group.slug]),
        ]
        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, '<img')

        # пробуем создать пост с неграфическим файлом
        response = self.client.post(reverse('new_post'), {
            'text': self.post_text,
            'group': self.group.pk,
            'image': self.non_image_file,
        })

        self.assertFormError(response, 'form', 'image', 'Загрузите правильное изображение. Файл, который вы загрузили, '
                                                        'поврежден или не является изображением.')


class TestCache(TestCase):
    """Набор тестов для проверки работы кэша."""

    def setUp(self):
        self.client = Client()
        Post.objects.all().delete()

        self.author, created = User.objects.get_or_create(
            username='alesha_popovich',
            first_name='Алёша',
            last_name='Попович',
            email='alex@popov.ru'
        )

        self.old_post = Post.objects.create(author=self.author, text='old post')
        self.new_post_text = 'another one post'

        self.index_url = reverse('index')

    def testIndex(self):
        """Тестирует кэширование главной страницы."""
        response = self.client.get(self.index_url)

        # сейчас на главной странице один пост
        # создаем еще один пост и снова запрашиваем главную страницу
        new_post = Post.objects.create(author=self.author, text=self.new_post_text)
        response = self.client.get(self.index_url)

        # на главной странице пост еще не появился, т.к. кэш возвращает старую версию страницы
        self.assertNotContains(response, self.new_post_text)

        # очищаем кэш и опять запрашиваем главную страницу
        cache.clear()
        response = self.client.get(self.index_url)

        # теперь новый пост есть на странице
        self.assertContains(response, self.new_post_text)
