from django.db import transaction
from lessons.tasks import send_lesson_email_task

def create_lesson_with_notification(form):
    # Атомарная операция: создает урок и ставит задачу на отправку email
    with transaction.atomic():
        # 1. Создаем запись в базе, сохраняем данные из формы в модель
        form.save()
        # 2. Планируем задачу Celery
        # on_commit гарантирует, что задача уйдет в redis только после того, как SQL запрос
        # реально завершится (COMMIT).
        transaction.on_commit(
            lambda: send_lesson_email_task(form.instance.id)
        )
