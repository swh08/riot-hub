import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Season(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.version}{' (active)' if self.is_active else ''}"


def upload_to(instance, filename: str) -> str:
    return f"season/{instance.season.version}/{filename}"


class TeamComposition(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    season = models.ForeignKey(Season, on_delete=models.PROTECT, related_name="images")

    image = models.ImageField(upload_to=upload_to)
    filename = models.CharField(max_length=255)

    comp_code = models.CharField(max_length=255, blank=True)
    tier_level = models.IntegerField()
    tier_display = models.CharField(max_length=255)

    keywords = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["filename", "comp_code"], name="uniq_comp_code_per_season"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.filename and self.image:
            self.filename = self.image.name.rsplit("/", 1)[-1]
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        storage = self.image.storage if self.image else None
        image_name = self.image.name if self.image else ""

        super().delete(*args, **kwargs)

        if storage and image_name:
            storage.delete(image_name)
