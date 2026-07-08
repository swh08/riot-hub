from rest_framework.exceptions import ValidationError
from .models import Season

def get_active_season() -> Season:
    season = Season.objects.filter(is_active=True).order_by("-created_at").first()
    if not season:
        raise ValidationError("No active season configured.")
    return season
