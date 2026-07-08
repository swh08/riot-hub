from rest_framework import serializers
from .models import Season, TeamComposition


MAX_BACKGROUND_SIZE = 10 * 1024 * 1024


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ["uid", "version", "is_active", "background", "created_at"]
        read_only_fields = ["background"]


class SeasonBackgroundSerializer(serializers.Serializer):
    background = serializers.ImageField()

    def validate_background(self, value):
        if value.size > MAX_BACKGROUND_SIZE:
            raise serializers.ValidationError("背景图不能超过 10 MB。")
        return value


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
