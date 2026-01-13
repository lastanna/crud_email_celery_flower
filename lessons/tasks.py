# app/tasks.py
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Lesson

# Настраиваем логгер, чтобы видеть прогресс в консоли воркера
logger = logging.getLogger(__name__)

@shared_task(
    bind=True,                # Позволяет обращаться к экземпляру задачи (self)
    max_retries=5,            # Пытаться отправить 5 раз в случае сбоя
    default_retry_delay=300   # Пауза между попытками — 5 минут
)
def send_lesson_email_task(self, lesson_id):
    """
    Задача по отправке email уведомления о новом уроке.
    """
    try:
        # 1. Получаем объект из базы данных
        lesson = Lesson.objects.get(pk=lesson_id)

        logger.info(f"Начало отправки email для урока ID: {lesson_id}")

        # 2. Формируем письмо
        subject = f"Опубликован новый урок: {lesson.title}"
        message = f"Здравствуйте!\n\nУрок '{lesson.title}' уже доступен на платформе."

        # 3. Отправка через Django SMTP
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['students@example.com'],  # Здесь может быть список студентов
            fail_silently=False,  # Выбрасывать ошибку, если не удалось отправить
        )

        return f"Email для урока {lesson_id} успешно отправлен."

    except Lesson.DoesNotExist:
        # Если урок удалили быстрее, чем воркер до него добрался
        logger.error(f"Ошибка: Урок с ID {lesson_id} не найден в базе.")
        return "Lesson not found"

    except Exception as exc:
        # Если упал почтовый сервер или нет интернета — пробуем еще раз позже
        logger.warning(f"Ошибка при отправке: {exc}. Перезапуск через 5 минут...")
        raise self.retry(exc=exc)

