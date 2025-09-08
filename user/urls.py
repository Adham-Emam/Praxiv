from django.urls import path
from . import views

urlpatterns = [
    # Auth (JWT)
    path("token/", views.OpaqueTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.OpaqueRefreshView.as_view(), name="token_refresh"),
    # User endpoints
    path("", views.UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path(
        "leaderboards/global/",
        views.GlobalLeaderboardView.as_view(),
        name="global_-leaderboard",
    ),
    # Plans endpoints
    path("plans/", views.PlanListView.as_view(), name="plan-list"),
    path("plans/<int:pk>/", views.PlanDetailView.as_view(), name="plan-detail"),
]
