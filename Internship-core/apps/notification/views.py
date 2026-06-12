"""通知视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import Notification
from .serializers import NotificationSerializer, CreateNotificationSerializer
from apps.user.models import User


class NotificationViewSet(viewsets.ModelViewSet):
    """消息通知 — /api/notification/"""

    serializer_class = NotificationSerializer
    permission_key = "notification:list"
    permission_key_map = {
        "create": "notification:create",
        "update": "notification:delete",
        "destroy": "notification:delete",
        "mark_read": "notification:delete",
        "mark_all_read": "notification:read-all",
        "clear_read": "notification:delete",
    }
    http_method_names = ["get", "post", "put", "delete"]

    def get_permissions(self):
        if self.action in ("create", "destroy", "mark_read", "mark_all_read", "clear_read"):
            return [IsAuthenticated(), HasPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        notification_type = self.request.query_params.get("type")
        if is_read is not None and is_read != "":
            qs = qs.filter(is_read=is_read == "true")
        if notification_type is not None and notification_type != "":
            qs = qs.filter(notification_type=int(notification_type))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_read:
            instance.is_read = True
            instance.read_time = timezone.now()
            instance.save(update_fields=["is_read", "read_time"])
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return APIResponse.success(message="删除成功")

    def create(self, request, *args, **kwargs):
        """创建通知（需 notification:create 权限）"""
        serializer = CreateNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        title = data["title"]
        content = data.get("content", "")
        notification_type = data.get("notification_type", 0)
        target_user_ids = data.get("target_user_ids")

        if target_user_ids:
            users = User.objects.filter(id__in=target_user_ids, status=1)
        else:
            users = User.objects.filter(status=1)

        notifications = [
            Notification(user=u, title=title, content=content, notification_type=notification_type)
            for u in users
        ]
        Notification.objects.bulk_create(notifications)
        return APIResponse.created(
            data={"count": len(notifications)},
            message=f"已发送给 {len(notifications)} 人",
        )

    @action(detail=True, methods=["put"], url_path="read")
    def mark_read(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_read:
            instance.is_read = True
            instance.read_time = timezone.now()
            instance.save(update_fields=["is_read", "read_time"])
        return APIResponse.success(message="已标记为已读")

    @action(detail=False, methods=["put"], url_path="read-all")
    def mark_all_read(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True, read_time=timezone.now())
        return APIResponse.success(data={"count": count}, message=f"已标记 {count} 条为已读")

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return APIResponse.success(data={"count": count})

    @action(detail=False, methods=["delete"], url_path="clear-read")
    def clear_read(self, request):
        count = Notification.objects.filter(user=request.user, is_read=True).delete()[0]
        return APIResponse.success(data={"count": count}, message=f"已清除 {count} 条已读通知")
