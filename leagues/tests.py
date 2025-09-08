from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from habit.models import Habit
from .models import League, LeagueParticipant

User = get_user_model()


class LeagueViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.user = User.objects.create_user(
            email="user@example.com", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="pass1234"
        )

        # Authenticate default user
        self.client.force_authenticate(user=self.user)

        # Habit required for League
        self.habit = Habit.objects.create(name="Daily Pushups")

        # Valid league dates
        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=7)

        # League created by user
        self.league = League.objects.create(
            created_by=self.user,
            title="Champions League",
            description="Test league",
            habit=self.habit,
            start_date=self.start_date,
            end_date=self.end_date,
            rules="Do your best",
            rewards="Gold medal",
        )

    # ---------------- LeagueListView ----------------
    def test_list_leagues(self):
        url = reverse("league-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # ---------------- LeagueCreateView ----------------
    def test_create_league_authenticated(self):
        url = reverse("league-create")
        data = {
            "title": "New League",
            "description": "desc",
            "habit": self.habit.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "rules": "Some rules",
            "rewards": "Some rewards",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["created_by"], self.user.id)

    def test_create_league_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("league-create")
        data = {
            "title": "Unauthorized League",
            "habit": self.habit.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------- LeagueDetailsView ----------------
    def test_retrieve_league_details(self):
        url = reverse("league-detail", args=[self.league.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.league.id)

    # ---------------- LeagueRetrieveUpdateDestroyView ----------------
    def test_update_league_by_owner(self):
        url = reverse("league-edit", args=[self.league.id])
        response = self.client.patch(url, {"title": "Updated Title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")

    def test_update_league_by_non_owner_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("league-edit", args=[self.league.id])
        response = self.client.patch(url, {"title": "Hack Attempt"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # non-owner won't see league due to get_queryset()

    def test_delete_league_by_owner(self):
        url = reverse("league-edit", args=[self.league.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ---------------- LeagueEnterView ----------------
    def test_user_can_join_league(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("league-enter", args=[self.league.id])
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.league.participants.filter(id=self.other_user.id).exists())

    def test_user_cannot_join_twice(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("league-enter", args=[self.league.id])
        self.client.patch(url, {}, format="json")  # first join
        response = self.client.patch(url, {}, format="json")  # second join
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------- LeagueLeaderboardView ----------------
    def test_league_leaderboard(self):
        LeagueParticipant.objects.create(league=self.league, user=self.user, score=50)
        LeagueParticipant.objects.create(
            league=self.league, user=self.other_user, score=70
        )

        url = reverse("league_leaderboard", args=[self.league.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Highest score should be first
        self.assertEqual(response.data[0]["user"], self.other_user.id)
