"""菜单模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Menu
from apps.user.models import User


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
class MenuAPITests(TestCase):
    """菜单模块 API 测试（禁用操作日志中间件）"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="testadmin", password="Admin123",
        )
        self.parent_menu = Menu.objects.create(
            menu_name="测试管理", menu_type=0, icon="Setting",
            sort_order=1, status=1,
        )
        self.child_menu = Menu.objects.create(
            menu_name="测试列表", menu_type=1, path="/test/list",
            component="test/TestList", parent=self.parent_menu,
            sort_order=1, status=1,
        )
        resp = self.client.post("/api/user/login", {
            "username": "testadmin", "password": "Admin123",
        }, format="json")
        self.token = resp.data["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_menu(self):
        resp = self.client.post("/api/menu/", {
            "menu_name": "新菜单", "menu_type": 1,
            "path": "/new", "component": "New", "sort_order": 2, "status": 1,
        }, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_menu_tree(self):
        resp = self.client.get("/api/menu/tree")
        self.assertEqual(resp.data["code"], 200)

    def test_update_menu(self):
        resp = self.client.put(f"/api/menu/{self.child_menu.id}", {
            "menu_name": "修改后", "path": "/updated",
        }, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_delete_menu(self):
        resp = self.client.delete(f"/api/menu/{self.child_menu.id}")
        self.assertEqual(resp.data["code"], 200)
        self.assertFalse(Menu.objects.filter(id=self.child_menu.id).exists())

    def test_batch_delete_menus(self):
        m = Menu.objects.create(menu_name="待删", menu_type=1, path="/d", component="D", status=1)
        resp = self.client.delete("/api/menu/batch", {"ids": [m.id]}, format="json")
        self.assertEqual(resp.data["code"], 200)
