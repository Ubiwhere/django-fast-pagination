"""
Module to interact with django settings
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

from django.conf import settings as django_settings

# Only export "settings" object, when module
# is used with star import. E.g: `from module import *`
__all__ = ["settings"]


@dataclass
class Settings:
    """
    Django Fast Pagination Settings Container
    """

    # The url that should used when rendering an example
    # response
    BASE_RESPONSE_URL: Optional[str] = "https://ubiwhere.com/api/resource/?"
    # The number of items per page by default
    PAGE_SIZE: Optional[int] = 100
    # The name of the query parameter that
    # controls the number of items to display
    # in a API response
    PAGE_SIZE_QUERY_PARAM: Optional[str] = "page_size"
    # The maximum number of items that can be
    # requested from the API in a single page.
    MAX_PAGE_SIZE: Optional[int] = 9000


# Get fast pagination config from django
__configs = getattr(django_settings, "FAST_PAGINATION", {})
# Filter out configs with `None` as values, and
# keys that are not part of the desired configurations
__configs = {
    k: v
    for k, v in __configs.items()
    if v is not None and k in Settings.__annotations__.keys()
}

try:
    # The exported settings object
    settings = Settings(**__configs)

except TypeError as err:
    import fast_pagination.errors as errors

    if "required positional argument" in str(err):
        # Get missing variables with regex
        missing_required_vars = re.findall("'([^']*)'", str(err))
        raise errors.FastPaginationMissingSettingError(
            " / ".join(missing_required_vars)
        ) from err
    else:
        raise err
