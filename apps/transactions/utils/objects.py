from typing import Any


class CommonEqualityMixin(object):
    """Easy peasy equality"""
    def __eq__(self, other: Any) -> bool:
        return type(other) is type(self) and vars(self) == vars(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
