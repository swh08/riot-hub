import json
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase

from tft.models import Season, TeamComposition
from tft.serializers import CompositionMetadataSerializer
from tft.views import (
    SeasonViewSet,
    TeamCompositionViewSet,
    _validate_metadata_season,
    _write_composition_metadata,
)


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


class CompositionMetadataSerializerTests(SimpleTestCase):
    def test_requires_season(self):
        serializer = CompositionMetadataSerializer(
            data={"compositions": [{"filename": "comp.png"}]}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("season", serializer.errors)

    def test_defaults_tier_fields_and_optional_metadata(self):
        serializer = CompositionMetadataSerializer(
            data={
                "season": 17,
                "compositions": [{"filename": "comp.png", "tier_level": 0}],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        item = serializer.validated_data["compositions"][0]
        self.assertEqual(item["comp_code"], "")
        self.assertEqual(item["tier_display"], "S")
        self.assertEqual(item["keywords"], [])

    def test_rejects_duplicate_filenames(self):
        serializer = CompositionMetadataSerializer(
            data={
                "season": 17,
                "compositions": [
                    {"filename": "comp.png"},
                    {"filename": "comp.png"},
                ]
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("compositions", serializer.errors)

    def test_legacy_uid_is_ignored(self):
        serializer = CompositionMetadataSerializer(
            data={
                "season": 17,
                "compositions": [
                    {
                        "uid": "2f653bae-e92b-4a30-87d6-090263c1dce2",
                        "filename": "comp.png",
                    }
                ]
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("uid", serializer.validated_data["compositions"][0])


class CompositionMetadataSeasonTests(SimpleTestCase):
    def test_rejects_non_integer_season(self):
        with self.assertRaises(ValidationError) as raised:
            _validate_metadata_season(
                {"season": "17"}, SimpleNamespace(version="17")
            )

        self.assertEqual(
            raised.exception.detail["detail"],
            "metadata 必须包含 JSON integer 类型的 season 字段。",
        )

    def test_rejects_different_season(self):
        with self.assertRaises(ValidationError) as raised:
            _validate_metadata_season({"season": 17}, SimpleNamespace(version="16"))

        self.assertEqual(
            raised.exception.detail["detail"],
            "metadata 属于赛季 17，不能恢复到赛季 16。",
        )


class CompositionMetadataWriterTests(SimpleTestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(self.media_dir.cleanup)

    def test_rewrites_metadata_with_latest_composition_values(self):
        season = SimpleNamespace(version="17")
        composition = SimpleNamespace(
            filename="comp.png",
            comp_code="OLD-CODE",
            tier_level=1,
            tier_display="A",
            keywords=["tempo"],
        )

        metadata_path = _write_composition_metadata(season, [composition])
        composition.comp_code = "NEW-CODE"
        _write_composition_metadata(season, [composition])

        with default_storage.open(metadata_path, "rb") as metadata_file:
            metadata = json.loads(metadata_file.read().decode("utf-8"))
        self.assertEqual(metadata["season"], 17)
        self.assertIsInstance(metadata["season"], int)
        self.assertEqual(metadata["compositions"][0]["comp_code"], "NEW-CODE")


class SeasonCompositionMetadataViewTests(SimpleTestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(self.media_dir.cleanup)
        self.season = SimpleNamespace(version="17")

    def metadata_upload(self, comp_code="BACKUP-CODE"):
        payload = {
            "schema_version": 1,
            "season": 17,
            "compositions": [
                {
                    "filename": "comp.gif",
                    "comp_code": comp_code,
                    "tier_level": 0,
                    "tier_display": "S",
                    "keywords": ["backup"],
                }
            ],
        }
        return SimpleUploadedFile(
            "metadata.json",
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
        )

    def store_image(self):
        default_storage.save("season/17/comp.gif", ContentFile(SMALL_GIF))

    def test_exports_existing_metadata_as_attachment(self):
        _write_composition_metadata(self.season, [])
        view = SeasonViewSet()
        view.get_object = MagicMock(return_value=self.season)

        response = view.composition_metadata(
            SimpleNamespace(method="GET"), pk="season-17"
        )
        body = b"".join(response.streaming_content)
        response.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn(
            'filename="season-17-metadata.json"', response["Content-Disposition"]
        )
        self.assertEqual(json.loads(body.decode("utf-8"))["season"], 17)

    def test_imports_metadata_and_runs_composition_sync(self):
        self.store_image()
        view = SeasonViewSet()
        view.get_object = MagicMock(return_value=self.season)
        view.import_compositions = MagicMock(
            return_value=Response({"imported": 1, "updated": 0, "skipped": 0})
        )
        request = SimpleNamespace(
            method="POST", data={"metadata": self.metadata_upload()}
        )

        response = view.composition_metadata(request, pk="season-17")

        self.assertTrue(response.data["metadata_imported"])
        view.import_compositions.assert_called_once_with(request, pk="season-17")
        with default_storage.open("season/17/metadata.json", "rb") as metadata_file:
            metadata = json.loads(metadata_file.read().decode("utf-8"))
        self.assertEqual(metadata["compositions"][0]["comp_code"], "BACKUP-CODE")

    def test_failed_import_restores_previous_metadata(self):
        self.store_image()
        previous = SimpleNamespace(
            filename="comp.gif",
            comp_code="CURRENT-CODE",
            tier_level=1,
            tier_display="A",
            keywords=[],
        )
        _write_composition_metadata(self.season, [previous])
        view = SeasonViewSet()
        view.get_object = MagicMock(return_value=self.season)
        view.import_compositions = MagicMock(
            side_effect=ValidationError({"detail": "数据库同步失败"})
        )
        request = SimpleNamespace(
            method="POST", data={"metadata": self.metadata_upload("BACKUP-CODE")}
        )

        with self.assertRaises(ValidationError):
            view.composition_metadata(request, pk="season-17")

        with default_storage.open("season/17/metadata.json", "rb") as metadata_file:
            metadata = json.loads(metadata_file.read().decode("utf-8"))
        self.assertEqual(metadata["compositions"][0]["comp_code"], "CURRENT-CODE")


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

    @patch("tft.views._write_composition_metadata")
    @patch("tft.views.get_active_season")
    def test_perform_create_updates_metadata(
        self, get_active_season, write_composition_metadata
    ):
        active_season = SimpleNamespace(uid="season-16", version="16")
        serializer = MagicMock()
        get_active_season.return_value = active_season

        view = TeamCompositionViewSet()

        view.perform_create(serializer)

        get_active_season.assert_called_once_with()
        serializer.save.assert_called_once_with(season=active_season)
        write_composition_metadata.assert_called_once_with(active_season)

    @patch("tft.views._write_composition_metadata")
    def test_perform_update_updates_metadata(self, write_composition_metadata):
        season = SimpleNamespace(uid="season-16", version="16")
        serializer = MagicMock()
        serializer.save.return_value = SimpleNamespace(season=season)

        TeamCompositionViewSet().perform_update(serializer)

        serializer.save.assert_called_once_with()
        write_composition_metadata.assert_called_once_with(season)

    @patch("tft.views._write_composition_metadata")
    def test_perform_destroy_updates_metadata(self, write_composition_metadata):
        season = SimpleNamespace(uid="season-16", version="16")
        composition = SimpleNamespace(season=season, delete=MagicMock())

        TeamCompositionViewSet().perform_destroy(composition)

        composition.delete.assert_called_once_with()
        write_composition_metadata.assert_called_once_with(season)


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


class SeasonBackgroundAPITests(APITestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(self.media_dir.cleanup)

        self.season = Season.objects.create(version="16", is_active=True)

    def upload_background(self, name="bg.gif"):
        return self.client.post(
            f"/api/tft/seasons/{self.season.uid}/background/",
            {"background": uploaded_image(name)},
            format="multipart",
        )

    def test_upload_sets_background_and_stores_file(self):
        response = self.upload_background()

        self.assertEqual(response.status_code, 200)
        self.assertIn("bg", response.data["background"])

        self.season.refresh_from_db()
        self.assertTrue(self.season.background)
        self.assertTrue(
            self.season.background.storage.exists(self.season.background.name)
        )

    def test_replacing_background_deletes_previous_file(self):
        self.upload_background("first.gif")
        self.season.refresh_from_db()
        old_name = self.season.background.name
        storage = self.season.background.storage

        response = self.upload_background("second.gif")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(storage.exists(old_name))

        self.season.refresh_from_db()
        self.assertIn("second", self.season.background.name)
        self.assertTrue(storage.exists(self.season.background.name))

    def test_delete_clears_background_and_removes_file(self):
        self.upload_background()
        self.season.refresh_from_db()
        old_name = self.season.background.name
        storage = self.season.background.storage

        response = self.client.delete(
            f"/api/tft/seasons/{self.season.uid}/background/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["background"])
        self.assertFalse(storage.exists(old_name))

        self.season.refresh_from_db()
        self.assertFalse(self.season.background)

    def test_upload_rejects_non_image_file(self):
        response = self.client.post(
            f"/api/tft/seasons/{self.season.uid}/background/",
            {
                "background": SimpleUploadedFile(
                    "not-image.txt", b"plain text", content_type="text/plain"
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_background_included_in_season_list(self):
        self.upload_background()

        response = self.client.get("/api/tft/seasons/")

        self.assertEqual(response.status_code, 200)
        payload = response.data[0] if isinstance(response.data, list) else None
        self.assertIsNotNone(payload)
        self.assertTrue(payload["background"])


class TeamCompositionAPITests(APITestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(self.media_dir.cleanup)

    @staticmethod
    def store_season_file(season, filename):
        path = f"season/{season.version}/{filename}"
        return default_storage.save(path, ContentFile(SMALL_GIF))

    @staticmethod
    def read_metadata(season):
        path = f"season/{season.version}/metadata.json"
        with default_storage.open(path, "rb") as metadata_file:
            return json.loads(metadata_file.read().decode("utf-8"))

    @staticmethod
    def write_metadata(season, payload):
        path = f"season/{season.version}/metadata.json"
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(
            path,
            ContentFile(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
        )

    def test_import_compositions_creates_portable_metadata(self):
        season = Season.objects.create(version="17", is_active=True)
        self.store_season_file(season, "阵容.gif")

        response = self.client.post(
            f"/api/tft/seasons/{season.uid}/import-compositions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["imported"], 1)
        self.assertEqual(response.data["updated"], 0)
        self.assertTrue(response.data["metadata_created"])

        TeamComposition.objects.get(season=season)
        metadata = self.read_metadata(season)
        self.assertEqual(metadata["schema_version"], 1)
        self.assertEqual(metadata["season"], 17)
        self.assertEqual(len(metadata["compositions"]), 1)
        self.assertNotIn("uid", metadata["compositions"][0])
        self.assertEqual(metadata["compositions"][0]["filename"], "阵容.gif")
        self.assertEqual(metadata["compositions"][0]["comp_code"], "")

    def test_first_metadata_generation_preserves_existing_database_values(self):
        season = Season.objects.create(version="17", is_active=True)
        self.store_season_file(season, "existing.gif")
        TeamComposition.objects.create(
            season=season,
            image="season/17/existing.gif",
            filename="existing.gif",
            comp_code="SET17-EXISTING",
            tier_level=1,
            tier_display="A",
            keywords=["tempo"],
        )

        response = self.client.post(
            f"/api/tft/seasons/{season.uid}/import-compositions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["imported"], 0)
        self.assertEqual(response.data["updated"], 0)
        self.assertEqual(response.data["skipped"], 1)

        metadata_item = self.read_metadata(season)["compositions"][0]
        self.assertNotIn("uid", metadata_item)
        self.assertEqual(metadata_item["comp_code"], "SET17-EXISTING")
        self.assertEqual(metadata_item["tier_level"], 1)
        self.assertEqual(metadata_item["tier_display"], "A")
        self.assertEqual(metadata_item["keywords"], ["tempo"])

    def test_import_compositions_updates_database_from_metadata(self):
        season = Season.objects.create(version="17", is_active=True)
        self.store_season_file(season, "existing.gif")
        self.client.post(f"/api/tft/seasons/{season.uid}/import-compositions/")
        composition = TeamComposition.objects.get(season=season)

        metadata = self.read_metadata(season)
        metadata["compositions"][0].update(
            {
                "comp_code": "SET17-UPDATED",
                "tier_level": 0,
                "tier_display": "S+",
                "keywords": ["fast 9", "flex"],
            }
        )
        self.write_metadata(season, metadata)

        response = self.client.post(
            f"/api/tft/seasons/{season.uid}/import-compositions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["imported"], 0)
        self.assertEqual(response.data["updated"], 1)
        self.assertFalse(response.data["metadata_created"])

        composition.refresh_from_db()
        self.assertEqual(composition.filename, "existing.gif")
        self.assertEqual(composition.image.name, "season/17/existing.gif")
        self.assertEqual(composition.comp_code, "SET17-UPDATED")
        self.assertEqual(composition.tier_level, 0)
        self.assertEqual(composition.tier_display, "S+")
        self.assertEqual(composition.keywords, ["fast 9", "flex"])

    def test_import_compositions_rejects_metadata_for_missing_image(self):
        season = Season.objects.create(version="17", is_active=True)
        self.store_season_file(season, "actual.gif")
        self.write_metadata(
            season,
            {
                "schema_version": 1,
                "season": 17,
                "compositions": [{"filename": "missing.gif"}],
            },
        )

        response = self.client.post(
            f"/api/tft/seasons/{season.uid}/import-compositions/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("missing.gif", response.data["detail"])
        self.assertFalse(TeamComposition.objects.filter(season=season).exists())

    def test_import_compositions_rejects_metadata_from_another_season(self):
        season = Season.objects.create(version="16", is_active=True)
        self.store_season_file(season, "comp.gif")
        self.write_metadata(
            season,
            {
                "schema_version": 1,
                "season": 17,
                "compositions": [{"filename": "comp.gif"}],
            },
        )

        response = self.client.post(
            f"/api/tft/seasons/{season.uid}/import-compositions/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "metadata 属于赛季 17，不能恢复到赛季 16。",
        )
        self.assertFalse(TeamComposition.objects.filter(season=season).exists())

    def test_metadata_file_import_restores_and_export_downloads_state(self):
        season = Season.objects.create(version="17", is_active=True)
        self.store_season_file(season, "backup.gif")
        metadata = {
            "schema_version": 1,
            "season": 17,
            "compositions": [
                {
                    "filename": "backup.gif",
                    "comp_code": "SET17-BACKUP",
                    "tier_level": 1,
                    "tier_display": "A",
                    "keywords": ["restored"],
                }
            ],
        }

        import_response = self.client.post(
            f"/api/tft/seasons/{season.uid}/composition-metadata/",
            {
                "metadata": SimpleUploadedFile(
                    "metadata.json",
                    json.dumps(metadata).encode("utf-8"),
                    content_type="application/json",
                )
            },
            format="multipart",
        )

        self.assertEqual(import_response.status_code, 200)
        self.assertTrue(import_response.data["metadata_imported"])
        composition = TeamComposition.objects.get(season=season)
        self.assertEqual(composition.filename, "backup.gif")
        self.assertEqual(composition.comp_code, "SET17-BACKUP")
        self.assertEqual(composition.tier_level, 1)
        self.assertEqual(composition.keywords, ["restored"])

        export_response = self.client.get(
            f"/api/tft/seasons/{season.uid}/composition-metadata/"
        )
        exported_metadata = json.loads(
            b"".join(export_response.streaming_content).decode("utf-8")
        )

        self.assertEqual(export_response.status_code, 200)
        self.assertIn("attachment", export_response["Content-Disposition"])
        self.assertEqual(exported_metadata["season"], 17)
        self.assertEqual(
            exported_metadata["compositions"][0]["comp_code"], "SET17-BACKUP"
        )

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
        season_16 = Season.objects.get(uid=season_16_response.data["uid"])
        self.assertEqual(
            self.read_metadata(season_16)["compositions"][0]["comp_code"],
            "SET16-DUELIST",
        )

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
        self.assertEqual(
            self.read_metadata(season_16)["compositions"][0]["comp_code"],
            "SET16-DUELIST-V2",
        )

        image_name = TeamComposition.objects.get(uid=comp_uid).image.name
        storage = TeamComposition.objects.get(uid=comp_uid).image.storage
        self.assertTrue(storage.exists(image_name))

        delete_response = self.client.delete(f"/api/tft/images/{comp_uid}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(TeamComposition.objects.filter(uid=comp_uid).exists())
        self.assertFalse(storage.exists(image_name))
        self.assertEqual(self.read_metadata(season_16)["compositions"], [])

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
