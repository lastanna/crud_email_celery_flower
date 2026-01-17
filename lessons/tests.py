from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from lessons.models import Lesson

User = get_user_model()
# Протестируем создание объектов
class LessonTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testworker', password='password123')
        self.lesson = Lesson.objects.create(title='Урок 1', content='Теория', task='Практика', author=self.user)

    # Проверим, что создан один урок, заполение полей, __str__ метод# Проверим, что создан один урок, заполение полей, __str__ метод
    def test_create_lesson(self):
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(str(self.lesson), self.lesson.title)
        self.assertEqual(self.lesson.author.username, 'testworker')
        self.assertIsNone(self.lesson.completed_at)
        self.assertIsNotNone(self.lesson.created_at)


from unittest.mock import patch
from django import forms
from lessons.models import Lesson
from lessons.services import create_lesson_with_notification


class LessonTransactionTest(TestCase):
    """Создаем тестовую форму для тестирования того, срабатывает ли
    отправка таска при on_commit"""

    @patch('lessons.services.send_created_email')
    def test_commit_triggers_task(self, mock_task):
        user = User.objects.create_user(username='testworker', password='password123')
        # Создаем форму для модели Lesson
        class TestForm(forms.ModelForm):
            class Meta:
                model = Lesson
                fields = '__all__'
        form = TestForm(data={'title': 'Test', 'content': 'Test', 'task': 'Practice exercises', 'author': user})
        # тестируем форму
        if not form.is_valid():
            print(f"Ошибки формы: {form.errors.as_json()}")

        self.assertTrue(form.is_valid())

        # Чтобы протестировать on_commit с реальной формой, созданной во views.py будем использовать captureOnCommitCallbacks
        # - встроенный контекстный менеджер для фиксации коммитов, поскольку в обычных TestCase транзакции всегда
        # откатываются (ROLLBACK), on_commit не сработает без специальных инструментов
        with self.captureOnCommitCallbacks(execute=True):
            create_lesson_with_notification(form)

        # on_commit выполняется сразу после выхода из atomic
        mock_task.assert_called_once()

