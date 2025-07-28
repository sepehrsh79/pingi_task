from django.urls import path

from apps.core.apis.view import NowView, StatsView


app_name = "view"
urlpatterns = [
        path("now", NowView.as_view(), name="now"),
        path("stats", StatsView.as_view(), name="stats"),
]
