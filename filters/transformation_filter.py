"""
transformation_filter.py
------------------------
Filter 3 - Transformation Filter

Converts the BTC amount to the target base currency using exchange rates
obtained from a simulated REST API (mock service with fixed realistic rates).

Simulated API endpoint: GET /api/v1/btc/price?currency={USD|EUR|GBP}
Response format: { "currency": "USD", "btc_price": 65000.00, "source": "MockBTCAPI" }
"""

import datetime
from filters.base_filter import BaseFilter


# ---------------------------------------------------------------------------
# Simulated REST API — Mock BTC Exchange Rate Service
# In a real implementation this would be an HTTP call to CoinGecko, Binance, etc.
# ---------------------------------------------------------------------------
MOCK_BTC_RATES = {
    "USD": 65_000.00,   # 1 BTC = 65,000.00 USD
    "EUR": 60_500.00,   # 1 BTC = 60,500.00 EUR
    "GBP": 51_800.00,   # 1 BTC = 51,800.00 GBP
}

MOCK_API_SOURCE = "MockBTCPriceAPI v1.0"


def _simulate_api_call(currency: str) -> dict:
    """
    Simulates an HTTP GET request to a BTC price REST API.

    In production this would be:
        response = requests.get(f"https://api.btcprice.io/v1/price?currency={currency}")
        return response.json()

    Args:
        currency (str): The target currency code (USD, EUR, GBP).

    Returns:
        dict: Simulated API response with BTC price data.

    Raises:
        ConnectionError: If the currency is not supported by the mock API.
    """
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
    """
    Pipeline Filter #3 — Transformation

    Responsibilities:
        - Call the (simulated) REST API to retrieve the current BTC price.
        - Calculate the total transaction value in the base currency.
        - Enrich the transaction with price data and computed total.
    """

    def process(self, transaction: dict) -> dict:
        """
        Convert BTC amount to the base currency value.

        Args:
            transaction (dict): Transaction context from the previous filter.

        Returns:
            dict: Transaction enriched with:
                  - 'btc_price'    : Price of 1 BTC in the base currency
                  - 'total_value'  : btc_amount × btc_price
                  - 'api_source'   : Name of the price data source

        Raises:
            ConnectionError: If the mock API cannot return a rate for the currency.
        """
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
