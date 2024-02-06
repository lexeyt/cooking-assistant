from rest_framework.pagination import PageNumberPagination as DefaultPagination


class PageNumberPagination(DefaultPagination):
    page_size_query_param = "limit"
