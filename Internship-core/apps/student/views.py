"""学生中心视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import StudentInfo, StudentScore
from .serializers import (
    StudentInfoSerializer,
    StudentScoreSerializer,
    StudentScoreCreateSerializer,
)
import csv
from django.http import HttpResponse


class StudentInfoViewSet(viewsets.ModelViewSet):
    """学生信息管理 — /api/student/info/"""

    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_key = "student:list"
    permission_key_map = {
        "create": "student:add",
        "update": "student:edit",
        "destroy": "student:delete",
        "batch": "student:delete",
        "status": "student:edit",
        "export": "student:export",
        "import": "student:import",
    }

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission()]

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get("name")
        student_no = self.request.query_params.get("student_no")
        class_name = self.request.query_params.get("class_name")
        status_val = self.request.query_params.get("status")
        if name:
            qs = qs.filter(name__icontains=name)
        if student_no:
            qs = qs.filter(student_no__icontains=student_no)
        if class_name:
            qs = qs.filter(class_name__icontains=class_name)
        if status_val is not None and status_val != "":
            qs = qs.filter(status=int(status_val))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="新增成功")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if StudentScore.objects.filter(student=instance).exists():
            return APIResponse.error(message="该学生存在关联成绩记录，无法删除")
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        """批量删除学生"""
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        if StudentScore.objects.filter(student_id__in=ids).exists():
            return APIResponse.error(message="部分学生存在关联成绩记录，无法批量删除")
        StudentInfo.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        """修改学生状态"""
        instance = self.get_object()
        status_val = request.data.get("status")
        if status_val not in (0, 1, 2):
            return APIResponse.error(message="状态值无效")
        instance.status = status_val
        instance.save(update_fields=["status", "update_time"])
        return APIResponse.success(message="状态更新成功")

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        """导出学生列表"""
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(["学号", "姓名", "性别", "班级", "专业", "学院", "手机号", "邮箱", "入学年份", "状态", "创建时间"])
        students = self.get_queryset()
        gender_map = {0: "未知", 1: "男", 2: "女"}
        status_map = {0: "休学", 1: "在读", 2: "毕业"}
        for s in students:
            writer.writerow([
                s.student_no, s.name, gender_map.get(s.gender, "未知"),
                s.class_name, s.major, s.college, s.phone, s.email,
                s.enrollment_year, status_map.get(s.status, "未知"), s.create_time,
            ])
        return response


class StudentScoreViewSet(viewsets.ModelViewSet):
    """学生成绩管理 — /api/student/score/"""

    queryset = StudentScore.objects.select_related("student").all()
    serializer_class = StudentScoreSerializer
    permission_key = "score:list"
    permission_key_map = {
        "create": "score:add",
        "update": "score:edit",
        "destroy": "score:delete",
        "batch": "score:delete",
        "export": "score:export",
    }

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return StudentScoreCreateSerializer
        return StudentScoreSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get("student_id")
        course_name = self.request.query_params.get("course_name")
        semester = self.request.query_params.get("semester")
        if student_id:
            qs = qs.filter(student_id=int(student_id))
        if course_name:
            qs = qs.filter(course_name__icontains=course_name)
        if semester:
            qs = qs.filter(semester=semester)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="新增成功")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        """批量删除成绩"""
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        StudentScore.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        """导出成绩列表"""
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="scores.csv"'
        writer = csv.writer(response)
        writer.writerow(["学号", "姓名", "课程名称", "成绩", "学分", "学期", "创建时间"])
        scores = self.get_queryset()
        for s in scores:
            writer.writerow([
                s.student.student_no, s.student.name, s.course_name,
                s.score, s.credit, s.semester, s.create_time,
            ])
        return response
