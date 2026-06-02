"""
URL configuration for Internship project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API 文档
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    # 业务模块
    path("api/user/", include("apps.user.urls")),
    path("api/role/", include("apps.role.urls")),
    path("api/menu/", include("apps.menu.urls")),
    path("api/permission/", include("apps.permission.urls")),
    path("api/department/", include("apps.department.urls")),
    path("api/log/", include("apps.log.urls")),
    path("api/config/", include("apps.config_app.urls")),
]
