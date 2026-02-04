from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SeasonViewSet, TeamCompositionViewSet

router = DefaultRouter()
router.register("seasons", SeasonViewSet, basename="season")
router.register("images", TeamCompositionViewSet, basename="image")
urlpatterns = [
    path("", include(router.urls)),
]
