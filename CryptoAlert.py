	import requests
import time
import sys
from typing import Dict, Any

API_URL = "https://api.coingecko.com/api/v3/simple/price"

class CryptoAlert:
    def __init__(self, watchlist: Dict[str, Dict[str, float]], interval: int = 60):
        self.watchlist = watchlist
        self.interval = interval
        self.last_prices: Dict[str, float] = {}

    def fetch_prices(self) -> Dict[str, float]:
        ids = ",".join(self.watchlist.keys())
        params = {"ids": ids, "vs_currencies": "usd"}
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {coin: data[coin]["usd"] for coin in self.watchlist if coin in data}
        except Exception as e:
            print(f"[Error] Failed to fetch prices: {e}", file=sys.stderr)
            return {}

    def check_thresholds(self, prices: Dict[str, float]) -> None:
        for coin, price in prices.items():
            thresholds = self.watchlist[coin]
            last = self.last_prices.get(coin)
            # Alert only on crossing thresholds
            if last is not None:
                if thresholds.get("upper") is not None and last < thresholds["upper"] <= price:
                    print(f"[Alert] {coin} price rose above {thresholds['upper']}$: {price}$")
                if thresholds.get("lower") is not None and last > thresholds["lower"] >= price:
                    print(f"[Alert] {coin} price fell below {thresholds['lower']}$: {price}$")
            self.last_prices[coin] = price

    def run(self) -> None:
        print("Starting CryptoAlert...")
        while True:
            prices = self.fetch_prices()
            if prices:
                self.check_thresholds(prices)
            time.sleep(self.interval)

def main():
    # Sample watchlist: coin IDs from CoinGecko, thresholds in USD
    sample_watchlist = {
        "bitcoin": {"upper": 30000, "lower": 25000},
        "ethereum": {"upper": 2000, "lower": 1500}
    }
    # Interval in seconds; adjust as needed
    alert = CryptoAlert(sample_watchlist, interval=30)
    try:
        alert.run()
    except KeyboardInterrupt:
        print("\nCryptoAlert stopped by user.")

if __name__ == "__main__":
    main()
