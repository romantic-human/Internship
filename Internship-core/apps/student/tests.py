"""学生模块单元测试 — 5 个核心测试用例"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import StudentInfo, StudentScore
from apps.user.models import User


@override_settings(MIDDLEWARE=[
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
class StudentAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="testadmin", password="Admin123")
        self.student = StudentInfo.objects.create(
            student_no="2024001", name="张三", gender=1, status=1,
        )
        self.score = StudentScore.objects.create(
            student=self.student, course_name="高数", score=95, semester="2024-1",
        )
        resp = self.client.post("/api/user/login", {"username": "testadmin", "password": "Admin123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["data"]["access_token"]}')

    def test_create_student(self):
        resp = self.client.post("/api/student/info", {"student_no": "2024002", "name": "李四", "gender": 2, "status": 1}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_student_no_unique(self):
        resp = self.client.post("/api/student/info", {"student_no": "2024001", "name": "重复", "status": 1}, format="json")
        self.assertNotEqual(resp.data.get("code"), 200)

    def test_list_students(self):
        resp = self.client.get("/api/student/info")
        self.assertEqual(resp.data["code"], 200)

    def test_update_student(self):
        resp = self.client.put(f"/api/student/info/{self.student.id}", {"name": "张三丰"}, format="json")
        self.assertEqual(resp.data["code"], 200)

    def test_delete_student(self):
        resp = self.client.delete(f"/api/student/info/{self.student.id}")
        self.assertEqual(resp.data["code"], 200)
