"""角色模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Role, RoleMenuRelation
from apps.user.models import User, UserRoleRelation
from apps.menu.models import Menu


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])


class RoleAPITests(TestCase):
    """角色模块 API 测试"""

    def setUp(self):
        self.client = APIClient()
        # 创建管理员（超级管理员，权限校验直接放行）
        self.admin = User.objects.create_superuser(
            username="testadmin", password="Admin123",
        )
        # 创建测试角色
        self.role = Role.objects.create(
            role_name="测试角色", role_key="test_role",
            role_sort=1, status=1, remark="测试用角色",
        )
        # 创建普通用户
        self.user = User.objects.create_user(
            username="testuser", password="User1234", status=1,
        )
        # 登录
        resp = self.client.post("/api/user/login", {
            "username": "testadmin", "password": "Admin123",
        }, format="json")
        self.token = resp.data["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    # ── 测试 1: 创建角色 ─────────────────────────────────────────
    def test_create_role(self):
        resp = self.client.post("/api/role/", {
            "role_name": "新角色",
            "role_key": "new_role",
            "role_sort": 2,
            "status": 1,
            "remark": "新增角色测试",
        }, format="json")
        self.assertEqual(resp.data["code"], 200)
        self.assertTrue(Role.objects.filter(role_key="new_role").exists())

    # ── 测试 2: 角色列表查询 ─────────────────────────────────────
    def test_list_roles(self):
        resp = self.client.get("/api/role/", {"page": 1, "pageSize": 10})
        self.assertEqual(resp.data["code"], 200)

    # ── 测试 3: 删除角色保护（关联用户时不可删除）──────────────
    def test_delete_role_protection(self):
        # 创建用户-角色关联
        UserRoleRelation.objects.create(user=self.user, role=self.role)

        # 尝试删除有关联用户的角色
        resp = self.client.delete(f"/api/role/{self.role.id}")
        self.assertEqual(resp.data["code"], 400)  # 返回错误
        self.assertIn("关联用户", resp.data.get("message", ""))
        # 角色仍然存在
        self.assertTrue(Role.objects.filter(id=self.role.id).exists())

        # 删除关联后应该可以删除
        UserRoleRelation.objects.filter(role=self.role).delete()
        resp = self.client.delete(f"/api/role/{self.role.id}")
        self.assertEqual(resp.data["code"], 200)
        self.assertFalse(Role.objects.filter(id=self.role.id).exists())

    # ── 测试 4: 批量排序 ─────────────────────────────────────────
    def test_batch_sort(self):
        role2 = Role.objects.create(role_name="角色B", role_key="role_b", role_sort=2)
        role3 = Role.objects.create(role_name="角色C", role_key="role_c", role_sort=3)

        resp = self.client.post("/api/role/batch-sort", [
            {"id": self.role.id, "sortOrder": 10},
            {"id": role2.id, "sortOrder": 20},
            {"id": role3.id, "sortOrder": 30},
        ], format="json")
        self.assertEqual(resp.data["code"], 200)

        # 验证排序已更新
        self.role.refresh_from_db()
        role2.refresh_from_db()
        role3.refresh_from_db()
        self.assertEqual(self.role.role_sort, 10)
        self.assertEqual(role2.role_sort, 20)
        self.assertEqual(role3.role_sort, 30)

    # ── 测试 5: 分配菜单权限 ─────────────────────────────────────
    def test_assign_menus(self):
        # 创建测试菜单
        menu1 = Menu.objects.create(
            menu_name="测试菜单1", menu_type=1, path="/test1",
            component="test1", sort_order=1, status=1,
        )
        menu2 = Menu.objects.create(
            menu_name="测试菜单2", menu_type=1, path="/test2",
            component="test2", sort_order=2, status=1,
        )

        # 分配菜单
        resp = self.client.put(f"/api/role/{self.role.id}/menus", {
            "menu_ids": [menu1.id, menu2.id],
        }, format="json")
        self.assertEqual(resp.data["code"], 200)
        self.assertEqual(
            RoleMenuRelation.objects.filter(role=self.role).count(), 2
        )

        # 重新分配（替换原有菜单）
        resp = self.client.put(f"/api/role/{self.role.id}/menus", {
            "menu_ids": [menu1.id],
        }, format="json")
        self.assertEqual(resp.data["code"], 200)
        self.assertEqual(
            RoleMenuRelation.objects.filter(role=self.role).count(), 1
        )

        # 获取菜单
        resp = self.client.get(f"/api/role/{self.role.id}/menus")
        self.assertEqual(resp.data["code"], 200)
        self.assertEqual(len(resp.data["data"]), 1)
