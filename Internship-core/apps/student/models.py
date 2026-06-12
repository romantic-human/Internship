"""学生中心模块"""
from django.db import models


class StudentInfo(models.Model):
    """学生信息表"""

    student_no = models.CharField(max_length=32, unique=True, verbose_name="学号")
    name = models.CharField(max_length=64, verbose_name="姓名")
    gender = models.SmallIntegerField(
        default=0,
        verbose_name="性别",
        help_text="0=未知 1=男 2=女",
    )
    class_name = models.CharField(max_length=64, blank=True, default="", verbose_name="班级")
    major = models.CharField(max_length=128, blank=True, default="", verbose_name="专业")
    college = models.CharField(max_length=128, blank=True, default="", verbose_name="学院")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    email = models.EmailField(max_length=128, blank=True, default="", verbose_name="邮箱")
    enrollment_year = models.IntegerField(null=True, blank=True, verbose_name="入学年份")
    status = models.SmallIntegerField(default=1, verbose_name="状态", help_text="0=休学 1=在读 2=毕业")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "student_info"
        verbose_name = "学生信息"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.student_no} - {self.name}"


class StudentScore(models.Model):
    """学生成绩表"""

    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name="学生",
    )
    course_name = models.CharField(max_length=128, verbose_name="课程名称")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="成绩")
    semester = models.CharField(max_length=32, verbose_name="学期", help_text="如 2025-2026-1")
    credit = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="学分")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "student_score"
        verbose_name = "学生成绩"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]
        unique_together = ("student", "course_name", "semester")

    def __str__(self):
        return f"{self.student.name} - {self.course_name} - {self.score}"
