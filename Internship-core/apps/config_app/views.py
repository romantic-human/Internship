"""系统配置模块视图 — 参考《组织架构模块设计方案.md》第 5.8 节"""
from rest_framework import viewsets
from rest_framework.decorators import action
from utils import APIResponse
from .models import SystemConfig
from .serializers import SystemConfigSerializer


class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer

    @action(detail=False, methods=["get"], url_path="by-key/(?P<key>[^/.]+)")
    def by_key(self, request, key=None):
        """根据键获取配置值 — GET /api/config/by-key/:key"""
        config = SystemConfig.objects.filter(config_key=key).first()
        if config:
            return APIResponse.success(data=config.config_value)
        return APIResponse.not_found()