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


class CreateNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    content = serializers.CharField(required=False, allow_blank=True, default="")
    notification_type = serializers.IntegerField(default=0)
    target_user_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
