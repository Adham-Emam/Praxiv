from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import UserScore, Plan

User = get_user_model()


class UserViewsTests(APITestCase):
    def setUp(self):

        self.client = APIClient()

        # Test plan
        self.plan = Plan.objects.create(
            name="Free",
            price_monthly=0,
            price_annually=0,
            features="Basic features",
            max_habits=5,
            max_leagues=1,
        )

        # Users
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass1234",
            first_name="Test",
            last_name="User",
            plan=self.plan,
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="pass1234",
            first_name="Other",
            last_name="User",
        )

        # Scores
        UserScore.objects.create(user=self.user, score=50)
        UserScore.objects.create(user=self.other_user, score=80)

        # clear cache before running tests
        cache.clear()

    # ---------------- UserCreateView ----------------
    def test_create_user(self):
        url = reverse("user-create")
        data = {
            "email": "new@example.com",
            "password": "strongpassword",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    # ---------------- UserDetailView ----------------
    def test_retrieve_user_detail(self):
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)

    # ---------------- CurrentUserView ----------------
    def test_current_user_view_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("current-user")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_current_user_view_unauthenticated(self):
        url = reverse("current-user")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------- JWT Token Views ----------------
    def test_obtain_token_pair(self):
        url = reverse("token_obtain_pair")
        data = {"email": self.user.email, "password": "pass1234"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_with_opaque_token(self):
        # Create refresh
        refresh = RefreshToken.for_user(self.user)

        # Create opaque mapping
        opaque = "opaque123"
        cache.set(opaque, str(refresh), timeout=int(refresh.lifetime.total_seconds()))

        url = reverse("token_refresh")  # your OpaqueRefreshView
        response = self.client.post(url, {"refresh": opaque}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_with_invalid_opaque_token(self):
        url = reverse("token_refresh")
        response = self.client.post(url, {"refresh": "invalid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------- Leaderboard ----------------
    def test_global_leaderboard(self):
        url = reverse("global_-leaderboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Highest score first
        self.assertEqual(response.data[0]["user"], self.other_user.id)

    # ---------------- Plans ----------------
    def test_list_plans(self):
        url = reverse("plan-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_plan_detail(self):
        url = reverse("plan-detail", args=[self.plan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.plan.id)
