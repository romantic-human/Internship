"""部门模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Department
from apps.user.models import User


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
class DepartmentAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="testadmin", password="Admin123")
        self.dept = Department.objects.create(dept_name="总公司", leader="张三", sort_order=1, status=1)
        self.child = Department.objects.create(dept_name="技术部", parent=self.dept, sort_order=1, status=1)
        resp = self.client.post("/api/user/login", {"username": "testadmin", "password": "Admin123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["data"]["access_token"]}')

    def test_create_department(self):
        resp = self.client.post("/api/department/", {"dept_name": "市场部", "sort_order": 2, "status": 1}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_department_tree(self):
        resp = self.client.get("/api/department/tree")
        self.assertEqual(resp.data["code"], 200)

    def test_update_department(self):
        resp = self.client.put(f"/api/department/{self.child.id}", {"dept_name": "研发部"}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_delete_department(self):
        resp = self.client.delete(f"/api/department/{self.child.id}")
        self.assertEqual(resp.data["code"], 200)

    def test_batch_delete_departments(self):
        d = Department.objects.create(dept_name="待删", sort_order=99, status=1)
        resp = self.client.post("/api/department/batch-delete", {"ids": [d.id]}, format="json")
        self.assertEqual(resp.data["code"], 200)
