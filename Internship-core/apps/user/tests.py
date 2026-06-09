"""用户模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase
from rest_framework.test import APIClient
from .models import User, UserRoleRelation
from apps.role.models import Role


class UserAPITests(TestCase):
    """用户模块 API 测试"""

    def setUp(self):
        self.client = APIClient()
        # 创建管理员用户（超级管理员，权限校验直接放行）
        self.admin = User.objects.create_superuser(
            username="testadmin", password="Admin123",
            nickname="测试管理员",
        )
        # 创建普通用户
        self.user = User.objects.create_user(
            username="testuser", password="User1234",
            nickname="测试用户", email="test@example.com",
            telephone="13800000001", status=1,
        )
        # 登录获取 token
        resp = self.client.post("/api/user/login", {
            "username": "testadmin", "password": "Admin123",
        }, format="json")
        self.token = resp.data.get("data", {}).get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    # ── 测试 1: 用户登录（正确密码 vs 错误密码）────────────────────
    def test_login_success_and_fail(self):
        client = APIClient()
        # 正确密码
        resp = client.post("/api/user/login", {
            "username": "testuser", "password": "User1234",
        }, format="json")
        self.assertEqual(resp.data["code"], 200)
        self.assertIn("access_token", resp.data["data"])

        # 错误密码
        resp = client.post("/api/user/login", {
            "username": "testuser", "password": "WrongPass",
        }, format="json")
        self.assertNotEqual(resp.data["code"], 200)

    # ── 测试 2: 创建用户 ─────────────────────────────────────────
    def test_create_user(self):
        resp = self.client.post("/api/user/", {
            "username": "newuser",
            "nickname": "新用户",
            "email": "new@example.com",
            "telephone": "13900000001",
            "status": 1,
        }, format="json")
        self.assertEqual(resp.data["code"], 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    # ── 测试 3: 用户名唯一性检查 ─────────────────────────────────
    def test_check_unique(self):
        # 已存在的用户名
        resp = self.client.get("/api/user/check-unique", {
            "field": "username", "value": "testuser",
        })
        self.assertEqual(resp.data["code"], 200)
        self.assertFalse(resp.data["data"]["unique"])

        # 不存在的用户名
        resp = self.client.get("/api/user/check-unique", {
            "field": "username", "value": "nonexistent",
        })
        self.assertTrue(resp.data["data"]["unique"])

        # 编辑时排除自身
        resp = self.client.get("/api/user/check-unique", {
            "field": "username", "value": "testuser",
            "exclude_id": self.user.id,
        })
        self.assertTrue(resp.data["data"]["unique"])

    # ── 测试 4: 密码强度校验 ─────────────────────────────────────
    def test_password_strength_validation(self):
        client = APIClient()
        # 用普通用户登录（需先设为超管以通过权限校验）
        self.user.is_superuser = True
        self.user.save()
        resp = client.post("/api/user/login", {
            "username": "testuser", "password": "User1234",
        }, format="json")
        token = resp.data["data"]["access_token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # 弱密码（纯数字）
        resp = client.put("/api/user/update-password", {
            "old_password": "User1234",
            "new_password": "12345678",
        }, format="json")
        self.assertEqual(resp.status_code, 400)

        # 弱密码（纯字母）
        resp = client.put("/api/user/update-password", {
            "old_password": "User1234",
            "new_password": "abcdefgh",
        }, format="json")
        self.assertEqual(resp.status_code, 400)

        # 强密码（数字+字母）
        resp = client.put("/api/user/update-password", {
            "old_password": "User1234",
            "new_password": "NewPass123",
        }, format="json")
        self.assertEqual(resp.data["code"], 200)

    # ── 测试 5: 删除用户 ─────────────────────────────────────────
    def test_delete_user(self):
        resp = self.client.delete(f"/api/user/{self.user.id}")
        self.assertEqual(resp.data["code"], 200)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

        # 删除不存在的用户
        resp = self.client.delete("/api/user/99999")
        self.assertEqual(resp.status_code, 404)
