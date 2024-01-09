import pandas as pd
import pytest
from ib_insync import IB, Stock

from strategy import calculate_moving_averages, generate_signals, get_historical_data

# Mock data for testing
mock_data = pd.DataFrame({"close": [100, 102, 101, 103, 105, 107, 108, 110, 112, 115]})


@pytest.fixture(scope="module")
def ib_connection():
    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=1)
    return ib


def test_get_historical_data(ib_connection):
    contract = Stock("AAPL", "SMART", "USD")
    data = get_historical_data(ib_connection, contract, "1 D", "1 min")
    assert not data.empty, "Data should not be empty"


def test_calculate_moving_averages():
    short_window = 3
    long_window = 5
    calculated_data = calculate_moving_averages(mock_data, short_window, long_window)
    assert (
        "short_mavg" in calculated_data.columns
    ), "Short moving average not calculated"
    assert "long_mavg" in calculated_data.columns, "Long moving average not calculated"
    assert (
        calculated_data["short_mavg"].iloc[-1] == mock_data["close"].iloc[-3:].mean()
    ), "Short moving average calculation is incorrect"
    assert (
        calculated_data["long_mavg"].iloc[-1] == mock_data["close"].iloc[-5:].mean()
    ), "Long moving average calculation is incorrect"


@pytest.mark.parametrize(
    "short_window, long_window, expected",
    [(3, 5, 1), (5, 3, 0), (3, 3, 0), (5, 5, 0)],
)
def test_generate_signals(short_window, long_window, expected):
    data_with_mavg = calculate_moving_averages(mock_data, short_window, long_window)
    signals = generate_signals(data_with_mavg, long_window)
    assert "signal" in signals.columns, "Signal column not generated"
    assert "positions" in signals.columns, "Positions column not generated"
    assert all(
        signals["signal"].isin([0, 1])
    ), "Signal column should only contain 0 or 1"
    assert expected == signals["signal"].iloc[-1], "Signal calculation is incorrect"
