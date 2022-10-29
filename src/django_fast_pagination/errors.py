"""
Module containing custom exceptions
"""


class FastPaginationMissingSettingError(Exception):
    """
    Raised when a given Django Fast Pagination setting is missing.
    """

    def __init__(self, setting: str):
        super().__init__(
            (
                f"The following settings are missing: '{setting}' "
                "Please add them in 'FAST_PAGINATION' inside Django settings"
            )
        )
