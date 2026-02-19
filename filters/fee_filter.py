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


    def __init__(self):
        self.base_fee_usd = BASE_FEE_USD
        self.conversion_rates = FEE_CONVERSION_RATES

    def _calculate_fee(self, currency: str) -> float:

        rate = self.conversion_rates.get(currency)
        if rate is None:
            raise ValueError(
                f"[FeeFilter] No fee conversion rate defined for currency '{currency}'"
            )
        return round(self.base_fee_usd * rate, 2)

    def process(self, transaction: dict) -> dict:

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
