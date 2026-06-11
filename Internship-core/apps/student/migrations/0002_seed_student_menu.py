"""数据迁移：写入学生中心菜单和权限数据"""
from django.db import migrations


def seed_student_menu(apps, schema_editor):
    Menu = apps.get_model("menu", "Menu")
    Permission = apps.get_model("permission", "Permission")
    MenuPermissionRelation = apps.get_model("permission", "MenuPermissionRelation")
    Role = apps.get_model("role", "Role")
    RoleMenuRelation = apps.get_model("role", "RoleMenuRelation")

    # ── 一级菜单：学生中心 ──
    student_m, _ = Menu.objects.get_or_create(
        menu_name="学生中心",
        defaults={
            "parent": None, "menu_type": 0, "icon": "Reading",
            "sort_order": 3, "path": "", "component": "",
            "permission": "", "visible": 1, "is_frame": 0, "status": 1,
        },
    )

    # ── 二级菜单：学生列表 ──
    stu_list_m, _ = Menu.objects.get_or_create(
        menu_name="学生列表", parent=student_m,
        defaults={
            "menu_type": 1, "icon": "User", "sort_order": 0,
            "path": "/student/list", "component": "student/StudentList",
            "permission": "", "visible": 1, "is_frame": 0, "status": 1,
        },
    )

    # 按钮权限
    btns_stu = [
        ("新增学生", "student:add", 0),
        ("编辑学生", "student:edit", 1),
        ("删除学生", "student:delete", 2),
    ]
    for name, perm, sort in btns_stu:
        btn, _ = Menu.objects.get_or_create(
            menu_name=name, parent=stu_list_m,
            defaults={
                "menu_type": 2, "icon": "", "sort_order": sort,
                "path": "", "component": "", "permission": perm,
                "visible": 1, "is_frame": 0, "status": 1,
            },
        )

    # ── 二级菜单：成绩管理 ──
    score_m, _ = Menu.objects.get_or_create(
        menu_name="成绩管理", parent=student_m,
        defaults={
            "menu_type": 1, "icon": "TrendCharts", "sort_order": 1,
            "path": "/student/score", "component": "student/ScoreList",
            "permission": "", "visible": 1, "is_frame": 0, "status": 1,
        },
    )

    btns_score = [
        ("新增成绩", "score:add", 0),
        ("编辑成绩", "score:edit", 1),
        ("删除成绩", "score:delete", 2),
    ]
    for name, perm, sort in btns_score:
        Menu.objects.get_or_create(
            menu_name=name, parent=score_m,
            defaults={
                "menu_type": 2, "icon": "", "sort_order": sort,
                "path": "", "component": "", "permission": perm,
                "visible": 1, "is_frame": 0, "status": 1,
            },
        )

    # ── 权限 ──
    perm_map = {
        "student:list": "学生查询", "student:add": "学生新增",
        "student:edit": "学生编辑", "student:delete": "学生删除",
        "student:export": "学生导出", "student:import": "学生导入",
        "score:list": "成绩查询", "score:add": "成绩新增",
        "score:edit": "成绩编辑", "score:delete": "成绩删除",
        "score:export": "成绩导出",
    }
    # 菜单→权限映射（用于关联）
    menu_perm_map = {
        "student:list": stu_list_m, "student:add": stu_list_m,
        "student:edit": stu_list_m, "student:delete": stu_list_m,
        "student:export": stu_list_m, "student:import": stu_list_m,
        "score:list": score_m, "score:add": score_m,
        "score:edit": score_m, "score:delete": score_m,
        "score:export": score_m,
    }
    for key, name in perm_map.items():
        perm, _ = Permission.objects.get_or_create(
            permission_key=key,
            defaults={"permission_name": name, "status": 1},
        )
        menu = menu_perm_map[key]
        MenuPermissionRelation.objects.get_or_create(menu=menu, permission=perm)

    # ── 管理员角色关联所有学生菜单 ──
    admin_role = Role.objects.filter(role_key="admin").first()
    if admin_role:
        for menu in Menu.objects.filter(
            menu_name__in=["学生中心", "学生列表", "成绩管理",
                           "新增学生", "编辑学生", "删除学生",
                           "新增成绩", "编辑成绩", "删除成绩"]
        ):
            RoleMenuRelation.objects.get_or_create(role=admin_role, menu=menu)


def reverse_seed(apps, schema_editor):
    """回滚时删除学生中心相关菜单和权限"""
    Menu = apps.get_model("menu", "Menu")
    Permission = apps.get_model("permission", "Permission")

    perm_keys = [
        "student:list", "student:add", "student:edit", "student:delete",
        "student:export", "student:import",
        "score:list", "score:add", "score:edit", "score:delete", "score:export",
    ]
    Permission.objects.filter(permission_key__in=perm_keys).delete()

    menu_names = [
        "学生中心", "学生列表", "成绩管理",
        "新增学生", "编辑学生", "删除学生",
        "新增成绩", "编辑成绩", "删除成绩",
    ]
    Menu.objects.filter(menu_name__in=menu_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("student", "0001_initial"),
        ("menu", "0001_initial"),
        ("permission", "0001_initial"),
        ("role", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_student_menu, reverse_seed),
    ]
