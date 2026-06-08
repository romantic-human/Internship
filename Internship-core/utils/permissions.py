from rest_framework.permissions import BasePermission


# 标准 CRUD 动作 → 权限后缀映射
ACTION_SUFFIX = {
    "create": "add",
    "update": "edit",
    "partial_update": "edit",
    "destroy": "delete",
}


class HasPermission(BasePermission):
    """自定义权限校验 — 支持动作级粒度

    规则：
    1. 超级管理员直接放行
    2. 如果 view 定义了 permission_key_map[action]，使用该值
    3. 否则从 permission_key（如 "dept:list"）提取模块名，
       按 ACTION_SUFFIX 映射后缀（create→add, update→edit, destroy→delete）
    4. 未匹配的动作（如 export）回退到 permission_key
    5. 支持 *:*:* 通配符
    6. 支持模块级通配符 user:* → 匹配 user:list, user:add 等
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        user_permissions = getattr(request.user, "permission_list", [])
        if "*:*:*" in user_permissions:
            return True

        required_permission = self._resolve_permission(view)
        if required_permission is None:
            return True

        if required_permission in user_permissions:
            return True

        # 模块级通配符：user:* 匹配 user:list, user:add ...
        parts = required_permission.split(":")
        for up in user_permissions:
            uparts = up.split(":")
            if len(uparts) == 2 and uparts[1] == "*" and uparts[0] == parts[0]:
                return True

        return False

    def _resolve_permission(self, view):
        """根据 action 解析实际需要的权限标识"""
        key_map = getattr(view, "permission_key_map", None)
        if key_map and view.action in key_map:
            return key_map[view.action]

        base = getattr(view, "permission_key", None)
        if base is None:
            return None

        # 如果 permission_key 本身不含冒号，直接返回
        if ":" not in base:
            return base

        module = base.split(":")[0]
        suffix = ACTION_SUFFIX.get(view.action)
        if suffix:
            return f"{module}:{suffix}"
        # 未匹配的动作（list, retrieve, export, batch, ...）使用原始值
        return base