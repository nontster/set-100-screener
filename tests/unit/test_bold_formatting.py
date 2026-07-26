import unittest
from src.nodes.final_reporter import enforce_bold_decisions


class TestBoldFormatting(unittest.TestCase):
    """Test suite for enforce_bold_decisions regex post-processor."""

    def test_enforce_bold_unbolded_reject(self):
        text = "We issue a definitive REJECT recommendation for EA."
        expected = "We issue a definitive **REJECT** recommendation for EA."
        self.assertEqual(enforce_bold_decisions(text), expected)

    def test_already_bolded_reject_remains_intact(self):
        text = "We issue a definitive **REJECT** recommendation for EA."
        expected = "We issue a definitive **REJECT** recommendation for EA."
        self.assertEqual(enforce_bold_decisions(text), expected)

    def test_enforce_bold_pass_and_watchlist(self):
        text = "The overall rating is PASS, with watchlist status set to WATCHLIST."
        expected = "The overall rating is **PASS**, with watchlist status set to **WATCHLIST**."
        self.assertEqual(enforce_bold_decisions(text), expected)

    def test_thai_text_with_decision_keyword(self):
        text = "เราออกคำแนะนำ REJECT อย่างเด็ดขาดสำหรับบริษัท EA score 7.0/100"
        expected = "เราออกคำแนะนำ **REJECT** อย่างเด็ดขาดสำหรับบริษัท EA score 7.0/100"
        self.assertEqual(enforce_bold_decisions(text), expected)

    def test_numerical_integrity_and_currency_preservation(self):
        text = "Loss of -4.86 billion THB alongside operating cash flow of +8.44 billion THB and D/E ratio of 1.42 with REJECT status."
        expected = "Loss of -4.86 billion THB alongside operating cash flow of +8.44 billion THB and D/E ratio of 1.42 with **REJECT** status."
        self.assertEqual(enforce_bold_decisions(text), expected)


if __name__ == "__main__":
    unittest.main()
