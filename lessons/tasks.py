# app/tasks.py
import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Lesson

# Настраиваем логгер, чтобы видеть прогресс в консоли воркера
logger = logging.getLogger(__name__)

@shared_task(
    bind=True,                # Позволяет обращаться к экземпляру задачи (self)
    max_retries=5,            # Пытаться отправить 5 раз в случае сбоя
    default_retry_delay=300   # Пауза между попытками — 5 минут
)
def send_created_email(self, lesson_id):
    """
    Задача по отправке email уведомления о новом уроке.
    """
    try:
        # 1. Получаем объект из базы данных
        lesson = Lesson.objects.get(pk=lesson_id)

        logger.info(f"Начало отправки email для урока ID: {lesson_id}")

        # 2. Формируем письмо.

        subject = f"Опубликован новый урок: {lesson.title}"
        text_content = f"Здравствуйте!\n\nУрок '{lesson.title}' уже доступен на платформе."
        html_content = f"<p>Здравствуйте!</br></br>Урок <strong>'{lesson.title}'</strong> уже доступен на платформе.</p>"

        # 3. Отправка через Django SMTP
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['student@example.com']
        )
        # Добавляем HTML-версию
        msg.attach_alternative(html_content, "text/html")

        # Отправляем (файл .eml появится в папке EMAIL_FILE_PATH)
        msg.send()
        return f"Email для урока {lesson_id} успешно отправлен."

    except Lesson.DoesNotExist:
        # Если урок удалили быстрее, чем воркер до него добрался
        logger.error(f"Ошибка: Урок с ID {lesson_id} не найден в базе.")
        return "Lesson not found"

    except Exception as exc:
        # Если упал почтовый сервер или нет интернета — пробуем еще раз позже
        logger.warning(f"Ошибка при отправке: {exc}. Перезапуск через 5 минут...")
        raise self.retry(exc=exc)


@shared_task(
    bind=True,                # Позволяет обращаться к экземпляру задачи (self)
    max_retries=5,            # Пытаться отправить 5 раз в случае сбоя
    default_retry_delay=300   # Пауза между попытками — 5 минут
)
def send_updated_email(self, lesson_id):
    """
    Задача по отправке email уведомления о том, что урок завершен.
    """
    try:
        # 1. Получаем объект из базы данных
        lesson = Lesson.objects.get(pk=lesson_id)

        logger.info(f"Начало отправки email для урока ID: {lesson_id}")

        # 2. Формируем письмо.
        subject = f'Урок {lesson.title} завершен'
        text_content = f'Здравствуйте! Обращаем Ваше внимание на то, что урок {lesson.title} завершен.'
        html_content = f'<p>Здравствуйте! Обращаем Ваше внимание на то, что урок <strong>{lesson.title}</strong> завершен.</p>'

        # 3. Отправка через Django SMTP
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['student@example.com']
        )
        # Добавляем HTML-версию
        msg.attach_alternative(html_content, "text/html")

        # Отправляем (файл .eml появится в папке EMAIL_FILE_PATH)
        msg.send()
    except Lesson.DoesNotExist:
        # Если урок удалили быстрее, чем воркер до него добрался
        logger.error(f"Ошибка: Урок с ID {lesson_id} не найден в базе.")
        return "Lesson not found"

    except Exception as exc:
        # Если упал почтовый сервер или нет интернета — пробуем еще раз позже
        logger.warning(f"Ошибка при отправке: {exc}. Перезапуск через 5 минут...")
        raise self.retry(exc=exc)