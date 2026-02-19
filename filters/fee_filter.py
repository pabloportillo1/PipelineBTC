"""
fee_filter.py
-------------
Filter 4 - Fee Calculation Filter

Calculates the fixed transaction commission (5.00 USD or its equivalent
in the base currency) and adds it to the total transaction amount.

Commission policy:
    - Base fee: 5.00 USD
    - Converted to the transaction's base currency using fixed exchange rates.
    - Added to the subtotal to produce the final payable amount.
"""

from filters.base_filter import BaseFilter


# ---------------------------------------------------------------------------
# Fixed commission in USD and conversion rates to supported currencies
# ---------------------------------------------------------------------------
BASE_FEE_USD = 5.00

# Approximate USD → target currency conversion rates for fee calculation
FEE_CONVERSION_RATES = {
    "USD": 1.0000,   # 5.00 USD  → 5.00 USD
    "EUR": 0.9240,   # 5.00 USD  → 4.62 EUR
    "GBP": 0.7920,   # 5.00 USD  → 3.96 GBP
}


class FeeFilter(BaseFilter):
    """
    Pipeline Filter #4 — Fee Calculation

    Responsibilities:
        - Determine the commission amount in the transaction's base currency.
        - Add the commission to the subtotal to compute the final payable amount.
        - Enrich the transaction with fee details.
    """

    def __init__(self):
        self.base_fee_usd = BASE_FEE_USD
        self.conversion_rates = FEE_CONVERSION_RATES

    def _calculate_fee(self, currency: str) -> float:
        """
        Convert the base USD fee to the target currency.

        Args:
            currency (str): Target currency code (USD, EUR, GBP).

        Returns:
            float: Fee amount in the target currency, rounded to 2 decimal places.

        Raises:
            ValueError: If no conversion rate is defined for the given currency.
        """
        rate = self.conversion_rates.get(currency)
        if rate is None:
            raise ValueError(
                f"[FeeFilter] No fee conversion rate defined for currency '{currency}'"
            )
        return round(self.base_fee_usd * rate, 2)

    def process(self, transaction: dict) -> dict:
        """
        Apply the transaction commission and compute the final total.

        Args:
            transaction (dict): Transaction context from the previous filter.

        Returns:
            dict: Transaction enriched with:
                  - 'fee'           : Commission amount in the base currency
                  - 'fee_currency'  : Currency of the commission
                  - 'fee_usd_base'  : Original fee in USD (for reference)
                  - 'subtotal'      : Value before commission (alias of total_value)
                  - 'total_with_fee': Final payable amount (subtotal + fee)

        Raises:
            ValueError: If the currency has no defined fee conversion rate.
        """
        currency = transaction["currency"]
        subtotal = transaction["total_value"]

        print(f"  ┌─ Calculating commission for currency: {currency}...")

        fee = self._calculate_fee(currency)
        total_with_fee = round(subtotal + fee, 2)

        # --- Enrich transaction ---
        transaction["fee"] = fee
        transaction["fee_currency"] = currency
        transaction["fee_usd_base"] = self.base_fee_usd
        transaction["subtotal"] = subtotal
        transaction["total_with_fee"] = total_with_fee

        print(
            f"  ├─ Base fee: {self.base_fee_usd:.2f} USD "
            f"→ {fee:.2f} {currency} "
            f"(rate: {self.conversion_rates[currency]})"
        )
        print(
            f"  └─ ✓ Fee applied | Subtotal: {subtotal:,.2f} {currency} "
            f"+ Fee: {fee:.2f} {currency} = Total: {total_with_fee:,.2f} {currency}"
        )
        return transaction
