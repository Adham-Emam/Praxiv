from django.urls import path
from . import views


urlpatterns = [
    path("", views.LeagueListView.as_view(), name="league-list"),
    path("create/", views.LeagueCreateView.as_view(), name="league-create"),
    path("<int:pk>/", views.LeagueDetailsView.as_view(), name="league-detail"),
    path(
        "<int:pk>/edit/",
        views.LeagueRetrieveUpdateDestroyView.as_view(),
        name="league-edit",
    ),
    path("<int:pk>/enter/", views.LeagueEnterView.as_view(), name="league-enter"),
    path(
        "leaderboards/<int:league_id>/",
        views.LeagueLeaderboardView.as_view(),
        name="league_leaderboard",
    ),
]
