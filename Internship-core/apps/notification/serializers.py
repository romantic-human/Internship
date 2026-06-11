"""通知模块序列化器"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_notification_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "title", "content", "notification_type", "type_display",
            "is_read", "extra_data", "create_time", "read_time",
        ]
