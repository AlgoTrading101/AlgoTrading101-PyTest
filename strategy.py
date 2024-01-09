import numpy as np
from ib_insync import *


def init_connection():
    """Initializes the connection to the IB API"""
    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=1)
    return ib


def get_historical_data(ib, contract, duration, barSize):
    """Returns historical data for a given contract"""
    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr=duration,
        barSizeSetting=barSize,
        whatToShow="MIDPOINT",
        useRTH=True,
        formatDate=1,
    )
    return bars


def calculate_moving_averages(data, short_window, long_window):
    """Calculates the short and long moving averages"""
    data["short_mavg"] = (
        data["close"].rolling(window=short_window, min_periods=1).mean()
    )
    data["long_mavg"] = data["close"].rolling(window=long_window, min_periods=1).mean()
    return data


def generate_signals(data, long_window):
    """Generates trading signals for a given dataset"""
    data["signal"] = 0
    data["signal"][long_window:] = np.where(
        data["short_mavg"][long_window:] > data["long_mavg"][long_window:], 1, 0
    )
    data["positions"] = data["signal"].diff()
    return data


def execute_order(ib, signal, contract, quantity):
    """Executes a trade"""
    if signal == 1:
        order = MarketOrder("BUY", quantity)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)
    elif signal == -1:
        order = MarketOrder("SELL", quantity)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)


def trading_strategy():
    """Executes the trading strategy"""
    ib = init_connection()
    contract = Stock("AAPL", "SMART", "USD")
    bars = get_historical_data(ib, contract, "1 Y", "1 day")
    df = util.df(bars)

    short_window = 40
    long_window = 100

    df_with_mavg = calculate_moving_averages(df, short_window, long_window)
    signals = generate_signals(df_with_mavg, long_window)

    for i in range(len(signals)):
        if signals["positions"][i] == 1:
            execute_order(ib, 1, contract, 100)  # Buy
        elif signals["positions"][i] == -1:
            execute_order(ib, -1, contract, 100)  # Sell

    ib.disconnect()


if __name__ == "__main__":
    trading_strategy()
