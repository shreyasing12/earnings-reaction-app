import streamlit as st
import pandas as pd
from earnings_logic import get_earnings_analysis

st.set_page_config(page_title="Earnings Reaction Analyzer", layout="wide")
st.title("📈 Earnings Reaction Analyzer")
st.caption("Analyze EPS beats/misses and next-day stock reactions")

# User inputs
ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
quarters = st.slider("Number of past earnings to analyze", 1, 8, 4)

if st.button("Analyze"):
    with st.spinner("Fetching earnings data..."):
        try:
            df = get_earnings_analysis(ticker, quarters)

            if df.empty:
                st.warning("No earnings data found for this ticker.")
            else:
                # Display table
                st.dataframe(df, use_container_width=True)

                # Metrics
                st.subheader("📊 Insights")
                avg_reaction = round(df["Stock Move %"].mean(), 2) if df["Stock Move %"].notna().any() else None
                st.metric("Average Stock Reaction %", avg_reaction)

                # Bar chart
                chart_data = df.set_index("Report Date")["Stock Move %"]
                st.bar_chart(chart_data)

                # CSV download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{ticker}_earnings_analysis.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"Error: {e}")
