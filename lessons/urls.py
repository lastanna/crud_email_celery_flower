from django.urls import path
from lessons.views import LessonList, LessonCreateView, LessonUpdateView

app_name = "lessons"

urlpatterns = [
    path('', LessonList.as_view(), name='list' ),
    path('create', LessonCreateView.as_view(), name='create'),
    path('<int:pk>/update', LessonUpdateView.as_view(), name='update'),
]