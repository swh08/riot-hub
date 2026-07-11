from pathlib import Path, PurePosixPath

from django.core.files.storage import default_storage
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Season, TeamComposition
from .serializers import (
    SeasonBackgroundSerializer,
    SeasonSerializer,
    TeamCompositionSerializer,
)
from .services import get_active_season


SUPPORTED_COMPOSITION_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}


class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all().order_by("-created_at")
    serializer_class = SeasonSerializer

    @action(detail=False, methods=["get"])
    def current(self, request):
        season = get_active_season()
        return Response(self.get_serializer(season).data)

    @action(detail=True, methods=["post", "delete"])
    def background(self, request, pk=None):
        season = self.get_object()

        if request.method == "DELETE":
            self._delete_background_file(season)
            season.background = None
            season.save(update_fields=["background"])
            return Response(self.get_serializer(season).data)

        upload = SeasonBackgroundSerializer(data=request.data)
        upload.is_valid(raise_exception=True)

        self._delete_background_file(season)
        season.background = upload.validated_data["background"]
        season.save(update_fields=["background"])
        return Response(self.get_serializer(season).data)

    @staticmethod
    def _delete_background_file(season):
        if season.background:
            season.background.storage.delete(season.background.name)

    @action(detail=True, methods=["post"])
    def set_active(self, request, pk=None):
        # 把其他 season 设为非 active，再设当前为 active
        Season.objects.update(is_active=False)
        season = self.get_object()
        season.is_active = True
        season.save(update_fields=["is_active"])
        return Response(self.get_serializer(season).data)

    @action(detail=True, methods=["post"], url_path="import-compositions")
    def import_compositions(self, request, pk=None):
        season = self.get_object()
        directory = PurePosixPath("season", season.version).as_posix()

        try:
            _, filenames = default_storage.listdir(directory)
        except FileNotFoundError as exc:
            raise NotFound(
                detail=f"未找到当前赛季的媒体目录：media/{directory}"
            ) from exc

        image_filenames = sorted(
            filename
            for filename in filenames
            if Path(filename).suffix.lower() in SUPPORTED_COMPOSITION_EXTENSIONS
        )
        existing_filenames = set(
            TeamComposition.objects.filter(
                season=season,
                filename__in=image_filenames,
            ).values_list("filename", flat=True)
        )

        compositions = [
            TeamComposition(
                season=season,
                image=PurePosixPath(directory, filename).as_posix(),
                filename=filename,
                comp_code="",
                tier_level=2,
                tier_display="B",
                keywords=[],
            )
            for filename in image_filenames
            if filename not in existing_filenames
        ]
        TeamComposition.objects.bulk_create(compositions)

        return Response(
            {
                "season": season.version,
                "imported": len(compositions),
                "skipped": len(existing_filenames),
                "ignored": len(filenames) - len(image_filenames),
            }
        )


class TeamCompositionViewSet(viewsets.ModelViewSet):
    serializer_class = TeamCompositionSerializer

    def get_queryset(self):
        qs = TeamComposition.objects.select_related("season").order_by("-created_at")

        season_version = self.request.query_params.get("season")

        if season_version:
            return qs.filter(season__version=season_version)

        return qs.filter(season=get_active_season())

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        season = get_active_season()
        serializer.save(season=season)
