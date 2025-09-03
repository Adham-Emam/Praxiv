from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

urlpatterns = [
    # Auth (JWT)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # User endpoints
    path("", views.UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    # Habits endpoints
    path("habits/", views.HabitListView.as_view(), name="habit-list"),
    path("habits/<int:pk>/", views.HabitDetailView.as_view(), name="habit-detail"),
    # Plans endpoints
    path("plans/", views.PlanListView.as_view(), name="plan-list"),
    path("plans/<int:pk>/", views.PlanDetailView.as_view(), name="plan-detail"),
]
