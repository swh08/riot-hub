from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.views import SeasonViewSet, TeamCompositionViewSet


class SeasonViewSetTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("core.views.get_active_season")
    def test_current_returns_active_season_data(self, get_active_season):
        season = SimpleNamespace(uid="season-16", version="16", is_active=True)
        get_active_season.return_value = season

        view = SeasonViewSet()
        view.request = Request(self.factory.get("/api/seasons/current/"))
        view.format_kwarg = None
        view.get_serializer = MagicMock(
            return_value=SimpleNamespace(data={"uid": "season-16", "version": "16"})
        )

        response = view.current(view.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["version"], "16")
        get_active_season.assert_called_once_with()
        view.get_serializer.assert_called_once_with(season)

    @patch("core.views.Season.objects.update")
    def test_set_active_deactivates_others_and_updates_target(self, update_all):
        season = SimpleNamespace(
            uid="season-17",
            version="17",
            is_active=False,
            save=MagicMock(),
        )

        view = SeasonViewSet()
        view.request = Request(
            self.factory.post("/api/seasons/season-17/set_active/")
        )
        view.format_kwarg = None
        view.get_object = MagicMock(return_value=season)
        view.get_serializer = MagicMock(
            return_value=SimpleNamespace(data={"uid": "season-17", "is_active": True})
        )

        response = view.set_active(view.request, pk="season-17")

        self.assertEqual(response.status_code, 200)
        update_all.assert_called_once_with(is_active=False)
        self.assertTrue(season.is_active)
        season.save.assert_called_once_with(update_fields=["is_active"])
        view.get_object.assert_called_once_with()


class TeamCompositionViewSetTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("core.views.TeamComposition.objects.select_related")
    def test_get_queryset_filters_by_requested_season(self, select_related):
        ordered = MagicMock()
        select_related.return_value.order_by.return_value = ordered

        view = TeamCompositionViewSet()
        view.request = Request(self.factory.get("/api/images/", {"season": "17"}))

        queryset = view.get_queryset()

        ordered.filter.assert_called_once_with(season__version="17")
        self.assertEqual(queryset, ordered.filter.return_value)

    @patch("core.views.get_active_season")
    @patch("core.views.TeamComposition.objects.select_related")
    def test_get_queryset_defaults_to_active_season(
        self, select_related, get_active_season
    ):
        ordered = MagicMock()
        active_season = SimpleNamespace(uid="season-16", version="16")
        select_related.return_value.order_by.return_value = ordered
        get_active_season.return_value = active_season

        view = TeamCompositionViewSet()
        view.request = Request(self.factory.get("/api/images/"))

        queryset = view.get_queryset()

        get_active_season.assert_called_once_with()
        ordered.filter.assert_called_once_with(season=active_season)
        self.assertEqual(queryset, ordered.filter.return_value)

    @patch("core.views.get_active_season")
    def test_perform_create_saves_with_active_season(self, get_active_season):
        active_season = SimpleNamespace(uid="season-16", version="16")
        serializer = MagicMock()
        get_active_season.return_value = active_season

        view = TeamCompositionViewSet()

        view.perform_create(serializer)

        get_active_season.assert_called_once_with()
        serializer.save.assert_called_once_with(season=active_season)
