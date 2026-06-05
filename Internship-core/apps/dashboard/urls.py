from django.urls import path

from apps.dashboard import views

urlpatterns = [
    path("", views.dashboard_stats, name="dashboard_stats"),
    path("trend", views.dashboard_trend, name="dashboard_trend"),
]