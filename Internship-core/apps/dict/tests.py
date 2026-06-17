"""字典模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import DictType, DictData
from apps.user.models import User


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
class DictAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="testadmin", password="Admin123")
        self.dict_type = DictType.objects.create(dict_name="性别", dict_type="gender", status=1)
        self.dict_data = DictData.objects.create(dict_type=self.dict_type, dict_label="男", dict_value="1", sort_order=1, status=1)
        resp = self.client.post("/api/user/login", {"username": "testadmin", "password": "Admin123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["data"]["access_token"]}')

    def test_create_dict_type(self):
        resp = self.client.post("/api/dict/type", {"dict_name": "状态", "dict_type": "status", "status": 1}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_dict_type_unique(self):
        resp = self.client.post("/api/dict/type", {"dict_name": "重复", "dict_type": "gender", "status": 1}, format="json")
        self.assertNotEqual(resp.data.get("code"), 200)

    def test_list_dict_types(self):
        resp = self.client.get("/api/dict/type")
        self.assertEqual(resp.data["code"], 200)

    def test_create_dict_data(self):
        resp = self.client.post("/api/dict/data", {
            "dict_type": self.dict_type.id, "dict_label": "女", "dict_value": "2", "sort_order": 2, "status": 1
        }, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_list_dict_data_by_type(self):
        resp = self.client.get(f"/api/dict/data/type/{self.dict_type.dict_type}")
        self.assertEqual(resp.data["code"], 200)
