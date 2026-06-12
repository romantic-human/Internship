from django.contrib import admin
from .models import DataSource, QueryHistory


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "db_type", "host", "db_name", "status", "created_at"]
    list_filter = ["db_type", "status"]


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "user", "datasource", "status", "is_favorite", "created_at"]
    list_filter = ["status", "is_favorite"]
