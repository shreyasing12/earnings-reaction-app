import yfinance as yf
import pandas as pd
import datetime as dt


def get_next_trading_close(stock, report_date):
    start = report_date
    end = report_date + dt.timedelta(days=7)
    hist = stock.history(start=start, end=end)

    if len(hist) < 2:
        return None, None

    earnings_close = hist["Close"].iloc[0]
    next_day_close = hist["Close"].iloc[1]

    pct_change = ((next_day_close - earnings_close) / earnings_close) * 100

    if pct_change > 1:
        reaction = "Positive"
    elif pct_change < -1:
        reaction = "Negative"
    else:
        reaction = "Flat"

    return round(pct_change, 2), reaction


def get_earnings_analysis(ticker, limit=4):
    stock = yf.Ticker(ticker)

    # Primary method
    try:
        earnings_df = stock.get_earnings_dates(limit=limit)
    except Exception:
        earnings_df = None

    # Fallback if Yahoo blocks earnings dates
    if earnings_df is None or earnings_df.empty:
        try:
            qe = stock.quarterly_earnings
            if qe is None or qe.empty:
                return pd.DataFrame()

            qe = qe.reset_index().head(limit)
            qe.rename(columns={"Earnings": "EPS Actual"}, inplace=True)
            qe["EPS Estimate"] = None
            qe["Earnings Date"] = qe["index"]

            earnings_df = qe
        except Exception:
            return pd.DataFrame()

    results = []

    for idx, row in earnings_df.iterrows():
        if "Earnings Date" in row:
            report_date = pd.to_datetime(row["Earnings Date"]).date()
        else:
            report_date = idx.date()

        actual = row.get("EPS Actual")
        estimate = row.get("EPS Estimate")

        if pd.notna(actual) and pd.notna(estimate) and estimate != 0:
            beat_amt = actual - estimate
            beat_pct = (beat_amt / estimate) * 100
        else:
            beat_amt, beat_pct = None, None

        move, reaction = get_next_trading_close(stock, report_date)

        results.append({
            "Report Date": report_date,
            "Reported EPS": actual,
            "Consensus EPS": estimate,
            "Beat Amount": beat_amt,
            "Beat %": round(beat_pct, 2) if beat_pct else None,
            "Stock Move %": move,
            "Reaction": reaction
        })

    return pd.DataFrame(results)
