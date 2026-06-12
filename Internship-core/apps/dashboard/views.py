from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.department.models import Department
from apps.log.models import OperationLog
from apps.menu.models import Menu
from apps.notification.models import Notification
from apps.permission.models import Permission
from apps.role.models import Role
from apps.student.models import StudentInfo
from apps.user.models import User
from utils.response import APIResponse


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """仪表盘统计数据 — 含缓存"""
    cache_key = "dashboard_stats"
    data = cache.get(cache_key)
    if data is not None:
        return APIResponse.success(data=data)

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    # 近 7 日登录趋势（从旧到新）
    login_trend = []
    for i in range(6, -1, -1):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = OperationLog.objects.filter(
            operation__icontains="登录",
            create_time__gte=day_start,
            create_time__lt=day_end,
        ).count()
        login_trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})

    # 部门分布（每个部门的用户数）
    dept_distribution = []
    for dept in Department.objects.all():
        user_count = User.objects.filter(department=dept).count()
        if user_count > 0:
            dept_distribution.append({"dept_name": dept.dept_name, "user_count": user_count})
    dept_distribution.sort(key=lambda x: x["user_count"], reverse=True)

    data = {
        "user_count": User.objects.count(),
        "role_count": Role.objects.count(),
        "menu_count": Menu.objects.count(),
        "permission_count": Permission.objects.count(),
        "department_count": Department.objects.count(),
        "student_count": StudentInfo.objects.count(),
        "notification_count": Notification.objects.filter(is_read=False).count(),
        "today_login_count": OperationLog.objects.filter(
            create_time__gte=today_start,
            operation__icontains="登录",
        ).count(),
        "log_today": OperationLog.objects.filter(create_time__gte=today_start).count(),
        "log_week": OperationLog.objects.filter(create_time__gte=week_start).count(),
        "log_month": OperationLog.objects.filter(create_time__gte=month_start).count(),
        "dept_distribution": dept_distribution,
        "login_trend": login_trend,
        "recent_logs": [
            {
                "username": log["username"],
                "module": log["module"],
                "operation": log["operation"],
                "ip": log["ip"],
                "execution_time": log["execution_time"],
                "create_time": log["create_time"].strftime("%Y-%m-%d %H:%M:%S"),
            }
            for log in OperationLog.objects.order_by("-create_time")[:10].values(
                "username", "module", "operation", "ip", "execution_time", "create_time"
            )
        ],
    }

    cache.set(cache_key, data, timeout=60)
    return APIResponse.success(data=data)
