from typing import Any, Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import StockState
from src.schemas import SentimentAnalysisSchema
from src.config import Config


def news_sentiment_node(state: StockState) -> Dict[str, Any]:
    """
    Branch C2 Node: Evaluates news sentiment from scraped Thai articles.
    Outputs SentimentAnalysisSchema (sentiment_score -100 to +100, overall_sentiment, catalysts, risks).
    """
    ticker = state.get("ticker", "UNKNOWN")
    articles: List[Dict[str, str]] = state.get("news_articles") or []

    # Edge Case: Zero news articles found
    if not articles:
        default_sentiment = SentimentAnalysisSchema(
            overall_sentiment="NEUTRAL",
            sentiment_score=0,
            key_catalysts=[],
            key_risks=[],
            news_summary=f"No recent news articles found for query '{ticker} หุ้น'. Set neutral score.",
        )
        return {"sentiment_report": default_sentiment.model_dump()}

    articles_text = "\n".join(
        [
            f"- Title: {a.get('title')} (Source: {a.get('source')}, Date: {a.get('pub_date')})"
            for a in articles
        ]
    )

    if Config.GOOGLE_API_KEY:
        try:
            llm = ChatGoogleGenerativeAI(
                model=Config.get_gemini_model(),
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.1,
            )
            structured_llm = llm.with_structured_output(SentimentAnalysisSchema)

            prompt = f"""
            You are a Thai market financial news sentiment analyst evaluating news for stock {ticker}.
            Analyze the following recent news headlines:
            {articles_text}

            Instructions:
            - Assign a sentiment score between -100 (extreme negative/crisis/fraud) and +100 (extreme positive/growth/record profits).
            - Set overall_sentiment to POSITIVE, NEUTRAL, or NEGATIVE.
            - List key catalysts (growth drivers) and key risks (legal/reputational/earnings concerns).
            - Summarize the overall news flow in news_summary.

            Return a structured SentimentAnalysisSchema.
            """

            result: SentimentAnalysisSchema = structured_llm.invoke(prompt)
            return {"sentiment_report": result.model_dump()}

        except Exception as e:
            print(f"Warning: Gemini API call failed in news_sentiment_node for {ticker}: {e}")

    # Heuristic fallback when Gemini is unavailable
    fallback_sentiment = SentimentAnalysisSchema(
        overall_sentiment="NEUTRAL",
        sentiment_score=0,
        key_catalysts=[],
        key_risks=[],
        news_summary=f"Scraped {len(articles)} news items for {ticker}. Evaluated with neutral fallback.",
    )

    return {"sentiment_report": fallback_sentiment.model_dump()}
