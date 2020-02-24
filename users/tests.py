from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail


User = get_user_model()


class TestSignUp(TestCase):
    """Набор тестов для проверки регистрации нового пользователя."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')

        self.user_info = {
            'username': 'tugarin',
            'first_name': 'Тугарин',
            'last_name': 'Змей',
            'email': 'tugarin@snake.ru',
        }

    def testSuccessfullSignUp(self):
        """Тестирует поведение при регистрации нового пользователя в том случае, когда все данные введены корректно."""
        response = self.client.post(self.url, {
            **self.user_info,
            'password1': 'A123456bc',
            'password2': 'A123456bc',
        })

        # операция прошла успешно и мы попали на страницу авторизации
        self.assertRedirects(response, reverse('login'))

        # в базе данных создался пользователь
        users = User.objects.filter(**self.user_info)
        self.assertEqual(users.count(), 1)

        # в исходящих письмах появилось письмо с подтверждением регистрации
        self.assertEqual(len(mail.outbox), 1)

        # тема письма и тело соответствуют требуемому формату
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение регистрации')
        self.assertEqual(
            mail.outbox[0].body,
            f'Дорогой Вы наш {self.user_info["username"]}, поздравляем Вас с регистрацией')

        # стала доступна персональная страница пользователя
        response = self.client.get(reverse('profile', args=[self.user_info['username']]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, f'Профиль пользователя {users[0].get_full_name()}')

    def testFailedSignUp(self):
        """
        Тестирует поведение при регистрации нового пользователя в том случае,
        когда в форму вводятся некорректные данные.
        """

        # пробуем с незаполненным логином
        response = self.client.post(self.url, {
            **self.user_info,
            'username': '',
            'password1': 'A123456bc',
            'password2': 'A123456bc',
        })
        self.assertFormError(response, 'form', 'username', 'Обязательное поле.')

        # пробуем с незаполненным паролем
        response = self.client.post(self.url, {
            **self.user_info,
            'password1': '',
            'password2': '',
        })
        self.assertFormError(response, 'form', 'password2', 'Обязательное поле.')

        # пробуем с паролем менее 8 символов
        response = self.client.post(self.url, {
            **self.user_info,
            'password1': 'A1234bc',
            'password2': 'A1234bc',
        })
        self.assertFormError(response, 'form', 'password2',
                             'Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов.')

        # пробуем с паролем без букв
        response = self.client.post(self.url, {
            **self.user_info,
            'password1': '19428510',
            'password2': '19428510',
        })
        self.assertFormError(response, 'form', 'password2', 'Введённый пароль состоит только из цифр.')

        # пробуем несовпадающие пароль и подтверждение пароля
        response = self.client.post(self.url, {
            **self.user_info,
            'username': '',
            'password1': 'A123456bc',
            'password2': 'A123456cb',
        })
        self.assertFormError(response, 'form', 'password2', 'Два поля с паролями не совпадают.')

        # пробуем слишком распространенный пароль
        response = self.client.post(self.url, {
            **self.user_info,
            'password1': '12345678',
            'password2': '12345678',
        })
        self.assertFormError(response, 'form', 'password2', [
            'Введённый пароль слишком широко распространён.',
            'Введённый пароль состоит только из цифр.'])
