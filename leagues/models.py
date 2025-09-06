from django.db import models
from user.models import CustomUser, Habit


class League(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="leagues",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="league_images/", blank=True, null=True)
    participants = models.ManyToManyField(
        CustomUser, related_name="joined_leagues", blank=True
    )
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="leagues")
    start_date = models.DateField()
    end_date = models.DateField()
    rules = models.TextField(blank=True, null=True)
    rewards = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} made by {self.created_by}"
