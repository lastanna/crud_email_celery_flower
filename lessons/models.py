from django.db import models
from django.conf import settings

class Lesson(models.Model):
    title = models.CharField(max_length=100, verbose_name='Наименование урока')
    content = models.TextField(verbose_name='Теория')
    task = models.TextField(verbose_name='Задание')
    # ForeignKey на модель пользователя
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Ссылка на текущую модель пользователя
        on_delete=models.CASCADE,  # При удалении пользователя удалятся его уроки
        related_name='lessons',  # Позволяет получить уроки через user.lessons.all()
        verbose_name="Автор")
    # события, которые будут отслеживаться
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

