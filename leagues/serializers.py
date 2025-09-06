from rest_framework import serializers
from .models import League
from datetime import date


class LeaguesSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "status"]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        if start_date and start_date < date.today():
            raise serializers.ValidationError(
                {"start_date": "Start date cannot be in the past."}
            )

        return attrs

    def get_created_by_name(self, obj):
        first_name = obj.created_by.first_name or ""
        last_name = obj.created_by.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name if full_name else obj.created_by.email
