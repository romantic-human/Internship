from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.department.models import Department
from apps.log.models import OperationLog
from apps.menu.models import Menu
from apps.permission.models import Permission
from apps.role.models import Role
from apps.user.models import User
from utils.response import APIResponse


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    today = today_start.date()

    # 用户部门分布
    dept_distribution = list(
        Department.objects.annotate(user_count=Count("user")).values("dept_name", "user_count")
    )
    # 加入无部门用户
    no_dept_count = User.objects.filter(department__isnull=True).count()
    if no_dept_count > 0:
        dept_distribution.append({"dept_name": "未分配", "user_count": no_dept_count})

    # 近7天登录趋势
    login_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        login_trend.append({
            "date": day.isoformat(),
            "count": User.objects.filter(last_login__date=day).count(),
        })

    data = {
        "user_count": User.objects.count(),
        "role_count": Role.objects.count(),
        "menu_count": Menu.objects.count(),
        "permission_count": Permission.objects.count(),
        "department_count": Department.objects.count(),
        "today_login_count": User.objects.filter(last_login__date=today).count(),
        "log_today": OperationLog.objects.filter(create_time__gte=today_start).count(),
        "log_week": OperationLog.objects.filter(create_time__gte=week_start).count(),
        "log_month": OperationLog.objects.filter(create_time__gte=month_start).count(),
        "recent_logs": list(
            OperationLog.objects.order_by("-create_time")[:10].values(
                "username", "module", "operation", "ip", "execution_time", "create_time"
            )
        ),
        "dept_distribution": dept_distribution,
        "login_trend": login_trend,
    }
    return APIResponse.success(data=data)