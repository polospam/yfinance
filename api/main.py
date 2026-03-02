from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.forward_pe import get_forward_pe, get_multiple_fwd_pes

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fwd-pe/{ticker}")
def forward_pe(ticker: str):
    fwd_pe = price = fwd_eps = trl_eps = None
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

@app.get("/fwd-pe/multiple/")
def forward_pe_multiple(tickers: str):
    ticker_list = tickers.split(",")
    data = get_multiple_fwd_pes(ticker_list)
    return {"tickers": data}