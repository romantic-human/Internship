"""通知视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from utils.response import APIResponse
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """消息通知 — /api/notification/"""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "delete"]

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
        # 查看详情时自动标记已读
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

    @action(detail=True, methods=["put"], url_path="read")
    def mark_read(self, request, pk=None):
        """标记单条已读"""
        instance = self.get_object()
        if not instance.is_read:
            instance.is_read = True
            instance.read_time = timezone.now()
            instance.save(update_fields=["is_read", "read_time"])
        return APIResponse.success(message="已标记为已读")

    @action(detail=False, methods=["put"], url_path="read-all")
    def mark_all_read(self, request):
        """全部标记已读"""
        count = Notification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True, read_time=timezone.now())
        return APIResponse.success(data={"count": count}, message=f"已标记 {count} 条为已读")

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """获取未读数量"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return APIResponse.success(data={"count": count})

    @action(detail=False, methods=["delete"], url_path="clear-read")
    def clear_read(self, request):
        """清除所有已读通知"""
        count = Notification.objects.filter(user=request.user, is_read=True).delete()[0]
        return APIResponse.success(data={"count": count}, message=f"已清除 {count} 条已读通知")
