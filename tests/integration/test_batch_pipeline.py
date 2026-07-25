import os
import pytest
from src.batch import run_batch_screening


def test_batch_screening_pipeline_small_batch(tmp_path):
    """Integration test for batch screening runner and Excel/CSV export."""
    test_tickers = ["CPALL", "PTT"]
    output_dir = str(tmp_path)

    df = run_batch_screening(
        tickers=test_tickers,
        max_workers=2,
        output_dir=output_dir,
        notify=False,
    )

    assert len(df) == 2
    assert "Ticker" in df.columns
    assert "Recommendation" in df.columns

    excel_file = os.path.join(output_dir, "SET100_AI_Screening_Report.xlsx")
    csv_file = os.path.join(output_dir, "SET100_AI_Screening_Report.csv")

    assert os.path.exists(excel_file)
    assert os.path.exists(csv_file)
