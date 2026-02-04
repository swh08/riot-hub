from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Season, TeamComposition
from .serializers import SeasonSerializer, TeamCompositionSerializer
from .services import get_active_season


class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all().order_by("-created_at")
    serializer_class = SeasonSerializer

    @action(detail=False, methods=["get"])
    def current(self, request):
        season = get_active_season()
        return Response(self.get_serializer(season).data)

    @action(detail=True, methods=["post"])
    def set_active(self, request, pk=None):
        # 把其他 season 设为非 active，再设当前为 active
        Season.objects.update(is_active=False)
        season = self.get_object()
        season.is_active = True
        season.save(update_fields=["is_active"])
        return Response(self.get_serializer(season).data)


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
