from filters.base_filter import BaseFilter


class ValidationFilter(BaseFilter):


    VALID_CURRENCIES = ["USD", "EUR", "GBP"]

    def process(self, transaction: dict) -> dict:

        print("  ┌─ Checking required fields...")

        # --- Validate user_id ---
        if "user_id" not in transaction:
            raise ValueError("[ValidationFilter] Missing required field: 'user_id'")
        if not transaction["user_id"] or not str(transaction["user_id"]).strip():
            raise ValueError("[ValidationFilter] Field 'user_id' cannot be empty")

        # --- Validate btc_amount ---
        if "btc_amount" not in transaction:
            raise ValueError("[ValidationFilter] Missing required field: 'btc_amount'")
        if not isinstance(transaction["btc_amount"], (int, float)):
            raise TypeError(
                f"[ValidationFilter] 'btc_amount' must be a number, "
                f"got {type(transaction['btc_amount']).__name__}"
            )
        if transaction["btc_amount"] <= 0:
            raise ValueError(
                f"[ValidationFilter] 'btc_amount' must be greater than 0, "
                f"got {transaction['btc_amount']}"
            )

        # --- Validate currency ---
        if "currency" not in transaction:
            raise ValueError("[ValidationFilter] Missing required field: 'currency'")
        if not transaction["currency"] or not str(transaction["currency"]).strip():
            raise ValueError("[ValidationFilter] Field 'currency' cannot be empty")

        currency_upper = str(transaction["currency"]).upper().strip()
        if currency_upper not in self.VALID_CURRENCIES:
            raise ValueError(
                f"[ValidationFilter] Invalid currency '{transaction['currency']}'. "
                f"Accepted values: {self.VALID_CURRENCIES}"
            )

        # --- Normalize and enrich ---
        transaction["currency"] = currency_upper
        transaction["user_id"] = str(transaction["user_id"]).strip()
        transaction["validation_status"] = "passed"

        print(
            f"  └─ ✓ Validation passed | user_id='{transaction['user_id']}' | "
            f"btc_amount={transaction['btc_amount']} | currency={transaction['currency']}"
        )
        return transaction
