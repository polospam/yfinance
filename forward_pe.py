import yfinance as yf


def get_forward_pe(ticker_symbol: str):
    stock = yf.Ticker(ticker_symbol.upper())
    info = stock.info
    # print("Stock info:", info)
    return info.get("forwardPE"), info.get("currentPrice"), info.get("forwardEps"), info.get("trailingEps")

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
    if forward_pe is not None:
        print(f"{ticker.upper()} Forward P/E Ratio: {round(forward_pe, 1)}")
        print(f"{ticker.upper()} Current Price: ${current_price}")
        print(f"{ticker.upper()} Forward EPS: ${round(forward_eps, 2)}")
        print(f"{ticker.upper()} Trailing EPS: ${trailing_eps}")
    else:
        print("Forward P/E data not available.")
    # list ["msft", "aapl", "googl"]
    # string "msft,aapl,googl"
    tickers_input = input("Enter multiple stock ticker symbols (comma-separated): ")
    ticker_list = [ticker.strip() for ticker in tickers_input.split(",")]
    fwd_pe_results = get_multiple_fwd_pes(ticker_list)
    print(fwd_pe_results)