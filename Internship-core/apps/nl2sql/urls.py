from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r"datasource", views.DataSourceViewSet, basename="datasource")
router.register(r"history", views.QueryHistoryViewSet, basename="queryhistory")

urlpatterns = [
    path("", include(router.urls)),
    path("query", views.QueryView.as_view(), name="nl2sql-query"),
]
