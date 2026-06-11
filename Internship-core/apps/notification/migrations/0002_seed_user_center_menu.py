"""数据迁移：写入用户中心菜单和权限数据"""
from django.db import migrations


def seed_user_center_menu(apps, schema_editor):
    Menu = apps.get_model("menu", "Menu")
    Permission = apps.get_model("permission", "Permission")
    MenuPermissionRelation = apps.get_model("permission", "MenuPermissionRelation")
    Role = apps.get_model("role", "Role")
    RoleMenuRelation = apps.get_model("role", "RoleMenuRelation")

    # ── 一级菜单：用户中心 ──
    uc_m, _ = Menu.objects.get_or_create(
        menu_name="用户中心",
        defaults={
            "parent": None, "menu_type": 0, "icon": "Avatar",
            "sort_order": 4, "path": "", "component": "",
            "permission": "", "visible": 1, "is_frame": 0, "status": 1,
        },
    )

    # ── 二级菜单：个人资料 ──
    profile_m, _ = Menu.objects.get_or_create(
        menu_name="个人资料", parent=uc_m,
        defaults={
            "menu_type": 1, "icon": "User", "sort_order": 0,
            "path": "/user-center/profile", "component": "user-center/ProfileView",
            "permission": "", "visible": 1, "is_frame": 0, "status": 1,
        },
    )

    # ── 二级菜单：消息通知 ──
    notif_m, _ = Menu.objects.get_or_create(
        menu_name="消息通知", parent=uc_m,
        defaults={
            "menu_type": 1, "icon": "Bell", "sort_order": 1,
            "path": "/user-center/notification", "component": "user-center/NotificationList",
            "permission": "", "visible": 1, "is_frame": 0, "status": 1,
        },
    )

    # 按钮权限
    btns = [
        ("删除通知", "notification:delete", 0, notif_m),
        ("全部已读", "notification:read-all", 1, notif_m),
        ("创建通知", "notification:create", 2, notif_m),
    ]
    for name, perm, sort, parent in btns:
        Menu.objects.get_or_create(
            menu_name=name, parent=parent,
            defaults={
                "menu_type": 2, "icon": "", "sort_order": sort,
                "path": "", "component": "", "permission": perm,
                "visible": 1, "is_frame": 0, "status": 1,
            },
        )

    # ── 权限 ──
    perm_map = {
        "notification:list": ("通知查询", notif_m),
        "notification:create": ("通知创建", notif_m),
        "notification:delete": ("通知删除", notif_m),
        "notification:read-all": ("全部已读", notif_m),
    }
    for key, (name, menu) in perm_map.items():
        perm, _ = Permission.objects.get_or_create(
            permission_key=key,
            defaults={"permission_name": name, "status": 1},
        )
        MenuPermissionRelation.objects.get_or_create(menu=menu, permission=perm)

    # ── 管理员角色关联 ──
    admin_role = Role.objects.filter(role_key="admin").first()
    if admin_role:
        for menu in Menu.objects.filter(
            menu_name__in=["用户中心", "个人资料", "消息通知", "删除通知", "全部已读", "创建通知"]
        ):
            RoleMenuRelation.objects.get_or_create(role=admin_role, menu=menu)


def reverse_seed(apps, schema_editor):
    Menu = apps.get_model("menu", "Menu")
    Permission = apps.get_model("permission", "Permission")

    perm_keys = ["notification:list", "notification:create", "notification:delete", "notification:read-all"]
    Permission.objects.filter(permission_key__in=perm_keys).delete()

    menu_names = ["用户中心", "个人资料", "消息通知", "删除通知", "全部已读", "创建通知"]
    Menu.objects.filter(menu_name__in=menu_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0001_initial"),
        ("menu", "0001_initial"),
        ("permission", "0001_initial"),
        ("role", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_user_center_menu, reverse_seed),
    ]
