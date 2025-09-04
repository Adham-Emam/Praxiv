from rest_framework import serializers
from .models import CustomUser, Habit, Plan


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    habits = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Habit.objects.all(),
        required=False,
        allow_empty=True,
    )
    plan = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Plan.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "email_verified",
            "first_name",
            "last_name",
            "bio",
            "title",
            "company",
            "timezone",
            "country",
            "city",
            "country_code",
            "phone_number",
            "website_url",
            "linkedin_url",
            "twitter_url",
            "github_url",
            "habits",
            "plan",
            "date_joined",
            "is_staff",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        if not validated_data.get("plan"):
            free_plan = Plan.objects.get(name="Free")
            validated_data["plan"] = free_plan

        user = CustomUser.objects.create_user(**validated_data)
        return user


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
