"""
base_filter.py
--------------
Abstract base class for all pipeline filters.
Every filter must implement the `process` method, which receives
a transaction dictionary, enriches it, and returns it for the next filter.
"""

from abc import ABC, abstractmethod


class BaseFilter(ABC):
    """
    Abstract base class that defines the common interface for all pipeline filters.
    Each filter in the pipeline must inherit from this class and implement `process()`.
    """

    @abstractmethod
    def process(self, transaction: dict) -> dict:
        """
        Process the transaction context and return the enriched transaction.

        Args:
            transaction (dict): The current transaction context passed through the pipeline.

        Returns:
            dict: The enriched transaction context to be passed to the next filter.

        Raises:
            Exception: If the filter detects an invalid or unauthorized transaction.
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
