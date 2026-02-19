"""
main.py
-------
Entry point for the BTC Transaction Pipeline.

Demonstrates the pipeline processing 4 test cases:
    1. Valid transaction in USD  (Alice Johnson  — 0.5 BTC)
    2. Valid transaction in EUR  (Bob Smith      — 1.2 BTC)
    3. Valid transaction in GBP  (Carol White    — 0.25 BTC)
    4. Error case: inactive user (David Brown    — 0.1 BTC)
    5. Error case: missing field (no currency)
"""

import sys
import os

# Ensure the PipelineBTC directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import Pipeline
from filters.validation_filter import ValidationFilter
from filters.authentication_filter import AuthenticationFilter
from filters.transformation_filter import TransformationFilter
from filters.fee_filter import FeeFilter
from filters.storage_filter import StorageFilter


# ---------------------------------------------------------------------------
# Pipeline factory — builds a fresh pipeline for each transaction
# ---------------------------------------------------------------------------
def build_pipeline() -> Pipeline:
    """
    Instantiate and configure the 5-stage BTC transaction pipeline.

    Returns:
        Pipeline: A fully configured pipeline ready to execute.
    """
    # Resolve paths relative to this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    users_db = os.path.join(base_dir, "data", "users.json")
    transactions_db = os.path.join(base_dir, "data", "transactions.db")

    pipeline = Pipeline()
    pipeline.add_filter(ValidationFilter())
    pipeline.add_filter(AuthenticationFilter(users_db_path=users_db))
    pipeline.add_filter(TransformationFilter())
    pipeline.add_filter(FeeFilter())
    pipeline.add_filter(StorageFilter(db_path=transactions_db))
    return pipeline


# ---------------------------------------------------------------------------
# Transaction runner — executes one transaction and prints the summary
# ---------------------------------------------------------------------------
def run_transaction(transaction: dict) -> dict | None:
    """
    Run a single transaction through the pipeline and print the result summary.

    Args:
        transaction (dict): Raw transaction input.

    Returns:
        dict | None: The processed transaction, or None if the pipeline failed.
    """
    pipeline = build_pipeline()

    try:
        result = pipeline.execute(transaction)
        _print_summary(result)
        return result

    except (ValueError, TypeError) as e:
        print(f"\n  ⚠  Validation / Type Error: {e}\n")
    except PermissionError as e:
        print(f"\n  🔒 Authentication Error: {e}\n")
    except ConnectionError as e:
        print(f"\n  🌐 API Error: {e}\n")
    except Exception as e:
        print(f"\n  ✗  Unexpected Error [{type(e).__name__}]: {e}\n")

    return None


def _print_summary(result: dict) -> None:
    """Print a formatted summary of the processed transaction."""
    currency = result["currency"]
    print()
    print("┌" + "─" * 62 + "┐")
    print("│{:^62}│".format("📊  TRANSACTION SUMMARY"))
    print("├" + "─" * 62 + "┤")
    print(f"│  Transaction ID  : {result['transaction_id']:<42}│")
    print(f"│  User            : {result['user_name']} ({result['user_id']}){'':<{20 - len(result['user_name']) - len(result['user_id'])}}│")
    print(f"│  Email           : {result['user_email']:<42}│")
    print("├" + "─" * 62 + "┤")
    print(f"│  BTC Amount      : {result['btc_amount']:<42}│")
    print(f"│  BTC Price       : {result['btc_price']:>12,.2f} {currency:<28}│")
    print(f"│  Subtotal        : {result['subtotal']:>12,.2f} {currency:<28}│")
    print(f"│  Commission      : {result['fee']:>12,.2f} {currency:<28}│")
    print(f"│  TOTAL PAYABLE   : {result['total_with_fee']:>12,.2f} {currency:<28}│")
    print("├" + "─" * 62 + "┤")
    print(f"│  Status          : {result['status'].upper():<42}│")
    print(f"│  Timestamp       : {result['timestamp']:<42}│")
    print(f"│  Price Source    : {result.get('api_source', 'N/A'):<42}│")
    print("└" + "─" * 62 + "┘")


# ---------------------------------------------------------------------------
# Main — test cases
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    SEPARATOR = "\n" + "━" * 64 + "\n"

    print("=" * 64)
    print("   BTC PURCHASE PIPELINE — EXECUTION DEMO")
    print("=" * 64)

    # ── Test Case 1: Valid USD transaction ──────────────────────────────
    print(SEPARATOR)
    print("TEST CASE 1 — Valid transaction | USD | Alice Johnson | 0.5 BTC")
    run_transaction({
        "user_id": "USR001",
        "btc_amount": 0.5,
        "currency": "USD"
    })

    # ── Test Case 2: Valid EUR transaction ──────────────────────────────
    print(SEPARATOR)
    print("TEST CASE 2 — Valid transaction | EUR | Bob Smith | 1.2 BTC")
    run_transaction({
        "user_id": "USR002",
        "btc_amount": 1.2,
        "currency": "EUR"
    })

    # ── Test Case 3: Valid GBP transaction ──────────────────────────────
    print(SEPARATOR)
    print("TEST CASE 3 — Valid transaction | GBP | Carol White | 0.25 BTC")
    run_transaction({
        "user_id": "USR003",
        "btc_amount": 0.25,
        "currency": "GBP"
    })

    # ── Test Case 4: Inactive user (should fail at Authentication) ──────
    print(SEPARATOR)
    print("TEST CASE 4 — ERROR: Inactive user | David Brown (USR004)")
    run_transaction({
        "user_id": "USR004",
        "btc_amount": 0.1,
        "currency": "USD"
    })

    # ── Test Case 5: Missing currency field (should fail at Validation) ─
    print(SEPARATOR)
    print("TEST CASE 5 — ERROR: Missing 'currency' field")
    run_transaction({
        "user_id": "USR001",
        "btc_amount": 0.3
    })

    print(SEPARATOR)
    print("✓ All test cases executed. Check data/transactions.db for stored records.")
    print("=" * 64)
