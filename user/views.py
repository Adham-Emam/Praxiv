import secrets
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import CustomUser, Habit, Plan
from .serializers import (
    UserSerializer,
    OpaqueTokenObtainPairSerializer,
    HabitSerializer,
    PlanSerializer,
)


# User Views
class OpaqueTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT tokens wim ==th opaque refresh tokens."""

    serializer_class = OpaqueTokenObtainPairSerializer


class OpaqueRefreshView(TokenRefreshView):
    """Refresh the Opaque token with new one and handle the hashing"""

    def post(self, request, *args, **kwargs):
        opaque = request.data.get("refresh")
        if not opaque:
            return Response(
                {"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        real_refresh = cache.get(opaque)
        if not real_refresh:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(real_refresh)
            access = refresh.access_token
        except Exception:
            return Response(
                {"detail": "Token invalid."}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Rotate: invalidate old opaque and issue a new one
        cache.delete(opaque)
        new_opaque = secrets.token_urlsafe(32)
        cache.set(
            new_opaque, str(refresh), timeout=int(refresh.lifetime.total_seconds())
        )

        return Response({"access": str(access), "refresh": new_opaque})


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
