"""
Module with custom pagination object
"""
import sys

from django.utils.functional import cached_property
from django.core.paginator import Paginator

# Import "slow" pagination class as double underscore to avoid confusion
# when importing our own pagination class
from rest_framework.pagination import PageNumberPagination as __
from rest_framework.response import Response

from django_fast_pagination.conf import settings

# Only export "FastPageNumberPagination" object, when module
# is used with star import. E.g: `from module import *`
__all__ = ["FastPageNumberPagination"]


class NoCountQuery(Paginator):
    """
    Django default Paginator makes a `.count()`
    call to get the total number of items in the database,
    which is very costly in millions of records.
    This paginator disables this behaviour by providing
    the system's maximum number as a count, thus avoiding
    the database query, reducing queries time by +99%.
    """

    @cached_property
    def count(self) -> int:
        return sys.maxsize


class FastPageNumberPagination(__):
    """
    Custom Django Rest Pagination class based on
    user defined settings and uses a custom Django
    Paginator that avoids `COUNT` SQL query on
    each API response.
    """

    django_paginator_class = NoCountQuery
    page_size = settings.PAGE_SIZE
    page_size_query_param = settings.PAGE_SIZE_QUERY_PARAM
    max_page_size = settings.MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response(
            {
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        """
        Returns the OpenAPI schema for the default API pagination
        mechanism.
        """
        return {
            "type": "object",
            "properties": {
                "current_page": {
                    "type": "integer",
                    "example": 2,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": f"{settings.BASE_RESPONSE_URL}{self.page_query_param}=3",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": f"{settings.BASE_RESPONSE_URL}{self.page_query_param}=1",
                },
                "results": schema,
            },
        }
