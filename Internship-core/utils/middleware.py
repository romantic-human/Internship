import json
import time
import re
from django.utils.deprecation import MiddlewareMixin
from apps.log.models import OperationLog


SKIP_PATHS = (
    re.compile(r"^/admin/"),
    re.compile(r"^/api/schema"),
    re.compile(r"^/api/docs"),
    re.compile(r"^/static/"),
)

SKIP_METHODS = ("GET",)

SENSITIVE_PATTERNS = re.compile(r"password|token|secret|key|authorization", re.IGNORECASE)


def sanitize_params(params):
    if isinstance(params, dict):
        result = {}
        for k, v in params.items():
            if SENSITIVE_PATTERNS.search(k):
                result[k] = "******"
            else:
                result[k] = sanitize_params(v)
        return result
    if isinstance(params, list):
        return [sanitize_params(item) for item in params]
    return params


class OperationLogMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        request._log_start_time = time.time()
        try:
            request._log_body = json.loads(request.body) if request.body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            request._log_body = {}
        return None

    def process_response(self, request, response):
        path = request.path
        if any(p.match(path) for p in SKIP_PATHS):
            return response
        if request.method in SKIP_METHODS:
            return response

        duration = int((time.time() - getattr(request, "_log_start_time", time.time())) * 1000)

        user = getattr(request, "user", None)
        user_id = user.id if user and user.is_authenticated else None
        username = user.username if user and user.is_authenticated else ""

        parts = [p for p in path.split("/") if p]
        module = parts[1] if len(parts) > 1 else ""

        operation_map = {
            "POST": "新增",
            "PUT": "更新",
            "DELETE": "删除",
        }
        operation = operation_map.get(request.method, request.method)

        request_params = ""
        if request.method in ("POST", "PUT"):
            body = getattr(request, "_log_body", {})
            request_params = json.dumps(sanitize_params(body), ensure_ascii=False)

        response_body = ""
        if hasattr(response, "data"):
            try:
                response_body = json.dumps(response.data, ensure_ascii=False)
            except (TypeError, AttributeError):
                response_body = str(getattr(response, "content", b""))

        OperationLog.objects.create(
            username=username,
            module=module,
            operation=operation,
            method=request.method,
            request_url=path,
            request_params=request_params[:2000] if request_params else "",
            response_result=response_body[:2000] if response_body else "",
            ip=request.META.get("REMOTE_ADDR", ""),
            status=1 if 200 <= response.status_code < 300 else 0,
            execution_time=duration,
        )

        return response