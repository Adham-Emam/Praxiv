from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    title = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)

    timezone = models.CharField(max_length=50, blank=True)

    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)

    country_code = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    website_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    habits = models.ManyToManyField(
        "habit.Habit",
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    plan = models.ForeignKey("Plan", on_delete=models.SET_NULL, null=True, blank=True)

    date_joined = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email


class UserScore(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="global_score"
    )
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} → {self.score} pts"


class Plan(models.Model):
    name = models.CharField(max_length=20, unique=True)
    price_monthly = models.DecimalField(max_digits=6, decimal_places=2)
    price_annually = models.DecimalField(max_digits=6, decimal_places=2)
    features = models.TextField()

    max_habits = models.IntegerField(default=0)
    max_leagues = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class UserProgress(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="progress"
    )
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    BASE_XP = 100  # XP required for level 1
    MULTIPLIER = 1.5  # Each next level requires 1.5x more XP

    def xp_for_level(self, level: int) -> int:
        """Total XP required to reach the *start* of a given level."""
        if level <= 1:
            return 0

        xp = 0
        for lvl in range(2, level + 1):
            xp += int(self.BASE_XP * (self.MULTIPLIER ** (lvl - 2)))
        return xp

    def calculate_level(self) -> int:
        """Determine the user's level based on total XP."""
        lvl = 1
        while self.xp >= self.xp_for_level(lvl + 1):
            lvl += 1
        return lvl

    def current_xp_in_level(self) -> int:
        """XP earned inside the current level (not total XP)."""
        return self.xp - self.xp_for_level(self.level)

    def xp_to_next_level(self) -> int:
        """Remaining XP until the next level."""
        return self.xp_for_level(self.level + 1) - self.xp

    def add_xp(self, amount: int):
        """Add XP and auto-update level."""
        self.xp += amount
        self.level = self.calculate_level()
        self.save()

    def save(self, *args, **kwargs):
        """Ensure level matches XP before saving."""
        self.level = self.calculate_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} → L{self.level} ({self.xp} XP)"
