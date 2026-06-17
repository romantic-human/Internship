"""权限模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Permission
from apps.user.models import User


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
class PermissionAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="testadmin", password="Admin123")
        self.perm = Permission.objects.create(permission_name="用户查询", permission_key="user:list", sort_order=1, status=1)
        resp = self.client.post("/api/user/login", {"username": "testadmin", "password": "Admin123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["data"]["access_token"]}')

    def test_create_permission(self):
        resp = self.client.post("/api/permission/", {"permission_name": "新增", "permission_key": "user:add", "sort_order": 2, "status": 1}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_permission_key_unique(self):
        resp = self.client.post("/api/permission/", {"permission_name": "重复", "permission_key": "user:list", "sort_order": 99, "status": 1}, format="json")
        self.assertNotEqual(resp.data.get("code"), 200)

    def test_list_permissions(self):
        resp = self.client.get("/api/permission/")
        self.assertEqual(resp.data["code"], 200)

    def test_update_permission(self):
        resp = self.client.put(f"/api/permission/{self.perm.id}", {"permission_name": "修改后"}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_delete_permission(self):
        resp = self.client.delete(f"/api/permission/{self.perm.id}")
        self.assertEqual(resp.data["code"], 200)
