"""学生模块序列化器"""
from rest_framework import serializers
from .models import StudentInfo, StudentScore


class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = [
            "id", "student_no", "name", "gender", "class_name", "major",
            "college", "phone", "email", "enrollment_year", "status",
            "remark", "create_time", "update_time",
        ]


class StudentScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_no = serializers.CharField(source="student.student_no", read_only=True)

    class Meta:
        model = StudentScore
        fields = [
            "id", "student", "student_name", "student_no", "course_name",
            "score", "semester", "credit", "remark", "create_time", "update_time",
        ]


class StudentScoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentScore
        fields = [
            "id", "student", "course_name", "score", "semester", "credit", "remark",
        ]
