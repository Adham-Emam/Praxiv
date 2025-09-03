from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import CustomUser, Habit, Plan
from .serializers import UserSerializer, HabitSerializer, PlanSerializer


# User Views
class UserCreateView(generics.CreateAPIView):
    """Create a new user."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserDetailView(generics.RetrieveAPIView):
    """Retrieve details of a specific user by ID."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return get_object_or_404(CustomUser, pk=self.kwargs.get("pk"))


class CurrentUserView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete the currently authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Habits Views
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


class UsersHabitsView(generics.ListAPIView):
    """List all habits for the current user, or create/link a new one with plan limits."""

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.habits.all()

    def perform_create(self, serializer):
        user = self.request.user
        plan = user.plan

        if plan and user.plan.name == "Free":
            if user.habits.count() >= plan.max_habits:
                raise PermissionError("Habit limit reached for your current plan.")
        serializer.save()
        user.habits.add(serializer.instance)


# Plans Views
class PlanListView(generics.ListAPIView):
    """List all plans. Creation of plans is handled via admin interface."""

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class PlanDetailView(generics.RetrieveAPIView):
    """Retrieve details of a specific plan."""

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return get_object_or_404(Plan, pk=self.kwargs.get("pk"))
