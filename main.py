from fastapi import FastAPI
from forward_pe import get_forward_pe
from prices import get_stock_price


app = FastAPI()

@app.get("/forward-pe/{ticker}")
def forward_pe(ticker: str):
    try:
        fwd_pe = get_forward_pe(ticker)
        price = get_stock_price(ticker)
    except:
        pass

    return {
        "ticker": ticker.upper(),
        "price": price,
        "forwardPE": fwd_pe
    }
