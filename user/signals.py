from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from .models import CustomUser, UserProgress, Plan


@receiver(post_save, sender=CustomUser)
def set_default_plan(sender, instance, created, **kwargs):
    if created and not instance.plan:
        free_plan = Plan.objects.get(name="Free")
        if free_plan:
            instance.plan = free_plan
            instance.save()


@receiver(post_save, sender=CustomUser)
def create_user_progress(sender, instance, created, **kwargs):
    if created:
        UserProgress.objects.create(user=instance)


@receiver(post_migrate)
def create_default_plan(sender, **kwargs):
    if sender.name == "user":
        plans = [
            {
                "name": "Free",
                "price_monthly": 0.00,
                "price_annually": 0.00,
                "features": "Basic tracking with limited features",
                "max_habits": 3,
                "max_leagues": 1,
            },
            {
                "name": "Plus",
                "price_monthly": 9.99,
                "price_annually": 99.99,
                "features": "More habits and leagues, better analytics",
                "max_habits": 10,
                "max_leagues": 3,
            },
            {
                "name": "Premium",
                "price_monthly": 19.99,
                "price_annually": 199.99,
                "features": "Unlimited habits, unlimited leagues, full analytics",
                "max_habits": 999,
                "max_leagues": 999,
            },
        ]

        for plan in plans:
            Plan.objects.get_or_create(**plan)
