"""
Module with custom pagination object
"""
import sys

from django.core.paginator import InvalidPage, Paginator
from rest_framework.exceptions import NotFound

# Import "slow" pagination class as double underscore to avoid confusion
# when importing our own pagination class
from rest_framework.pagination import PageNumberPagination as __
from rest_framework.response import Response

from django_fast_pagination.conf import settings

# Only export "FastPageNumberPagination" object, when module
# is used with star import. E.g: `from module import *`
__all__ = ["FastPageNumberPagination"]


def get_show_count_from_request(request) -> bool:
    return request.query_params.get("show_count", "False").lower() == "true"


class NoCountQuery(Paginator):
    """
    Django default Paginator makes a `.count()`
    call to get the total number of items in the database,
    which is very costly in millions of records.
    This paginator disables this behaviour by providing
    the system's maximum number as a count, thus avoiding
    the database query, reducing queries time by +99%.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    @property
    def count(self) -> int:
        """If `show_count` query parameter is true, an actual count
        is performed. Otherwise (default behavior), we patch the count
        with `sys.maxsize`."""
        show_count: bool = get_show_count_from_request(self.request)
        if show_count:
            return super().count
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
    # use template without page numbers for django rest browseable API
    template = "rest_framework/pagination/previous_and_next.html"

    def get_paginated_response(self, data):
        # Check if the response should include counting or not
        show_count: bool = get_show_count_from_request(self.request)
        if show_count:
            response = {"count": self.page.paginator.count}
        else:
            response = {}
        # Add the common response
        response |= {
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
        return Response(response)

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
                    "example": f"{settings.EXAMPLE_URL}&page=3",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": f"{settings.EXAMPLE_URL}&page=1",
                },
                "results": schema,
            },
        }

    def get_html_context(self):
        """Specify the needed context for
        "rest_framework/pagination/previous_and_next.html" template rendering."""
        return {
            "previous_url": self.get_previous_link(),
            "next_url": self.get_next_link(),
        }

    def paginate_queryset(self, queryset, request, view):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        # This is where the code differs from the original. We instantiate
        # paginator class with an extra argument to pass the "request" object.
        paginator = self.django_paginator_class(queryset, page_size, request=request)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        qs = list(self.page)
        # If queryset returned empty make sure we dont render any
        # next link. We already ran out of data
        if not qs:
            self.page.has_next = lambda: False
        return qs
