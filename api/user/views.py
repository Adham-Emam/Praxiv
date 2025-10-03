import secrets
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import CustomUser, UserScore, Plan
from .serializers import (
    UserSerializer,
    UserScoreSerializer,
    OpaqueTokenObtainPairSerializer,
    PlanSerializer,
)


# User Views
class OpaqueTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT tokens with opaque refresh tokens."""

    serializer_class = OpaqueTokenObtainPairSerializer


class OpaqueRefreshView(TokenRefreshView):
    """Refresh the Opaque token with new one and handle the hashing"""

    def post(self, request, *args, **kwargs):
        opaque_refresh = request.data.get("refresh")
        if not opaque_refresh:
            return Response(
                {"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        real_refresh = cache.get(opaque_refresh)
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
        cache.delete(opaque_refresh)
        new_opaque_refresh = secrets.token_urlsafe(32)
        cache.set(
            new_opaque_refresh,
            str(refresh),
            timeout=int(refresh.lifetime.total_seconds()),
        )

        #  Generate opaque access token
        new_opaque_access = secrets.token_urlsafe(32)
        cache.set(
            new_opaque_access,
            str(access),
            timeout=int(access.lifetime.total_seconds()),
        )

        return Response({"access": new_opaque_access, "refresh": new_opaque_refresh})


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


class GlobalLeaderboardView(generics.ListAPIView):
    """List users ranked globally by score."""

    queryset = UserScore.objects.all().order_by("-score")
    serializer_class = UserScoreSerializer
    permission_classes = [permissions.AllowAny]


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
