from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """自定义权限校验 — 根据权限标识判断"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # 超级管理员
        if request.user.is_superuser:
            return True
        # 从 view 读取所需的权限标识
        required_permission = getattr(view, "permission_key", None)
        if required_permission is None:
            return True
        user_permissions = request.user.permission_list if hasattr(request.user, "permission_list") else []
        return required_permission in user_permissions