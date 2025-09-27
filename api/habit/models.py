from django.db import models
from user.models import CustomUser
from django.utils import timezone


class Habit(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="habit_logs"
    )
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("habit", "user", "date")

    def __str__(self):
        return f"{self.user} - {self.habit} on {self.date} ({'done' if self.completed else 'missed'})"
