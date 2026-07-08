import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from tft.models import Season, TeamComposition
from tft.views import SeasonViewSet, TeamCompositionViewSet


SMALL_GIF = (
    b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def uploaded_image(name="comp.gif"):
    return SimpleUploadedFile(name, SMALL_GIF, content_type="image/gif")


class SeasonViewSetTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("tft.views.get_active_season")
    def test_current_returns_active_season_data(self, get_active_season):
        season = SimpleNamespace(uid="season-16", version="16", is_active=True)
        get_active_season.return_value = season

        view = SeasonViewSet()
        view.request = Request(self.factory.get("/api/tft/seasons/current/"))
        view.format_kwarg = None
        view.get_serializer = MagicMock(
            return_value=SimpleNamespace(data={"uid": "season-16", "version": "16"})
        )

        response = view.current(view.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["version"], "16")
        get_active_season.assert_called_once_with()
        view.get_serializer.assert_called_once_with(season)

    @patch("tft.views.Season.objects.update")
    def test_set_active_deactivates_others_and_updates_target(self, update_all):
        season = SimpleNamespace(
            uid="season-17",
            version="17",
            is_active=False,
            save=MagicMock(),
        )

        view = SeasonViewSet()
        view.request = Request(
            self.factory.post("/api/tft/seasons/season-17/set_active/")
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

    @patch("tft.views.TeamComposition.objects.select_related")
    def test_get_queryset_filters_by_requested_season(self, select_related):
        ordered = MagicMock()
        select_related.return_value.order_by.return_value = ordered

        view = TeamCompositionViewSet()
        view.request = Request(self.factory.get("/api/tft/images/", {"season": "17"}))

        queryset = view.get_queryset()

        ordered.filter.assert_called_once_with(season__version="17")
        self.assertEqual(queryset, ordered.filter.return_value)

    @patch("tft.views.get_active_season")
    @patch("tft.views.TeamComposition.objects.select_related")
    def test_get_queryset_defaults_to_active_season(
        self, select_related, get_active_season
    ):
        ordered = MagicMock()
        active_season = SimpleNamespace(uid="season-16", version="16")
        select_related.return_value.order_by.return_value = ordered
        get_active_season.return_value = active_season

        view = TeamCompositionViewSet()
        view.request = Request(self.factory.get("/api/tft/images/"))

        queryset = view.get_queryset()

        get_active_season.assert_called_once_with()
        ordered.filter.assert_called_once_with(season=active_season)
        self.assertEqual(queryset, ordered.filter.return_value)

    @patch("tft.views.get_active_season")
    def test_perform_create_saves_with_active_season(self, get_active_season):
        active_season = SimpleNamespace(uid="season-16", version="16")
        serializer = MagicMock()
        get_active_season.return_value = active_season

        view = TeamCompositionViewSet()

        view.perform_create(serializer)

        get_active_season.assert_called_once_with()
        serializer.save.assert_called_once_with(season=active_season)


class TeamCompositionModelTests(SimpleTestCase):
    @patch("django.db.models.Model.delete")
    def test_delete_removes_related_image_file(self, model_delete):
        storage = MagicMock()
        comp = TeamComposition(
            season=Season(version="17"),
            filename="comp.png",
            comp_code="test-comp",
            tier_level=0,
            tier_display="S",
            keywords=["test"],
        )
        comp.image = SimpleNamespace(name="season/17/comp.png", storage=storage)

        comp.delete()

        model_delete.assert_called_once_with()
        storage.delete.assert_called_once_with("season/17/comp.png")

    @patch("django.db.models.Model.delete")
    def test_delete_skips_storage_when_image_is_missing(self, model_delete):
        comp = TeamComposition(
            season=Season(version="17"),
            filename="comp.png",
            comp_code="test-comp",
            tier_level=0,
            tier_display="S",
            keywords=["test"],
        )
        comp.image = None

        comp.delete()

        model_delete.assert_called_once_with()


class TeamCompositionAPITests(APITestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(self.media_dir.cleanup)

    def test_composition_management_flow_uses_active_and_requested_seasons(self):
        season_16_response = self.client.post(
            "/api/tft/seasons/", {"version": "16"}, format="json"
        )
        season_17_response = self.client.post(
            "/api/tft/seasons/", {"version": "17"}, format="json"
        )
        self.assertEqual(season_16_response.status_code, 201)
        self.assertEqual(season_17_response.status_code, 201)

        activate_response = self.client.post(
            f"/api/tft/seasons/{season_16_response.data['uid']}/set_active/"
        )
        self.assertEqual(activate_response.status_code, 200)
        self.assertTrue(activate_response.data["is_active"])

        upload_response = self.client.post(
            "/api/tft/images/",
            {
                "image": uploaded_image("duelist.gif"),
                "comp_code": "SET16-DUELIST",
                "tier_level": 0,
                "tier_display": "S",
                "keywords": ["fast 8", "reroll"],
            },
            format="multipart",
        )
        self.assertEqual(upload_response.status_code, 201)
        self.assertEqual(upload_response.data["filename"], "duelist.gif")
        self.assertEqual(upload_response.data["comp_code"], "SET16-DUELIST")
        self.assertEqual(upload_response.data["tier_level"], 0)

        list_response = self.client.get("/api/tft/images/", {"season": "16"})
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["filename"], "duelist.gif")

        empty_season_response = self.client.get("/api/tft/images/", {"season": "17"})
        self.assertEqual(empty_season_response.status_code, 200)
        self.assertEqual(empty_season_response.data, [])

        comp_uid = upload_response.data["uid"]
        patch_response = self.client.patch(
            f"/api/tft/images/{comp_uid}/",
            {
                "comp_code": "SET16-DUELIST-V2",
                "tier_level": 1,
                "tier_display": "A",
                "keywords": ["tempo"],
            },
            format="json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data["comp_code"], "SET16-DUELIST-V2")
        self.assertEqual(patch_response.data["tier_level"], 1)
        self.assertEqual(patch_response.data["keywords"], ["tempo"])

        image_name = TeamComposition.objects.get(uid=comp_uid).image.name
        storage = TeamComposition.objects.get(uid=comp_uid).image.storage
        self.assertTrue(storage.exists(image_name))

        delete_response = self.client.delete(f"/api/tft/images/{comp_uid}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(TeamComposition.objects.filter(uid=comp_uid).exists())
        self.assertFalse(storage.exists(image_name))

    def test_same_filename_and_code_can_be_reused_in_different_seasons(self):
        season_16 = Season.objects.create(version="16", is_active=True)
        season_17 = Season.objects.create(version="17", is_active=False)

        first_response = self.client.post(
            "/api/tft/images/",
            {
                "image": uploaded_image("shared.gif"),
                "comp_code": "SHARED-CODE",
                "tier_level": 0,
                "tier_display": "S",
                "keywords": [],
            },
            format="multipart",
        )
        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(str(first_response.data["season"]), str(season_16.uid))

        self.client.post(f"/api/tft/seasons/{season_17.uid}/set_active/")
        second_response = self.client.post(
            "/api/tft/images/",
            {
                "image": uploaded_image("shared.gif"),
                "comp_code": "SHARED-CODE",
                "tier_level": 1,
                "tier_display": "A",
                "keywords": [],
            },
            format="multipart",
        )

        self.assertEqual(second_response.status_code, 201)
        self.assertEqual(str(second_response.data["season"]), str(season_17.uid))
        self.assertEqual(TeamComposition.objects.count(), 2)
