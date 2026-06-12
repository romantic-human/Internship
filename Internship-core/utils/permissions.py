from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """自定义权限校验 — 根据权限标识判断（支持 action 级细分）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        permission_key_map = getattr(view, "permission_key_map", {})
        permission_key = getattr(view, "permission_key", None)
        required = permission_key_map.get(view.action, permission_key)

        if required is None:
            return True
        user_permissions = request.user.permission_list if hasattr(request.user, "permission_list") else []
        return required in user_permissions