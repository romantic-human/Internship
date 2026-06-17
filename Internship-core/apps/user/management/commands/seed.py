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
        self._m(role_m, "导出角色", 2, "", 3, permission="role:export")
        self._m(role_m, "导入角色", 2, "", 4, permission="role:import")

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

        dict_m = self._m(sys_m, "数据字典", 1, "Notebook", 8, "/system/dict", "system/dict/DictList")
        self._m(dict_m, "新增字典类型", 2, "", 0, permission="dict:type:add")
        self._m(dict_m, "编辑字典类型", 2, "", 1, permission="dict:type:edit")
        self._m(dict_m, "删除字典类型", 2, "", 2, permission="dict:type:delete")

        ai_model_m = self._m(sys_m, "AI 模型配置", 1, "Cpu", 9, "/system/ai-model", "system/ai-model/AIModelList")
        self._m(ai_model_m, "新增模型", 2, "", 0, permission="config:add")
        self._m(ai_model_m, "编辑模型", 2, "", 1, permission="config:edit")
        self._m(ai_model_m, "删除模型", 2, "", 2, permission="config:delete")

        # ── NL2SQL ─────────────────────────────────────────
        nl2sql_m = self._m(None, "自然语言查询", 0, "Connection", 2)

        query_m = self._m(nl2sql_m, "SQL 查询", 1, "Connection", 0, "/nl2sql/query", "nl2sql/QueryView")
        self._m(query_m, "执行查询", 2, "", 0, permission="nl2sql:query")
        self._m(query_m, "导出结果", 2, "", 1, permission="nl2sql:export")

        hist_m = self._m(nl2sql_m, "查询历史", 1, "Document", 1, "/nl2sql/history", "nl2sql/HistoryList")
        self._m(hist_m, "查询历史列表", 2, "", 0, permission="nl2sql:list")
        self._m(hist_m, "删除查询记录", 2, "", 1, permission="nl2sql:delete")

        ds_m = self._m(nl2sql_m, "数据源管理", 1, "Tools", 2, "/nl2sql/datasource", "nl2sql/DataSourceList")
        self._m(ds_m, "新增数据源", 2, "", 0, permission="nl2sql:add")
        self._m(ds_m, "编辑数据源", 2, "", 1, permission="nl2sql:edit")
        self._m(ds_m, "删除数据源", 2, "", 2, permission="nl2sql:delete")


        # --- RAG 知识库 ---
        rag_m = self._m(None, "知识库管理", 0, "Collection", 3)

        kb_m = self._m(rag_m, "知识库列表", 1, "FolderOpened", 0, "/rag/kb-list", "rag/KBList")
        self._m(kb_m, "新增知识库", 2, "", 0, permission="rag:add")
        self._m(kb_m, "编辑知识库", 2, "", 1, permission="rag:edit")
        self._m(kb_m, "删除知识库", 2, "", 2, permission="rag:delete")

        doc_m = self._m(rag_m, "文档管理", 1, "Document", 1, "/rag/kb-detail", "rag/KBDetail")
        self._m(doc_m, "上传文档", 2, "", 0, permission="rag:upload")
        self._m(doc_m, "删除文档", 2, "", 1, permission="rag:doc-delete")

        chat_m = self._m(rag_m, "AI 问答", 1, "ChatDotRound", 2, "/rag/chat", "rag/ChatView")
        self._m(chat_m, "发送问答", 2, "", 0, permission="rag:chat")

        self.stdout.write(f"  [OK] 菜单树: 系统管理 + NL2SQL + RAG知识库 + 学生管理 + 用户中心")

        # ── 3. 权限 ────────────────────────────────────────
        # 从数据库获取已有的父菜单（由 data migration 创建）
        stu_list_m = Menu.objects.filter(menu_name="学生列表").first()
        score_m = Menu.objects.filter(menu_name="成绩管理").first()
        notif_m = Menu.objects.filter(menu_name="消息通知").first()
        perm_map = {
            "user:list": ("用户查询", user_m), "user:add": ("用户新增", user_m),
            "user:edit": ("用户编辑", user_m), "user:delete": ("用户删除", user_m),
            "user:export": ("用户导出", user_m), "user:import": ("用户导入", user_m),
            "role:list": ("角色查询", role_m), "role:add": ("角色新增", role_m),
            "role:edit": ("角色编辑", role_m), "role:delete": ("角色删除", role_m),
            "role:assign": ("角色授权", role_m),
            "role:export": ("角色导出", role_m), "role:import": ("角色导入", role_m),
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
            "config:export": ("配置导出", config_m),
            # 数据字典
            "dict:type:list": ("字典类型查询", dict_m), "dict:type:add": ("字典类型新增", dict_m),
            "dict:type:edit": ("字典类型编辑", dict_m), "dict:type:delete": ("字典类型删除", dict_m),
            "dict:data:list": ("字典数据查询", dict_m), "dict:data:add": ("字典数据新增", dict_m),
            "dict:data:edit": ("字典数据编辑", dict_m), "dict:data:delete": ("字典数据删除", dict_m),
            # NL2SQL
            "nl2sql:query": ("查询执行", query_m), "nl2sql:export": ("查询导出", query_m),
            "nl2sql:list": ("历史查询", hist_m), "nl2sql:delete": ("历史删除", hist_m),
            "nl2sql:add": ("数据源新增", ds_m), "nl2sql:edit": ("数据源编辑", ds_m),
            "nl2sql:delete": ("数据源删除", ds_m),
            # RAG
            "rag:list": ("知识库查询", kb_m), "rag:add": ("知识库新增", kb_m),
            "rag:edit": ("知识库编辑", kb_m), "rag:delete": ("知识库删除", kb_m),
            "rag:upload": ("文档上传", doc_m), "rag:doc-delete": ("文档删除", doc_m),
            "rag:chat": ("AI问答", chat_m),
        }
        # 补充从 data migration 创建的菜单的权限
        if stu_list_m:
            perm_map["student:import"] = ("学生导入", stu_list_m)
        if score_m:
            perm_map["score:import"] = ("成绩导入", score_m)
        if notif_m:
            perm_map["notification:create"] = ("通知创建", notif_m)
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
        self.stdout.write(f"  [OK] test / test123")

        self.stdout.write(self.style.SUCCESS("\n种子数据创建完成!"))
        self.stdout.write("  管理员: admin / admin123  (全部权限)")
        self.stdout.write("  普通用户: test / test123  (暂无权限)")

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
