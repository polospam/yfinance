import yfinance as yf


def get_forward_pe(ticker_symbol: str):
    stock = yf.Ticker(ticker_symbol.upper())
    info = stock.info
    # print("Stock info:", info)
    return info.get("forwardPE"), info.get("currentPrice"), info.get("forwardEps"), info.get("trailingEps")

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
