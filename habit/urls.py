from django.urls import path
from . import views


urlpatterns = [
    # Habits endpoints
    path("me/", views.UsersHabitsView.as_view(), name="user-habits"),
    path("", views.HabitListView.as_view(), name="habit-list"),
    path("<int:pk>/", views.HabitDetailView.as_view(), name="habit-detail"),
    # Habit Logs endpoints
    path(
        "<int:habit_id>/logs/",
        views.HabitLogCreateView.as_view(),
        name="habit-log-create",
    ),
    path("me/logs/", views.UserHabitLogListView.as_view(), name="user-habit-logs"),
]
