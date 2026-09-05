"""
this script implements the exact signal logic described in AgentQuiet.md
in plain Python using Binance public market data endpoints

"""

import requests

WATCHLIST = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
INTERVAL = "1h"
LOOKBACK = 20
VOLUME_MULTIPLE = 2.0
MAX_PRICE_MOVE_PERCENT = 1.0

BASE_URL = "https://api.binance.com/api/v3/klines"


def fetchCandles(symbol):
    params = {"symbol": symbol, "interval": INTERVAL, "limit": LOOKBACK}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def analyzeSymbol(symbol):
    candles = fetchCandles(symbol)
    if len(candles) < LOOKBACK:
        return None

    pastCandles = candles[:-1]
    latestCandle = candles[-1]

    pastVolumes = [float(candle[5]) for candle in pastCandles]
    baselineVolume = sum(pastVolumes) / len(pastVolumes)

    latestOpen = float(latestCandle[1])
    latestClose = float(latestCandle[4])
    latestVolume = float(latestCandle[5])

    priceMovePercent = abs((latestClose - latestOpen) / latestOpen) * 100
    volumeRatio = latestVolume / baselineVolume if baselineVolume else 0

    isSignal = volumeRatio >= VOLUME_MULTIPLE and priceMovePercent <= MAX_PRICE_MOVE_PERCENT

    return {
        "symbol": symbol,
        "volumeRatio": round(volumeRatio, 2),
        "priceMovePercent": round(priceMovePercent, 2),
        "isSignal": isSignal,
    }


def runScan():
    results = []
    for symbol in WATCHLIST:
        result = analyzeSymbol(symbol)
        if result:
            results.append(result)
    return results


def printReport(results):
    print("Quiet Accumulation Report")
    print()
    signals = [result for result in results if result["isSignal"]]

    print("Signals Found")
    if signals:
        for signal in signals:
            print(
                f"{signal['symbol']}: volume is {signal['volumeRatio']}x baseline, "
                f"price moved only {signal['priceMovePercent']}%, "
                "unusually high volume with little price movement can mean "
                "quiet accumulation. This is an observation, not a recommendation."
            )
    else:
        print("No signals this scan. Closest candidate shown below.")

    print()
    print("Watchlist Snapshot")
    for result in results:
        print(
            f"{result['symbol']}: volume ratio {result['volumeRatio']}x, "
            f"price move {result['priceMovePercent']}%"
        )


if __name__ == "__main__":
    scanResults = runScan()
    printReport(scanResults)
