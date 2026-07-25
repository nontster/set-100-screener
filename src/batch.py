import os
import argparse
from datetime import datetime
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd

from src.set100_tickers import SET100_TICKERS
from src.graph import run_single_stock_screening
from src.nodes.notification import send_batch_digest


def run_batch_screening(
    tickers: List[str] = SET100_TICKERS,
    max_workers: int = 3,
    output_dir: str = ".",
    notify: bool = True,
) -> pd.DataFrame:
    """
    Execute multi-threaded batch screening across SET100 tickers,
    export Excel and UTF-8-SIG CSV reports, and dispatch notifications.
    """
    print(f"Starting SET100 Batch Screening for {len(tickers)} tickers using {max_workers} worker threads...")

    results: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(run_single_stock_screening, ticker): ticker
            for ticker in tickers
        }

        for future in tqdm(as_completed(future_to_ticker), total=len(tickers), desc="Screening SET100"):
            ticker = future_to_ticker[future]
            try:
                res = future.result()
                classification = res.get("classification_report") or {}
                mega_trends_list = classification.get("mega_trends") or []
                mega_trends_str = ", ".join(mega_trends_list) if mega_trends_list else "None"

                results.append(
                    {
                        "Ticker": res["ticker"],
                        "Recommendation": res["recommendation"],
                        "Total Score": res["total_score"],
                        "Stock Category": classification.get("category", "NEUTRAL"),
                        "Payout Safety": classification.get("payout_safety", "N/A"),
                        "Mega Trend Tags": mega_trends_str,
                        "Value Score": res["value_score"],
                        "Fraud Risk": res["fraud_risk_level"],
                        "Sentiment Score": res["sentiment_score"],
                        "Overall Sentiment": res.get("overall_sentiment", "N/A"),
                        "Executive Summary": res["executive_summary"],
                        "Classification Rationale": classification.get("rationale", ""),
                    }
                )
            except Exception as e:
                print(f"Error processing ticker {ticker}: {e}")
                results.append(
                    {
                        "Ticker": ticker,
                        "Recommendation": "REJECT",
                        "Total Score": 0.0,
                        "Stock Category": "REJECTED",
                        "Payout Safety": "UNSAFE",
                        "Mega Trend Tags": "None",
                        "Value Score": 0,
                        "Fraud Risk": "HIGH",
                        "Sentiment Score": 0,
                        "Overall Sentiment": "N/A",
                        "Executive Summary": f"Batch processing failed: {e}",
                        "Classification Rationale": "Batch failure override",
                    }
                )

    df = pd.DataFrame(results)

    # Sort results: Recommendation (PASS -> WATCHLIST -> REJECT), then Total Score DESC
    rec_order = {"PASS": 0, "WATCHLIST": 1, "REJECT": 2}
    df["rec_rank"] = df["Recommendation"].map(rec_order).fillna(3)
    df = df.sort_values(by=["rec_rank", "Total Score"], ascending=[True, False]).drop(columns=["rec_rank"])

    # Export paths
    excel_path = os.path.join(output_dir, "SET100_AI_Screening_Report.xlsx")
    csv_path = os.path.join(output_dir, "SET100_AI_Screening_Report.csv")

    # Export to Excel & UTF-8-SIG CSV
    try:
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"Saved Excel report to: {excel_path}")
    except Exception as ex_err:
        print(f"Warning: Failed to save Excel report: {ex_err}")

    try:
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"Saved CSV report to: {csv_path}")
    except Exception as csv_err:
        print(f"Warning: Failed to save CSV report: {csv_err}")

    # Dispatch Batch Digest Notification
    if notify:
        date_str = datetime.now().strftime("%Y-%m-%d")
        dict_results = df.to_dict(orient="records")
        # Format keys for notification helper
        formatted_for_notify = [
            {
                "ticker": r["Ticker"],
                "recommendation": r["Recommendation"],
                "total_score": r["Total Score"],
                "value_score": r["Value Score"],
            }
            for r in dict_results
        ]
        send_batch_digest(formatted_for_notify, date_str)

    return df


def main():
    parser = argparse.ArgumentParser(description="SET100 Batch Screener Pipeline")
    parser.add_argument("--workers", type=int, default=3, help="Number of worker threads")
    parser.add_argument("--output-dir", type=str, default=".", help="Output directory for reports")
    parser.add_argument("--no-notify", action="store_true", help="Disable push notifications")

    args = parser.parse_args()
    run_batch_screening(
        max_workers=args.workers,
        output_dir=args.output_dir,
        notify=not args.no_notify,
    )


if __name__ == "__main__":
    main()
