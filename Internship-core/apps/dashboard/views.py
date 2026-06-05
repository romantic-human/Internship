from datetime import datetime, timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.department.models import Department
from apps.log.models import OperationLog
from apps.menu.models import Menu
from apps.permission.models import Permission
from apps.role.models import Role
from apps.user.models import User, UserRoleRelation
from utils.response import APIResponse


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    today_start = timezone.make_aware(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    data = {
        "user_count": User.objects.count(),
        "role_count": Role.objects.count(),
        "menu_count": Menu.objects.count(),
        "permission_count": Permission.objects.count(),
        "department_count": Department.objects.count(),
        "log_today": OperationLog.objects.filter(create_time__gte=today_start).count(),
        "log_week": OperationLog.objects.filter(create_time__gte=week_start).count(),
        "log_month": OperationLog.objects.filter(create_time__gte=month_start).count(),
        "recent_logs": list(
            OperationLog.objects.order_by("-create_time")[:10].values(
                "username", "module", "operation", "ip", "execution_time", "create_time"
            )
        ),
    }
    return APIResponse.success(data=data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_trend(request):
    today = timezone.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    log_trend = []
    for d in dates:
        day_start = timezone.make_aware(datetime(d.year, d.month, d.day))
        day_end = day_start + timedelta(days=1)
        log_trend.append({
            "date": d.strftime("%Y-%m-%d"),
            "count": OperationLog.objects.filter(create_time__gte=day_start, create_time__lt=day_end).count(),
        })

    role_dist = list(
        Role.objects.annotate(user_count=Count("userrolerelation")).values("role_name", "user_count")
    )

    return APIResponse.success(data={
        "log_trend": log_trend,
        "role_distribution": role_dist,
    })