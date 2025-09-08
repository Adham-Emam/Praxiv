from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Habit, HabitLog

# from user.models import Plan  # uncomment if you really have a Plan model


User = get_user_model()


class HabitViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user (without Plan for now — remove if you have plan logic)
        self.user = User.objects.create_user(
            email="test@example.com",
            password="pass1234",
        )
        self.client.force_authenticate(user=self.user)

        # Habits
        self.habit1 = Habit.objects.create(name="Drink Water")
        self.habit2 = Habit.objects.create(name="Read 10 pages")
        self.habit3 = Habit.objects.create(name="Run 5km")

    # ---------------- HabitListView ----------------
    def test_list_habits(self):
        url = reverse("habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    # ---------------- HabitDetailView ----------------
    def test_retrieve_habit_detail(self):
        url = reverse("habit-detail", args=[self.habit1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.habit1.id)

    def test_retrieve_habit_not_found(self):
        url = reverse("habit-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- UsersHabitsView ----------------
    def test_update_user_habits_with_valid_list(self):
        url = reverse("user-habits")
        response = self.client.patch(
            url, {"habits": [self.habit1.id, self.habit2.id]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["habits"]), 2)

    def test_update_user_habits_invalid_format(self):
        url = reverse("user-habits")
        response = self.client.patch(url, {"habits": "not-a-list"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------- HabitLogCreateView ----------------
    def test_create_habit_log(self):
        url = reverse("habit-log-create", args=[self.habit1.id])
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HabitLog.objects.count(), 1)
        log = HabitLog.objects.first()
        self.assertEqual(log.habit, self.habit1)
        self.assertEqual(log.user, self.user)

    def test_create_habit_log_invalid_habit(self):
        url = reverse("habit-log-create", args=[999])
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- UserHabitLogListView ----------------
    def test_list_user_habit_logs(self):
        HabitLog.objects.create(user=self.user, habit=self.habit1)
        HabitLog.objects.create(user=self.user, habit=self.habit2)

        url = reverse("user-habit-logs")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # newest log should come first
        self.assertEqual(response.data[0]["habit"], self.habit1.id)
