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


class CompositionMetadataItemSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255, trim_whitespace=False)
    comp_code = serializers.CharField(
        max_length=255, allow_blank=True, required=False, default=""
    )
    tier_level = serializers.IntegerField(min_value=0, max_value=2, required=False)
    tier_display = serializers.CharField(
        max_length=255, allow_blank=True, required=False
    )
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, default=list
    )

    def validate_filename(self, value):
        if not value or "/" in value or "\\" in value:
            raise serializers.ValidationError("图片名必须是赛季目录中的单个文件名。")
        return value

    def validate(self, attrs):
        tier_level = attrs.setdefault("tier_level", 2)
        attrs.setdefault("tier_display", {0: "S", 1: "A", 2: "B"}[tier_level])
        return attrs


class CompositionMetadataSerializer(serializers.Serializer):
    schema_version = serializers.IntegerField(default=1, min_value=1, max_value=1)
    season = serializers.IntegerField(min_value=1)
    compositions = CompositionMetadataItemSerializer(many=True)

    def validate_compositions(self, value):
        filenames = [item["filename"] for item in value]
        if len(filenames) != len(set(filenames)):
            raise serializers.ValidationError("metadata 中存在重复的图片名。")

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
