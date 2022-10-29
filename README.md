# Django Fast Pagination

## Want to improve your API performance? :dash:

You can use this small package as a drop-in replacement for Django's Rest Framework
`DEFAULT_PAGINATION_CLASS`, or apply it on a per-view basis.

## Instructions
1. Install
```
python -m pip install git+https://github.com/ubiwhere/django-fast-pagination
```
2. Add to your `requirements.txt`
```
django-fast-pagination @ git+https://github.com/ubiwhere/django-fast-pagination
```
3. Add as the default pagination class:
```python
REST_FRAMEWORK = {
    # Your other rest framework settings...
    "DEFAULT_PAGINATION_CLASS": "django_fast_pagination.FastPageNumberPagination",
}
```
or per-view basis:
```python
from rest_framework import viewsets
from django_fast_pagination import FastPageNumberPagination
class FooViewSet(viewsets.ModelViewSet):
    pagination_class = FastPageNumberPagination
```

**That's it! No need to add to `INSTALLED_APPS`, as this package does not contain any Django models**

Optionally, you can define some settings:
```python
# Configuration for Fast Pagination (all fields are optional)
FAST_PAGINATION = {
    # The url that should used when rendering an example
    # response (don't forgot the '?' at the end)
    "BASE_RESPONSE_URL": "https://ubiwhere.com/api/resource/?",
    # The number of items per page
    "PAGE_SIZE": 100,
    # The name of the query parameter that
    # controls the number of items to display
    # in a API response
    "PAGE_SIZE_QUERY_PARAM": "page_size",
    # The maximum number of items that can be
    # requested from the API in a single page.
    "MAX_PAGE_SIZE": 9000
}
```

## Package caveats

This package works by "patching" the Django's paginator class `count` method, with
a very large number (`sys.maxsize`), thus avoiding the database count query, that can
have a very large performance drag on high volume databases. The only caveat is that your
browseable API will show the following:

**Alternative**: Alternatively, you can use Django Rest built-in `CursorPagination` that will achieve a similar result as this package. However, it requires a more complex setup. Refer to the [documentation](https://www.django-rest-framework.org/api-guide/pagination/#cursorpagination) for more information.
