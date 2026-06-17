"""NL2SQL 模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import DataSource, QueryHistory
from apps.user.models import User


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
class NL2SQLAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="testadmin", password="Admin123")
        self.datasource = DataSource.objects.create(
            name="测试数据源", db_type="mysql", host="127.0.0.1", port=3306,
            db_name="test_db", username="root", status=1, created_by=self.admin,
        )
        self.datasource.set_password("test_pass")
        self.datasource.save()
        self.history = QueryHistory.objects.create(
            user=self.admin, datasource=self.datasource,
            question="查询所有用户", generated_sql="SELECT * FROM users",
            execution_time=0.5, result_count=10, status=1,
        )
        resp = self.client.post("/api/user/login", {"username": "testadmin", "password": "Admin123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["data"]["access_token"]}')

    def test_create_datasource(self):
        resp = self.client.post("/api/nl2sql/datasource", {
            "name": "新数据源", "db_type": "mysql", "host": "192.168.1.1",
            "port": 3306, "db_name": "new_db", "username": "root", "password": "pass", "status": 1,
        }, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_datasource_password_encrypted(self):
        ds = DataSource.objects.get(id=self.datasource.id)
        self.assertNotEqual(ds.password_enc, "test_pass")
        self.assertEqual(ds.get_password(), "test_pass")

    def test_list_datasources(self):
        resp = self.client.get("/api/nl2sql/datasource")
        self.assertEqual(resp.data["code"], 200)

    def test_list_query_history(self):
        resp = self.client.get("/api/nl2sql/history")
        self.assertEqual(resp.data["code"], 200)

    def test_delete_query_history(self):
        resp = self.client.delete(f"/api/nl2sql/history/{self.history.id}")
        self.assertEqual(resp.data["code"], 200)
