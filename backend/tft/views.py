import json
from pathlib import Path, PurePosixPath

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import IntegrityError, transaction
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .models import Season, TeamComposition
from .serializers import (
    CompositionMetadataSerializer,
    SeasonBackgroundSerializer,
    SeasonSerializer,
    TeamCompositionSerializer,
)
from .services import get_active_season


SUPPORTED_COMPOSITION_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
COMPOSITION_METADATA_FILENAME = "metadata.json"
MAX_COMPOSITION_METADATA_SIZE = 5 * 1024 * 1024


def _season_version_number(season):
    try:
        return int(season.version)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            {"detail": "赛季版本必须是整数，才能读写阵容 metadata。"}
        ) from exc


def _validate_metadata_season(metadata_payload, season):
    metadata_season = (
        metadata_payload.get("season")
        if isinstance(metadata_payload, dict)
        else None
    )
    if type(metadata_season) is not int:
        raise ValidationError(
            {"detail": "metadata 必须包含 JSON integer 类型的 season 字段。"}
        )

    expected_season = _season_version_number(season)
    if metadata_season != expected_season:
        raise ValidationError(
            {
                "detail": (
                    f"metadata 属于赛季 {metadata_season}，"
                    f"不能恢复到赛季 {expected_season}。"
                )
            }
        )


def _composition_metadata_item(composition):
    return {
        "filename": composition.filename,
        "comp_code": composition.comp_code,
        "tier_level": composition.tier_level,
        "tier_display": composition.tier_display,
        "keywords": composition.keywords,
    }


def _default_composition_metadata_item(filename):
    return {
        "filename": filename,
        "comp_code": "",
        "tier_level": 2,
        "tier_display": "B",
        "keywords": [],
    }


def _save_composition_metadata_payload(metadata_path, metadata_payload):
    metadata_content = json.dumps(
        metadata_payload, ensure_ascii=False, indent=2, default=str
    ).encode("utf-8")
    if default_storage.exists(metadata_path):
        default_storage.delete(metadata_path)
    default_storage.save(metadata_path, ContentFile(metadata_content + b"\n"))


def _validate_metadata_images(metadata_items, image_filenames):
    missing_filenames = sorted(
        item["filename"]
        for item in metadata_items
        if item["filename"] not in image_filenames
    )
    if missing_filenames:
        raise ValidationError(
            {
                "detail": "metadata 中的图片不存在于赛季目录："
                + "、".join(missing_filenames)
            }
        )


def _write_composition_metadata(season, compositions=None):
    if compositions is None:
        compositions = TeamComposition.objects.filter(season=season)

    metadata_path = PurePosixPath(
        "season", season.version, COMPOSITION_METADATA_FILENAME
    ).as_posix()
    metadata_payload = {
        "schema_version": 1,
        "season": _season_version_number(season),
        "compositions": [
            _composition_metadata_item(composition)
            for composition in sorted(
                compositions, key=lambda composition: composition.filename
            )
        ],
    }
    _save_composition_metadata_payload(metadata_path, metadata_payload)
    return metadata_path


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

    @action(detail=True, methods=["get", "post"], url_path="composition-metadata")
    def composition_metadata(self, request, pk=None):
        season = self.get_object()
        directory = PurePosixPath("season", season.version).as_posix()
        metadata_path = PurePosixPath(
            directory, COMPOSITION_METADATA_FILENAME
        ).as_posix()

        if request.method == "GET":
            if not default_storage.exists(metadata_path):
                _write_composition_metadata(season)
            return FileResponse(
                default_storage.open(metadata_path, "rb"),
                as_attachment=True,
                filename=f"season-{season.version}-metadata.json",
                content_type="application/json",
            )

        metadata_upload = request.data.get("metadata")
        if metadata_upload is None:
            raise ValidationError({"detail": "请选择要导入的 metadata JSON 文件。"})
        if not hasattr(metadata_upload, "read") or not hasattr(metadata_upload, "size"):
            raise ValidationError({"detail": "metadata 必须通过文件上传。"})
        if metadata_upload.size > MAX_COMPOSITION_METADATA_SIZE:
            raise ValidationError({"detail": "metadata 文件不能超过 5 MB。"})

        try:
            metadata_payload = json.loads(metadata_upload.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError(
                {"detail": "上传的 metadata 不是有效的 UTF-8 JSON 文件。"}
            ) from exc

        _validate_metadata_season(metadata_payload, season)
        metadata_serializer = CompositionMetadataSerializer(data=metadata_payload)
        metadata_serializer.is_valid(raise_exception=True)
        validated_metadata = metadata_serializer.validated_data

        try:
            _, filenames = default_storage.listdir(directory)
        except FileNotFoundError as exc:
            raise NotFound(
                detail=f"未找到当前赛季的媒体目录：media/{directory}"
            ) from exc
        image_filenames = {
            filename
            for filename in filenames
            if Path(filename).suffix.lower() in SUPPORTED_COMPOSITION_EXTENSIONS
        }
        _validate_metadata_images(
            validated_metadata["compositions"], image_filenames
        )

        previous_metadata = None
        if default_storage.exists(metadata_path):
            with default_storage.open(metadata_path, "rb") as metadata_file:
                previous_metadata = metadata_file.read()

        _save_composition_metadata_payload(metadata_path, validated_metadata)
        try:
            response = self.import_compositions(request, pk=pk)
        except Exception:
            if default_storage.exists(metadata_path):
                default_storage.delete(metadata_path)
            if previous_metadata is not None:
                default_storage.save(metadata_path, ContentFile(previous_metadata))
            raise

        response.data["metadata_imported"] = True
        return response

    @action(detail=True, methods=["post"], url_path="import-compositions")
    def import_compositions(self, request, pk=None):
        season = self.get_object()
        directory = PurePosixPath("season", season.version).as_posix()
        metadata_path = PurePosixPath(
            directory, COMPOSITION_METADATA_FILENAME
        ).as_posix()

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
        image_filename_set = set(image_filenames)
        existing_compositions = list(
            TeamComposition.objects.filter(season=season).order_by("created_at")
        )
        existing_by_filename = {}
        for composition in existing_compositions:
            existing_by_filename.setdefault(composition.filename, composition)

        metadata_exists = default_storage.exists(metadata_path)
        if metadata_exists:
            try:
                with default_storage.open(metadata_path, "rb") as metadata_file:
                    metadata_payload = json.loads(metadata_file.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValidationError(
                    {"detail": f"{COMPOSITION_METADATA_FILENAME} 不是有效的 UTF-8 JSON 文件。"}
                ) from exc

            _validate_metadata_season(metadata_payload, season)
            metadata_serializer = CompositionMetadataSerializer(data=metadata_payload)
            metadata_serializer.is_valid(raise_exception=True)
            validated_metadata = metadata_serializer.validated_data
            metadata_items = list(validated_metadata["compositions"])
        else:
            metadata_items = []
            for filename in image_filenames:
                composition = existing_by_filename.get(filename)
                metadata_items.append(
                    _composition_metadata_item(composition)
                    if composition
                    else _default_composition_metadata_item(filename)
                )

        _validate_metadata_images(metadata_items, image_filename_set)

        metadata_filenames = {item["filename"] for item in metadata_items}
        for filename in image_filenames:
            if filename in metadata_filenames:
                continue

            composition = existing_by_filename.get(filename)
            metadata_items.append(
                _composition_metadata_item(composition)
                if composition
                else _default_composition_metadata_item(filename)
            )

        imported = 0
        updated = 0
        unchanged = 0
        synced_compositions = []

        try:
            with transaction.atomic():
                for item in metadata_items:
                    composition = existing_by_filename.get(item["filename"])

                    image_name = PurePosixPath(directory, item["filename"]).as_posix()
                    if composition is None:
                        create_kwargs = {
                            "season": season,
                            "image": image_name,
                            "filename": item["filename"],
                            "comp_code": item["comp_code"],
                            "tier_level": item["tier_level"],
                            "tier_display": item["tier_display"],
                            "keywords": item["keywords"],
                        }
                        composition = TeamComposition.objects.create(**create_kwargs)
                        imported += 1
                    else:
                        changed_fields = []
                        values = {
                            "image": image_name,
                            "filename": item["filename"],
                            "comp_code": item["comp_code"],
                            "tier_level": item["tier_level"],
                            "tier_display": item["tier_display"],
                            "keywords": item["keywords"],
                        }
                        for field, value in values.items():
                            current_value = (
                                composition.image.name
                                if field == "image" and composition.image
                                else getattr(composition, field)
                            )
                            if current_value != value:
                                setattr(composition, field, value)
                                changed_fields.append(field)

                        if changed_fields:
                            composition.save(
                                update_fields=[*changed_fields, "updated_at"]
                            )
                            updated += 1
                        else:
                            unchanged += 1

                    synced_compositions.append(composition)
        except IntegrityError as exc:
            raise ValidationError(
                {"detail": "metadata 更新与现有阵容的图片名或阵容码冲突。"}
            ) from exc

        _write_composition_metadata(season, synced_compositions)

        return Response(
            {
                "season": season.version,
                "imported": imported,
                "updated": updated,
                "skipped": unchanged,
                "ignored": sum(
                    1
                    for filename in filenames
                    if filename != COMPOSITION_METADATA_FILENAME
                    and filename not in image_filename_set
                ),
                "metadata": metadata_path,
                "metadata_created": not metadata_exists,
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
        _write_composition_metadata(season)

    def perform_update(self, serializer):
        composition = serializer.save()
        _write_composition_metadata(composition.season)

    def perform_destroy(self, instance):
        season = instance.season
        instance.delete()
        _write_composition_metadata(season)
