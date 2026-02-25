from typing import Optional
import yfinance as yf

def get_forward_pe(ticker_symbol: str):
    stock = yf.Ticker(ticker_symbol.upper())
    info: dict = stock.info
    # print("Stock info:", info)
    raw_fwd_pe = info.get("forwardPE")
    if raw_fwd_pe is None:
        fwd_pe: Optional[float] = None
    else:
        try:
            fwd_pe = round(float(raw_fwd_pe), 1)
        except (TypeError, ValueError):
            fwd_pe = None

    price = info.get("currentPrice")

    raw_fwd_eps = info.get("forwardEps")
    if raw_fwd_eps is None:
        fwd_eps: Optional[float] = None
    else:
        try:
            fwd_eps = round(float(raw_fwd_eps), 2)
        except (TypeError, ValueError):
            fwd_eps = None

    trl_eps_raw = info.get("trailingEps")
    if trl_eps_raw is None:
        trl_eps: Optional[float] = None
    else:
        try:
            trl_eps = round(float(trl_eps_raw), 2)
        except (TypeError, ValueError):
            trl_eps = None

    return fwd_pe, price, fwd_eps, trl_eps

def get_multiple_fwd_pes(ticker_symbols: list[str]):
    fwd_pe_data = {}
    for ticker in ticker_symbols:
        fwd_pe, price, fwd_eps, trl_eps = get_forward_pe(ticker)
        fwd_pe_data[ticker.upper()] = {
            "currentPrice": price,
            "trailingEPS": trl_eps,
            "forwardEPS": fwd_eps,
            "forwardPE": fwd_pe
        }
    return fwd_pe_data

if __name__ == "__main__":
    ticker = input("Enter a stock ticker symbol: ")
    forward_pe, current_price, forward_eps, trailing_eps = get_forward_pe(ticker)
    if forward_pe is not None and forward_eps is not None and trailing_eps is not None:
        print(f"{ticker.upper()} Forward P/E Ratio: {forward_pe}")
        print(f"{ticker.upper()} Current Price: ${current_price}")
        print(f"{ticker.upper()} Forward EPS: ${forward_eps}")
        print(f"{ticker.upper()} Trailing EPS: ${trailing_eps}")
    else:
        print("Forward P/E data not available.")
    # list ["msft", "aapl", "googl"]
    # string "msft,aapl,googl"
    tickers_input = input("Enter multiple stock ticker symbols (comma-separated): ")
    ticker_list = [ticker.strip() for ticker in tickers_input.split(",")]
    fwd_pe_results = get_multiple_fwd_pes(ticker_list)
    print(fwd_pe_results)