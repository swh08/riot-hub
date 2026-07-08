from rest_framework import serializers
from .models import Season, TeamComposition


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ["uid", "version", "is_active", "created_at"]


class TeamCompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamComposition
        fields = [
            "uid",
            "season",
            "image",
            "filename",
            "comp_code",
            "tier_level",
            "tier_display",
            "keywords",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uid", "season", "filename", "created_at", "updated_at"]
