class ComparableMixin:
    """Mixin to provide full comparison operations based on just __lt__.

    Classes using this mixin must implement __lt__.
    Note: In modern Python, `functools.total_ordering` is preferred for this purpose.
    """

    def __eq__(self, other):
        """Check if self is equal to other.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        return not self < other and not other < self

    def __ne__(self, other):
        """Check if self is not equal to other.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if not equal, False otherwise.
        """
        return self < other or other < self

    def __gt__(self, other):
        """Check if self is greater than other.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if greater than, False otherwise.
        """
        return other < self

    def __ge__(self, other):
        """Check if self is greater than or equal to other.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if greater than or equal to, False otherwise.
        """
        return not self < other

    def __le__(self, other):
        """Check if self is less than or equal to other.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if less than or equal to, False otherwise.
        """
        return not other < self
