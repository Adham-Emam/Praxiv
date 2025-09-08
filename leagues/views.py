from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import League, LeagueParticipant
from .serializers import LeaguesSerializer, LeagueParticipantSerializer
from core.permissions import IsOwner


class LeagueListView(generics.ListAPIView):
    """
    List all leagues.
    - If permission_classes = AllowAny → anyone can view all leagues.
    - Change to IsAuthenticated and filter queryset if you want
      users to see only their own leagues.
    """

    queryset = League.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = [permissions.AllowAny]


class LeagueCreateView(generics.CreateAPIView):
    """
    Create a new league.
    - Requires authentication.
    - Automatically assigns the logged-in user as 'created_by'.
    """

    queryset = League.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.plan and user.plan.name.lower() == "free":
            raise PermissionDenied(
                "Free plan users cannot create leagues. Upgrade your plan."
            )
        serializer.save(created_by=user)


class LeagueDetailsView(generics.RetrieveAPIView):
    """Retrieve details of a single league."""

    queryset = League.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = [permissions.AllowAny]


class LeagueRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a league.
    - Requires authentication.
    - Only the league owner can update or delete.
    """

    serializer_class = LeaguesSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return League.objects.filter(created_by=self.request.user)


class LeagueEnterView(generics.RetrieveUpdateAPIView):
    serializer_class = LeaguesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(League, pk=pk)

    def perform_update(self, serializer):
        user = self.request.user
        league = self.get_object()

        if league.participants.filter(id=user.id).exists():
            raise ValidationError("You have already joined this league.")

        league.participants.add(user)

        serializer.save()


class LeagueLeaderboardView(generics.ListAPIView):
    """List users ranked in a specific league."""

    serializer_class = LeagueParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        league_id = self.kwargs["league_id"]
        return LeagueParticipant.objects.filter(league_id=league_id).order_by("-score")
