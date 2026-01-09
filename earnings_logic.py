def get_earnings_analysis(ticker, limit=4):
    stock = yf.Ticker(ticker)

    try:
        earnings_df = stock.get_earnings_dates(limit=limit)
    except Exception:
        return pd.DataFrame()

    if earnings_df is None or earnings_df.empty:
        return pd.DataFrame()

    results = []

    for idx, row in earnings_df.iterrows():
        # Earnings date may be index OR column → handle safely
        if isinstance(idx, pd.Timestamp):
            report_date = idx.date()
        else:
            report_date = pd.to_datetime(row.get("Earnings Date")).date()

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

