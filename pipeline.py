"""
pipeline.py
-----------
Pipeline Orchestrator

Implements the Pipe-and-Filter architectural pattern.
The Pipeline class chains multiple BaseFilter instances sequentially,
passing the transaction context from one filter to the next.

Each filter:
    - Receives the transaction dict from the previous stage.
    - Processes and enriches it.
    - Returns the updated dict to be passed to the next filter.

If any filter raises an exception, the pipeline halts immediately
and propagates the error with a clear diagnostic message.
"""

from typing import List
from filters.base_filter import BaseFilter


class Pipeline:
    """
    Pipe-and-Filter Pipeline Orchestrator.

    Manages an ordered list of filters and executes them sequentially
    against a transaction context dictionary.

    Usage:
        pipeline = Pipeline()
        pipeline.add_filter(ValidationFilter())
        pipeline.add_filter(AuthenticationFilter())
        ...
        result = pipeline.execute(transaction)
    """

    def __init__(self):
        self._filters: List[BaseFilter] = []

    def add_filter(self, filter_instance: BaseFilter) -> "Pipeline":
        """
        Append a filter to the end of the pipeline.

        Args:
            filter_instance (BaseFilter): An instance of a class that extends BaseFilter.

        Returns:
            Pipeline: Returns self to allow method chaining.

        Raises:
            TypeError: If the provided object is not a BaseFilter instance.
        """
        if not isinstance(filter_instance, BaseFilter):
            raise TypeError(
                f"Expected a BaseFilter instance, got {type(filter_instance).__name__}"
            )
        self._filters.append(filter_instance)
        return self

    def execute(self, transaction: dict) -> dict:
        """
        Execute all filters in sequence against the transaction context.

        Args:
            transaction (dict): The initial transaction data to process.

        Returns:
            dict: The fully enriched transaction after all filters have run.

        Raises:
            Exception: Re-raises any exception thrown by a filter, with context info.
        """
        if not self._filters:
            raise RuntimeError("Pipeline has no filters configured.")

        self._print_header(transaction)

        current_data = transaction.copy()

        for step, filter_instance in enumerate(self._filters, start=1):
            filter_name = filter_instance.__class__.__name__
            self._print_step(step, filter_name)

            try:
                current_data = filter_instance.process(current_data)
            except Exception as exc:
                self._print_error(step, filter_name, exc)
                raise

            print()  # blank line between steps

        self._print_footer()
        return current_data

    # ------------------------------------------------------------------
    # Private helpers for formatted console output
    # ------------------------------------------------------------------

    def _print_header(self, transaction: dict) -> None:
        print()
        print("╔" + "═" * 62 + "╗")
        print("║{:^62}║".format("BITCOIN TRANSACTION PIPELINE"))
        print("╠" + "═" * 62 + "╣")
        print("║  INPUT TRANSACTION:                                          ║")
        print(f"║    user_id    : {transaction.get('user_id', 'N/A'):<44}║")
        print(f"║    btc_amount : {str(transaction.get('btc_amount', 'N/A')):<44}║")
        print(f"║    currency   : {transaction.get('currency', 'N/A'):<44}║")
        print("╠" + "═" * 62 + "╣")
        print("║  PROCESSING STAGES:                                          ║")
        print("╚" + "═" * 62 + "╝")
        print()

    def _print_step(self, step: int, filter_name: str) -> None:
        label = f"[{step}/5] {filter_name}"
        print(f"▶ {label}")
        print("  " + "─" * 56)

    def _print_error(self, step: int, filter_name: str, exc: Exception) -> None:
        print()
        print("╔" + "═" * 62 + "╗")
        print("║{:^62}║".format("✗ PIPELINE FAILED"))
        print("╠" + "═" * 62 + "╣")
        print(f"║  Step        : {step}/5 — {filter_name:<40}║")
        print(f"║  Error type  : {type(exc).__name__:<44}║")
        # Truncate long messages for display
        msg = str(exc)
        for i in range(0, min(len(msg), 120), 58):
            print(f"║  {msg[i:i+58]:<60}║")
        print("╚" + "═" * 62 + "╝")

    def _print_footer(self) -> None:
        print("╔" + "═" * 62 + "╗")
        print("║{:^62}║".format("✓ PIPELINE COMPLETED SUCCESSFULLY"))
        print("╚" + "═" * 62 + "╝")
