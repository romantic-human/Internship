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
        # 支持通配符 *:*:*
        if "*:*:*" in user_permissions:
            return True
        # 支持模块级通配符 e.g. user:* 匹配 user:list
        parts = required_permission.split(":")
        for up in user_permissions:
            uparts = up.split(":")
            if len(uparts) == 2 and uparts[1] == "*":
                if uparts[0] == parts[0]:
                    return True
            if up == required_permission:
                return True
        return False