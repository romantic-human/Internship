from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """统一分页器：返回格式与设计文档一致"""

    page_size = 10
    page_size_query_param = "pageSize"
    page_query_param = "page"
    max_page_size = 50

    def get_paginated_response(self, data):
        from rest_framework.response import Response

        return Response(
            {
                "code": 200,
                "message": "success",
                "data": {
                    "records": data,
                    "total": self.page.paginator.count,
                    "page": self.page.number,
                    "pageSize": self.get_page_size(self.request),
                    "totalPages": self.page.paginator.num_pages,
                },
            }
        )
