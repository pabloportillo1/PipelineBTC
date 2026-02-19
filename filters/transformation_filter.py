import datetime
from filters.base_filter import BaseFilter


MOCK_BTC_RATES = {
    "USD": 65_000.00,   # 1 BTC = 65,000.00 USD
    "EUR": 60_500.00,   # 1 BTC = 60,500.00 EUR
    "GBP": 51_800.00,   # 1 BTC = 51,800.00 GBP
}

MOCK_API_SOURCE = "MockBTCPriceAPI v1.0"


def _simulate_api_call(currency: str) -> dict:

    if currency not in MOCK_BTC_RATES:
        raise ConnectionError(
            f"[TransformationFilter] Mock API error: "
            f"No rate available for currency '{currency}'"
        )

    return {
        "currency": currency,
        "btc_price": MOCK_BTC_RATES[currency],
        "source": MOCK_API_SOURCE,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "ok",
    }


class TransformationFilter(BaseFilter):


    def process(self, transaction: dict) -> dict:

        currency = transaction["currency"]
        btc_amount = transaction["btc_amount"]

        print(f"  ┌─ Calling BTC price API for currency: {currency}...")

        # --- Simulate REST API call ---
        api_response = _simulate_api_call(currency)

        btc_price = api_response["btc_price"]
        total_value = round(btc_amount * btc_price, 2)

        # --- Enrich transaction ---
        transaction["btc_price"] = btc_price
        transaction["total_value"] = total_value
        transaction["api_source"] = api_response["source"]
        transaction["price_timestamp"] = api_response["timestamp"]

        print(
            f"  ├─ API Response: 1 BTC = {btc_price:,.2f} {currency} "
            f"(source: {api_response['source']})"
        )
        print(
            f"  └─ ✓ Transformation complete | "
            f"{btc_amount} BTC × {btc_price:,.2f} = {total_value:,.2f} {currency}"
        )
        return transaction
