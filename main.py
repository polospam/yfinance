from fastapi import FastAPI
from forward_pe import get_forward_pe, get_multiple_fwd_pes


app = FastAPI()

@app.get("/fwd-pe/{ticker}")
def forward_pe(ticker: str):
    try:
        fwd_pe, price, fwd_eps, trl_eps = get_forward_pe(ticker)
    except:
        pass

    return {
        "ticker": ticker.upper(),
        "price": price,
        "forwardPE": fwd_pe,
        "forwardEPS": fwd_eps,
        "trailingEPS": trl_eps
    }

# Endpoint for multiple comma-seprated tickers
@app.get("/fwd-pe/multiple/")
def forward_pe_multiple(tickers: str):
    ticker_list = tickers.split(",")
    data = get_multiple_fwd_pes(ticker_list)
    return {"tickers": data}
