"""学生模块序列化器"""
from rest_framework import serializers
from .models import StudentInfo, StudentScore


class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = "__all__"


class StudentScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_no = serializers.CharField(source="student.student_no", read_only=True)

    class Meta:
        model = StudentScore
        fields = "__all__"


class StudentScoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentScore
        fields = "__all__"
