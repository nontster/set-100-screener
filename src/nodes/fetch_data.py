import yfinance as yf
from typing import Any, Dict
from src.state import StockState
from src.cache import get_cached_data, set_cached_data


def fetch_data_node(state: StockState) -> Dict[str, Any]:
    """
    Entry Node: Fetches financial metrics for Thai stock ticker using yfinance.
    Appends .BK suffix, uses 12-hour local JSON cache, and tags missing fields cleanly.
    """
    raw_ticker = state.get("ticker", "").strip().upper()
    if not raw_ticker:
        return {"error": "No ticker provided in StockState"}

    # Strip .BK suffix if provided by user to normalize key name
    clean_ticker = raw_ticker[:-3] if raw_ticker.endswith(".BK") else raw_ticker
    full_ticker = f"{clean_ticker}.BK"

    # Check 12-hour file cache
    cached_data = get_cached_data(clean_ticker)
    if cached_data:
        return {"ticker": clean_ticker, "raw_data": cached_data}

    # Fetch from yfinance
    try:
        stock = yf.Ticker(full_ticker)
        info = stock.info or {}

        # Safely extract metrics from info dict
        pe_ratio = info.get("trailingPE")
        pb_ratio = info.get("priceToBook")

        roe_raw = info.get("returnOnEquity")
        roe = roe_raw * 100 if roe_raw is not None else None

        de_raw = info.get("debtToEquity")
        de_ratio = de_raw / 100 if de_raw is not None else None

        div_raw = info.get("dividendYield")
        div_yield = div_raw * 100 if div_raw is not None else None

        current_ratio = info.get("currentRatio")

        # Safely extract cash flow items
        free_cash_flow = None
        operating_cash_flow = None
        net_income = None

        try:
            cf = stock.cashflow
            if cf is not None and not cf.empty:
                if "Free Cash Flow" in cf.index:
                    free_cash_flow = float(cf.loc["Free Cash Flow"].iloc[0])
                if "Operating Cash Flow" in cf.index:
                    operating_cash_flow = float(cf.loc["Operating Cash Flow"].iloc[0])
        except Exception as cf_err:
            print(f"Warning: Cashflow extraction for {full_ticker} failed: {cf_err}")

        # Safely extract financials (income statement) items
        try:
            fin = stock.financials
            if fin is not None and not fin.empty:
                if "Net Income" in fin.index:
                    net_income = float(fin.loc["Net Income"].iloc[0])
        except Exception as fin_err:
            print(f"Warning: Financials extraction for {full_ticker} failed: {fin_err}")

        raw_data: Dict[str, Any] = {
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "roe": roe,
            "de_ratio": de_ratio,
            "dividend_yield": div_yield,
            "current_ratio": current_ratio,
            "free_cash_flow": free_cash_flow,
            "operating_cash_flow": operating_cash_flow,
            "net_income": net_income,
            "company_name": info.get("longName") or info.get("shortName") or clean_ticker,
            "sector": info.get("sector") or "N/A",
            "industry": info.get("industry") or "N/A",
        }

        # Cache data locally
        set_cached_data(clean_ticker, raw_data)

        return {"ticker": clean_ticker, "raw_data": raw_data}

    except Exception as e:
        error_msg = f"Failed to fetch data for {full_ticker}: {str(e)}"
        print(error_msg)
        return {
            "ticker": clean_ticker,
            "raw_data": {},
            "error": error_msg,
        }
