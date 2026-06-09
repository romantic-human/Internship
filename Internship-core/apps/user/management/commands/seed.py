"""
种子数据生成命令
用法: python manage.py seed

所有组员执行此命令后即可获得统一的测试数据。
"""
from django.core.management.base import BaseCommand
from apps.user.models import User, UserRoleRelation
from apps.role.models import Role, RoleMenuRelation
from apps.menu.models import Menu
from apps.permission.models import Permission, MenuPermissionRelation
from apps.department.models import Department


class Command(BaseCommand):
    help = "初始化测试数据：用户、部门、角色、菜单、权限"

    def handle(self, *args, **options):
        self.stdout.write("开始创建测试数据...\n")

        # ── 1. 部门 ────────────────────────────────────────
        root, _ = Department.objects.get_or_create(
            dept_name="总公司", defaults={"sort_order": 0, "status": 1},
        )
        self.stdout.write(f"  [OK] 总公司")

        tech, _ = Department.objects.get_or_create(
            dept_name="技术部", defaults={"parent": root, "sort_order": 10, "status": 1},
        )
        self.stdout.write(f"  [OK] 技术部")

        hr, _ = Department.objects.get_or_create(
            dept_name="人事部", defaults={"parent": root, "sort_order": 20, "status": 1},
        )
        self.stdout.write(f"  [OK] 人事部")

        finance, _ = Department.objects.get_or_create(
            dept_name="财务部", defaults={"parent": root, "sort_order": 30, "status": 1},
        )
        self.stdout.write(f"  [OK] 财务部")

        frontend, _ = Department.objects.get_or_create(
            dept_name="前端组", defaults={"parent": tech, "sort_order": 11, "status": 1},
        )
        self.stdout.write(f"  [OK] 前端组")

        backend, _ = Department.objects.get_or_create(
            dept_name="后端组", defaults={"parent": tech, "sort_order": 12, "status": 1},
        )
        self.stdout.write(f"  [OK] 后端组")

        # ── 2. 菜单树 ──────────────────────────────────────
        sys_m = self._m(None, "系统管理", 0, "Setting", 0)

        user_m = self._m(sys_m, "用户管理", 1, "User", 1, "/system/user", "system/user/UserList")
        self._m(user_m, "新增用户", 2, "", 0, permission="user:add")
        self._m(user_m, "编辑用户", 2, "", 1, permission="user:edit")
        self._m(user_m, "删除用户", 2, "", 2, permission="user:delete")

        role_m = self._m(sys_m, "角色管理", 1, "UserFilled", 2, "/system/role", "system/role/RoleList")
        self._m(role_m, "新增角色", 2, "", 0, permission="role:add")
        self._m(role_m, "编辑角色", 2, "", 1, permission="role:edit")
        self._m(role_m, "删除角色", 2, "", 2, permission="role:delete")

        menu_m = self._m(sys_m, "菜单管理", 1, "Menu", 3, "/system/menu", "system/menu/MenuTree")
        self._m(menu_m, "新增菜单", 2, "", 0, permission="menu:add")
        self._m(menu_m, "编辑菜单", 2, "", 1, permission="menu:edit")
        self._m(menu_m, "删除菜单", 2, "", 2, permission="menu:delete")

        perm_m = self._m(sys_m, "权限管理", 1, "Key", 4, "/system/permission", "system/permission/PermissionList")
        self._m(perm_m, "新增权限", 2, "", 0, permission="permission:add")
        self._m(perm_m, "编辑权限", 2, "", 1, permission="permission:edit")
        self._m(perm_m, "删除权限", 2, "", 2, permission="permission:delete")

        dept_m = self._m(sys_m, "部门管理", 1, "Office", 5, "/system/department", "system/department/DeptTree")
        self._m(dept_m, "新增部门", 2, "", 0, permission="dept:add")
        self._m(dept_m, "编辑部门", 2, "", 1, permission="dept:edit")
        self._m(dept_m, "删除部门", 2, "", 2, permission="dept:delete")

        log_m = self._m(sys_m, "操作日志", 1, "Document", 6, "/system/log", "system/log/LogList")
        config_m = self._m(sys_m, "系统配置", 1, "Tools", 7, "/system/config", "system/config/ConfigList")

        # ── RAG 知识库 ──────────────────────────────────────
        rag_m = self._m(None, "RAG知识库", 0, "Document", 10)
        kb_list_m = self._m(rag_m, "知识库列表", 1, "Document", 0, "/rag/kb-list", "rag/KBList")
        self._m(kb_list_m, "新增知识库", 2, "", 0, permission="rag:kb:add")
        self._m(kb_list_m, "编辑知识库", 2, "", 1, permission="rag:kb:edit")
        self._m(kb_list_m, "删除知识库", 2, "", 2, permission="rag:kb:delete")

        kb_detail_m = self._m(rag_m, "文档管理", 1, "Document", 1, "/rag/kb-detail", "rag/KBDetail")
        self._m(kb_detail_m, "上传文档", 2, "", 0, permission="rag:doc:upload")
        self._m(kb_detail_m, "删除文档", 2, "", 1, permission="rag:doc:delete")

        chat_m = self._m(rag_m, "AI问答", 1, "Document", 2, "/rag/chat", "rag/ChatView")
        self._m(chat_m, "AI问答", 2, "", 0, permission="rag:chat")

        self.stdout.write(f"  [OK] RAG知识库: 3 个菜单 + 6 个按钮")

        self.stdout.write(f"  [OK] 菜单树: 8 个一级菜单 + 18 个按钮")

        # ── 3. 权限 ────────────────────────────────────────
        perm_map = {
            "user:list": ("用户查询", user_m), "user:add": ("用户新增", user_m),
            "user:edit": ("用户编辑", user_m), "user:delete": ("用户删除", user_m),
            "user:export": ("用户导出", user_m), "user:import": ("用户导入", user_m),
            "role:list": ("角色查询", role_m), "role:add": ("角色新增", role_m),
            "role:edit": ("角色编辑", role_m), "role:delete": ("角色删除", role_m),
            "role:assign": ("角色授权", role_m),
            "menu:list": ("菜单查询", menu_m), "menu:add": ("菜单新增", menu_m),
            "menu:edit": ("菜单编辑", menu_m), "menu:delete": ("菜单删除", menu_m),
            "permission:list": ("权限查询", perm_m), "permission:add": ("权限新增", perm_m),
            "permission:edit": ("权限编辑", perm_m), "permission:delete": ("权限删除", perm_m),
            "dept:list": ("部门查询", dept_m), "dept:add": ("部门新增", dept_m),
            "dept:edit": ("部门编辑", dept_m), "dept:delete": ("部门删除", dept_m),
            "log:list": ("日志查询", log_m), "log:delete": ("日志清空", log_m),
            "log:export": ("日志导出", log_m),
            "config:list": ("配置查询", config_m), "config:add": ("配置新增", config_m),
            "config:edit": ("配置编辑", config_m), "config:delete": ("配置删除", config_m),
            # RAG 知识库
            "rag:kb:add": ("新增知识库", kb_list_m), "rag:kb:edit": ("编辑知识库", kb_list_m),
            "rag:kb:delete": ("删除知识库", kb_list_m),
            "rag:doc:upload": ("上传文档", kb_detail_m), "rag:doc:delete": ("删除文档", kb_detail_m),
            "rag:chat": ("AI问答", chat_m),
        }
        for key, (name, menu) in perm_map.items():
            perm, _ = Permission.objects.get_or_create(
                permission_key=key, defaults={"permission_name": name, "status": 1},
            )
            MenuPermissionRelation.objects.get_or_create(menu=menu, permission=perm)

        self.stdout.write(f"  [OK] {len(perm_map)} 个权限")

        # ── 4. 角色 ────────────────────────────────────────
        admin_role, _ = Role.objects.get_or_create(
            role_key="admin", defaults={"role_name": "管理员", "role_sort": 0, "status": 1},
        )
        user_role, _ = Role.objects.get_or_create(
            role_key="user", defaults={"role_name": "普通用户", "role_sort": 10, "status": 1},
        )
        self.stdout.write(f"  [OK] 管理员 + 普通用户")

        # 管理员拥有所有菜单
        for mid in Menu.objects.values_list("id", flat=True):
            RoleMenuRelation.objects.get_or_create(role=admin_role, menu_id=mid)
        self.stdout.write(f"  [OK] 管理员拥有全部菜单权限")

        # 普通用户拥有只读菜单权限
        readonly_keys = ["dept:list", "config:list", "log:list", "user:list", "role:list", "menu:list", "permission:list"]
        for pk in readonly_keys:
            perm = Permission.objects.filter(permission_key=pk).first()
            if perm:
                mids = MenuPermissionRelation.objects.filter(permission=perm).values_list("menu_id", flat=True)
                for mid in mids:
                    RoleMenuRelation.objects.get_or_create(role=user_role, menu_id=mid)
        self.stdout.write(f"  [OK] 普通用户拥有只读权限")

        # ── 5. 用户 ────────────────────────────────────────
        admin = User.objects.filter(username="admin").first()
        if not admin:
            admin = User(username="admin", nickname="系统管理员", is_superuser=True, status=1)
            admin.set_password("admin123")
            admin.save()
        # 确保 admin 用户关联到 admin 角色
        UserRoleRelation.objects.get_or_create(user=admin, role=admin_role)
        self.stdout.write(f"  [OK] admin / admin123")

        test = User.objects.filter(username="test").first()
        if not test:
            test = User(username="test", nickname="测试用户", is_superuser=False, status=1, department=tech)
            test.set_password("test123")
            test.save()
        UserRoleRelation.objects.get_or_create(user=test, role=user_role)
        self.stdout.write(f"  [OK] test / test123")

        demo_data = [
            ("zhangsan", "张三", tech, "zhang123"),
            ("lisi", "李四", tech, "lisi123"),
            ("wangwu", "王五", hr, "wang123"),
            ("zhaoliu", "赵六", finance, "zhao123"),
        ]
        for uname, nickname, dept, pwd in demo_data:
            u = User.objects.filter(username=uname).first()
            if not u:
                u = User(username=uname, nickname=nickname, is_superuser=False, status=1, department=dept)
                u.set_password(pwd)
                u.save()
            UserRoleRelation.objects.get_or_create(user=u, role=user_role)
            self.stdout.write(f"  [OK] {uname} / {pwd}")

        self.stdout.write(self.style.SUCCESS("\n种子数据创建完成!"))
        self.stdout.write("  管理员: admin / admin123  (全部权限)")
        self.stdout.write("  普通用户: test / test123  (只读权限)")
        self.stdout.write("  更多用户: zhangsan/lisi/wangwu/zhaoliu (密码见上)")

    def _m(self, parent, name, mtype, icon, sort, path="", component="", permission=""):
        """创建菜单项"""
        menu, created = Menu.objects.get_or_create(
            menu_name=name,
            defaults={
                "parent": parent, "menu_type": mtype, "icon": icon,
                "sort_order": sort, "path": path, "component": component,
                "permission": permission, "visible": 1, "is_frame": 0, "status": 1,
            },
        )
        return menu