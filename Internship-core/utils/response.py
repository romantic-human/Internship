from rest_framework.response import Response as DRFResponse


class APIResponse:
    """统一响应格式"""

    @staticmethod
    def success(data=None, message="操作成功"):
        return DRFResponse(
            {"code": 200, "message": message, "data": data or {}},
        )

    @staticmethod
    def created(data=None, message="新增成功"):
        return DRFResponse(
            {"code": 200, "message": message, "data": data or {}},
            status=201,
        )

    @staticmethod
    def error(message="操作失败", code=400, http_status=400):
        return DRFResponse(
            {"code": code, "message": message, "data": None},
            status=http_status,
        )

    @staticmethod
    def not_found(message="数据不存在"):
        return DRFResponse(
            {"code": 2002, "message": message, "data": None},
            status=404,
        )

    @staticmethod
    def conflict(message="数据已存在"):
        return DRFResponse(
            {"code": 2001, "message": message, "data": None},
            status=409,
        )
