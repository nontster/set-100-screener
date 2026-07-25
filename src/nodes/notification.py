import requests
from typing import Any, Dict, List, Optional
from src.config import Config
from src.state import StockState


def send_telegram_message(text: str) -> bool:
    """Send Markdown formatted text via Telegram Bot API."""
    token = Config.TELEGRAM_BOT_TOKEN
    chat_id = Config.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("Notice: Telegram notification skipped (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured).")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to send Telegram alert: {e}")
        return False


def send_line_message(text: str) -> bool:
    """Send plain text push notification via LINE Messaging API."""
    token = Config.LINE_CHANNEL_ACCESS_TOKEN
    user_id = Config.LINE_USER_ID

    if not token or not user_id:
        print("Notice: LINE notification skipped (LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID not configured).")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to send LINE alert: {e}")
        return False


def format_single_stock_telegram(result: Dict[str, Any]) -> str:
    """Format single-stock PASS recommendation as Telegram Markdown."""
    ticker = result.get("ticker", "N/A")
    total_score = result.get("total_score", 0.0)
    value_score = result.get("value_score", 0)
    fraud_risk = result.get("fraud_risk_level", "N/A")
    sentiment = result.get("sentiment_score", 0)
    overall_sentiment = result.get("overall_sentiment", "N/A")
    summary = result.get("executive_summary", "")

    return (
        f"🟢 *PASS: {ticker}*\n\n"
        f"*Total Score*: {total_score}/100\n"
        f"*Value Score*: {value_score}/100\n"
        f"*Fraud Risk*: {fraud_risk}\n"
        f"*Sentiment*: {sentiment} ({overall_sentiment})\n\n"
        f"📊 *Executive Summary*\n"
        f"{summary}"
    )


def format_batch_digest_telegram(results: List[Dict[str, Any]], date_str: str) -> str:
    """Format consolidated SET100 batch screening digest as Telegram Markdown."""
    pass_list = [r for r in results if r.get("recommendation") == "PASS"]
    watchlist_list = [r for r in results if r.get("recommendation") == "WATCHLIST"]
    reject_list = [r for r in results if r.get("recommendation") == "REJECT"]

    msg = f"📋 *SET100 Daily Screening Report*\n" f"📅 {date_str} | ⏰ 17:00 ICT\n\n"

    if pass_list:
        msg += f"🟢 *PASS Stocks ({len(pass_list)})*:\n"
        for item in pass_list:
            msg += f"• *{item.get('ticker')}*: Total Score {item.get('total_score')} | Value {item.get('value_score')}\n"
        msg += "\n"
    else:
        msg += "🟢 *PASS Stocks (0)*: None qualified today.\n\n"

    msg += (
        f"📊 *Summary*: {len(pass_list)} PASS | "
        f"{len(watchlist_list)} WATCHLIST | "
        f"{len(reject_list)} REJECT"
    )

    return msg


def send_batch_digest(results: List[Dict[str, Any]], date_str: str) -> None:
    """Dispatch batch digest alert to Telegram and LINE."""
    tg_text = format_batch_digest_telegram(results, date_str)
    # Strip markdown syntax for LINE plain text
    line_text = (
        tg_text.replace("*", "").replace("• ", "- ")
    )

    send_telegram_message(tg_text)
    send_line_message(line_text)


def notification_node(state: StockState) -> Dict[str, Any]:
    """
    Notification Node: Dispatches Telegram & LINE push notifications if recommendation is PASS.
    """
    final_decision = state.get("final_decision") or {}
    recommendation = final_decision.get("recommendation")
    ticker = state.get("ticker", "N/A")

    if recommendation == "PASS":
        fraud = state.get("fraud_report") or {}
        value = state.get("value_report") or {}
        sentiment = state.get("sentiment_report") or {}

        summary_dict = {
            "ticker": ticker,
            "total_score": final_decision.get("total_score", 0.0),
            "value_score": value.get("score", 0),
            "fraud_risk_level": fraud.get("fraud_risk_level", "N/A"),
            "sentiment_score": sentiment.get("sentiment_score", 0),
            "overall_sentiment": sentiment.get("overall_sentiment", "N/A"),
            "executive_summary": final_decision.get("executive_summary", ""),
        }

        tg_msg = format_single_stock_telegram(summary_dict)
        line_msg = tg_msg.replace("*", "")

        send_telegram_message(tg_msg)
        send_line_message(line_msg)

    return {"notification_sent": recommendation == "PASS"}
