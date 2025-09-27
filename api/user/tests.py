from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import UserScore, Plan, UserProgress

User = get_user_model()


class UserViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Ensure base plans exist
        self.free_plan, _ = Plan.objects.get_or_create(
            name="Free",
            defaults={
                "price_monthly": 0,
                "price_annually": 0,
                "features": "Basic access",
                "max_habits": 3,
                "max_leagues": 1,
            },
        )
        self.plus_plan, _ = Plan.objects.get_or_create(
            name="Plus",
            defaults={
                "price_monthly": 9.99,
                "price_annually": 99.99,
                "features": "More habits and leagues",
                "max_habits": 10,
                "max_leagues": 3,
            },
        )
        self.premium_plan, _ = Plan.objects.get_or_create(
            name="Premium",
            defaults={
                "price_monthly": 19.99,
                "price_annually": 199.99,
                "features": "Unlimited access",
                "max_habits": 0,
                "max_leagues": 0,
            },
        )

        # Users
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass1234",
            first_name="Test",
            last_name="User",
            plan=self.plus_plan,  # explicitly test non-default plan
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="pass1234",
            first_name="Other",
            last_name="User",
        )  # should default to Free plan

        # Scores
        UserScore.objects.create(user=self.user, score=50)
        UserScore.objects.create(user=self.other_user, score=80)

        # Clear cache before running tests
        cache.clear()

    # ---------------- UserCreateView ----------------
    def test_create_user_defaults(self):
        url = reverse("user-create")
        data = {
            "email": "new@example.com",
            "password": "strongpassword",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_user = User.objects.get(email="new@example.com")
        self.assertEqual(new_user.plan.name, "Free")  # default plan
        self.assertTrue(
            UserProgress.objects.filter(user=new_user).exists()
        )  # progress created

    # ---------------- UserDetailView ----------------
    def test_retrieve_user_detail(self):
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["plan"]["name"], self.user.plan.name)

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
        refresh = RefreshToken.for_user(self.user)

        opaque = "opaque123"
        cache.set(opaque, str(refresh), timeout=int(refresh.lifetime.total_seconds()))

        url = reverse("token_refresh")
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
        url = reverse("global-leaderboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data[0]["user"], self.other_user.id
        )  # Highest score first

    # ---------------- Plans ----------------
    def test_list_plans(self):
        url = reverse("plan-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)  # Free, Plus, Premium

    def test_retrieve_plan_detail(self):
        url = reverse("plan-detail", args=[self.plus_plan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.plus_plan.id)
