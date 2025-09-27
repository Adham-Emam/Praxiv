from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer
from user.serializers import UserSerializer


class HabitListView(generics.ListAPIView):
    """List all habits, or create a new habit."""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]


class HabitDetailView(generics.RetrieveAPIView):
    """retrieve, update, or delete a habit instance."""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Habit, pk=self.kwargs.get("pk"))


class UsersHabitsView(generics.UpdateAPIView):
    """Update user's Habits with plan limits."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        habit_ids = request.data.get("habits", [])

        if not isinstance(habit_ids, list):
            raise ValidationError({"habits": "Must be a list of habit IDs."})

        plan = user.plan
        if plan and len(habit_ids) > plan.max_habits:
            raise ValidationError(
                {
                    "habits": f"You can only have {plan.max_habits} habits with your current plan."
                }
            )

        habits = Habit.objects.filter(id__in=habit_ids)

        user.habits.set(habits)
        user.save()

        return Response(UserSerializer(user).data)


class HabitLogCreateView(generics.CreateAPIView):
    """Log completion of a habit for the current user."""

    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        habit = get_object_or_404(Habit, pk=self.kwargs.get("habit_id"))
        serializer.save(user=self.request.user, habit=habit)


class UserHabitLogListView(generics.ListAPIView):
    """List all logs of the authenticated user."""

    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HabitLog.objects.filter(user=self.request.user).order_by("-date")


class UserHabitLogUpdateView(generics.UpdateAPIView):
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(HabitLog, pk=self.kwargs.get("log_id"))
