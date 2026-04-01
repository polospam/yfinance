from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.momentum import analyze_momentum, analyze_multiple_momentum


client = TestClient(app)


def _make_mock_history(n=300):
    """Create a realistic-looking DataFrame for yfinance history."""
    dates = pd.bdate_range(end="2026-03-31", periods=n)
    rng = np.random.RandomState(42)
    close = 150.0 + rng.randn(n).cumsum()
    return pd.DataFrame(
        {
            "Open": close - rng.uniform(0, 2, n),
            "High": close + rng.uniform(0, 3, n),
            "Low": close - rng.uniform(0, 3, n),
            "Close": close,
            "Volume": rng.randint(1_000_000, 50_000_000, n).astype(float),
        },
        index=dates,
    )


def _patch_yf_ticker(history_df):
    """Return a mock yf.Ticker whose .history() returns the given df."""
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = history_df
    return mock_ticker


# ---------- Unit tests for analyze_momentum ----------


@patch("api.momentum.yf.Ticker")
def test_analyze_momentum_single(mock_ticker_cls):
    df = _make_mock_history()
    mock_ticker_cls.return_value = _patch_yf_ticker(df)

    result = analyze_momentum("AAPL")

    assert result["ticker"] == "AAPL"
    assert "current_price" in result
    assert "rsi_14" in result
    assert "macd" in result
    assert "verdict" in result
    assert "bullish_signals" in result
    assert isinstance(result["bullish_signals"], int)


@patch("api.momentum.yf.Ticker")
def test_analyze_momentum_empty_data(mock_ticker_cls):
    mock_ticker_cls.return_value = _patch_yf_ticker(pd.DataFrame())

    result = analyze_momentum("INVALID")
    assert result == {}


# ---------- Unit tests for analyze_multiple_momentum ----------


@patch("api.momentum.yf.Ticker")
def test_analyze_multiple_momentum(mock_ticker_cls):
    df = _make_mock_history()
    mock_ticker_cls.return_value = _patch_yf_ticker(df)

    results = analyze_multiple_momentum(["AAPL", "MSFT"])

    assert "AAPL" in results
    assert "MSFT" in results
    assert results["AAPL"]["ticker"] == "AAPL"
    assert results["MSFT"]["ticker"] == "MSFT"


@patch("api.momentum.yf.Ticker")
def test_analyze_multiple_momentum_skips_empty_tickers(mock_ticker_cls):
    df = _make_mock_history()
    mock_ticker_cls.return_value = _patch_yf_ticker(df)

    results = analyze_multiple_momentum(["AAPL", "", "  ", "MSFT"])

    assert "AAPL" in results
    assert "MSFT" in results
    assert len(results) == 2


@patch("api.momentum.yf.Ticker")
def test_analyze_multiple_momentum_empty_list(mock_ticker_cls):
    results = analyze_multiple_momentum([])
    assert results == {}
    mock_ticker_cls.assert_not_called()


# ---------- Endpoint integration tests ----------


@patch("api.momentum.yf.Ticker")
def test_momentum_single_endpoint(mock_ticker_cls):
    df = _make_mock_history()
    mock_ticker_cls.return_value = _patch_yf_ticker(df)

    response = client.get("/momentum/AAPL")

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "verdict" in data


@patch("api.momentum.yf.Ticker")
def test_momentum_multiple_endpoint(mock_ticker_cls):
    df = _make_mock_history()
    mock_ticker_cls.return_value = _patch_yf_ticker(df)

    response = client.get("/momentum/multiple/?tickers=AAPL,MSFT,GOOG")

    assert response.status_code == 200
    data = response.json()
    assert "tickers" in data
    assert "AAPL" in data["tickers"]
    assert "MSFT" in data["tickers"]
    assert "GOOG" in data["tickers"]


@patch("api.momentum.yf.Ticker")
def test_momentum_multiple_single_ticker(mock_ticker_cls):
    """Backward compatibility: a single ticker still works."""
    df = _make_mock_history()
    mock_ticker_cls.return_value = _patch_yf_ticker(df)

    response = client.get("/momentum/multiple/?tickers=AAPL")

    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data["tickers"]
    assert len(data["tickers"]) == 1


def test_momentum_multiple_empty_tickers():
    response = client.get("/momentum/multiple/?tickers=")

    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "No valid tickers provided"
    assert data["tickers"] == {}


def test_momentum_multiple_whitespace_only():
    response = client.get("/momentum/multiple/?tickers=%20,%20,")

    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "No valid tickers provided"
    assert data["tickers"] == {}


@patch("api.momentum.yf.Ticker")
def test_momentum_multiple_invalid_ticker_returns_empty(mock_ticker_cls):
    """An invalid ticker returns an empty dict from analyze_momentum."""
    mock_ticker_cls.return_value = _patch_yf_ticker(pd.DataFrame())

    response = client.get("/momentum/multiple/?tickers=INVALIDTICKER123")

    assert response.status_code == 200
    data = response.json()
    assert "INVALIDTICKER123" in data["tickers"]
    assert data["tickers"]["INVALIDTICKER123"] == {}
