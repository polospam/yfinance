from fastapi import FastAPI
from forward_pe import get_forward_pe


app = FastAPI()

@app.get("/forward-pe/{ticker}")
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
