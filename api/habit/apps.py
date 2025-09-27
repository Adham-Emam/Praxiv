from django.apps import AppConfig


class HabitConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "habit"

    def ready(self):
        import habit.signals

        return super().ready()
