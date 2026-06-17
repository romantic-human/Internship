from rest_framework import serializers
from .models import DataSource, QueryHistory
from utils.crypto import encrypt_password


class DataSourceSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True, default="")
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, default="")

    class Meta:
        model = DataSource
        fields = [
            "id", "name", "db_type", "host", "port", "db_name",
            "username", "password", "description", "status",
            "created_by", "created_by_name", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        raw_password = validated_data.pop("password", "")
        instance = super().create(validated_data)
        instance.set_password(raw_password)
        instance.save(update_fields=["password_enc"])
        return instance

    def update(self, instance, validated_data):
        raw_password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if raw_password is not None:
            instance.set_password(raw_password)
            instance.save(update_fields=["password_enc"])
        return instance


class QueryHistorySerializer(serializers.ModelSerializer):
    datasource_name = serializers.CharField(source="datasource.name", read_only=True, default="")

    class Meta:
        model = QueryHistory
        fields = [
            "id", "user", "datasource", "datasource_name",
            "question", "generated_sql", "execution_time",
            "result_count", "status", "is_favorite", "error_message",
            "natural_language_result", "created_at",
        ]
        read_only_fields = [
            "id", "user", "generated_sql", "execution_time",
            "result_count", "status", "error_message", "created_at",
        ]


class QueryRequestSerializer(serializers.Serializer):
    datasource_id = serializers.IntegerField(required=True)
    question = serializers.CharField(required=True, max_length=2000)


class DbConnectionTestSerializer(serializers.Serializer):
    db_type = serializers.CharField(default="mysql")
    host = serializers.CharField(default="127.0.0.1")
    port = serializers.IntegerField(default=3306)
    db_name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(required=False, allow_blank=True, default="")
