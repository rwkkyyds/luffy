
from rest_framework.pagination import PageNumberPagination

# 分页类：前端不传参数时，每页默认返回 10 条数据
# page_size_query_param='page_size' 表示前端可以通过 ?page_size=20 来自定义每页条数
# max_page_size=50 表示前端最多只能请求每页 50 条，防止一次查太多拖慢数据库
class CommonPageNumberPagination(PageNumberPagination):
    page_size = 10           # 默认每页 10 条
    page_query_param = 'page'  # 前端用 ?page=2 来指定第几页
    page_size_query_param = 'page_size'  # 前端用 ?page_size=20 来指定每页条数
    max_page_size = 50       # 每页最多 50 条，防止前端传很大的值
