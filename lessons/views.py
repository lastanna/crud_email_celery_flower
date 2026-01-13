from django.utils import timezone
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from lessons.models import Lesson
from lessons.services import create_lesson_with_notification

class LessonList(ListView):
    model = Lesson
    template_name = "lessons/list.html"   # template path
    context_object_name = "object_list"

class LessonCreateView(CreateView):
    model = Lesson
    fields = ['title', 'content', 'task']
    # Перенаправляет после успешного создания/редактирования
    success_url = reverse_lazy('lessons:list')
    template_name = 'lessons/create_form.html'

    def form_valid(self, form):
        """
        Этот метод вызывается, когда форма успешно прошла валидацию.
        """
        # Проверяем кликнута ли кнопочка "Завершить урок"
        if 'complete_lesson' in self.request.POST:
            # Инициализируем поле формы текущим временем
            form.instance.completed_at = timezone.now().date()
        form.instance.author = self.request.user
        # Вместо стандартного form.save() вызываем наш сервис
        self.object = create_lesson_with_notification(form)
        # Сохраняем форму, работает для обеих кнопочек и для "Сохранить" и для "Завершить урок"
        return super().form_valid(form)

class LessonUpdateView(UpdateView):
    model = Lesson
    fields = ['title', 'content', 'task']
    # Перенаправляет после успешного создания/редактирования
    success_url = reverse_lazy('lessons:list')
    template_name = 'lessons/edit_form.html'

    def form_valid(self, form):
        # Проверяем кликнута ли кнопочка "Завершить урок"
        if 'complete_lesson' in self.request.POST:
            # Инициализируем поле формы текущим временем
            form.instance.completed_at = timezone.now().date()
            form.instance.author = self.request.user
        # Сохраняем форму, работает для обеих кнопочек и для "Сохранить" и для "Завершить урок"
        return super().form_valid(form)