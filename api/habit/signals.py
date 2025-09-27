from django.db.models.signals import pre_save
from django.dispatch import receiver

from user.models import UserProgress
from .models import HabitLog


@receiver(pre_save, sender=HabitLog)
def add_xp_on_completion(sender, instance, **kwargs):
    if instance.pk:
        old = HabitLog.objects.get(pk=instance.pk)
        if not old.completed and instance.completed:
            UserProgress.add_xp(instance.user.progress, 10)
