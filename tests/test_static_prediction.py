"""Portable regression tests for Firefly's optional static language table.

Run independently of Tk, Windows, and the Amazon/AnyWare input chain:
    python -m unittest discover -s tests -p test_static_prediction.py
"""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from firefly_prediction import StaticNextWords


class StaticPredictionTests(unittest.TestCase):
    def test_bundled_model_is_real_and_useful(self):
        model = StaticNextWords.load(str(ROOT / "data" / "en_context_bigrams.tsv"))
        self.assertGreaterEqual(len(model.rows), 4000)
        candidates = model.candidates("you")
        self.assertGreaterEqual(len(candidates), 3)
        self.assertEqual(candidates[0][0], "can")
        self.assertEqual(model.candidates("how", "t")[0][0], "to")

    def test_prefix_gating_and_relative_order(self):
        model = StaticNextWords({"you": (("can", 50), ("have", 25), ("are", 10))})
        self.assertEqual(model.candidates("YOU", "ha"), (("have", 25),))
        self.assertEqual(model.candidates("you", "have"), ())
        self.assertGreater(model.strength("you", "can"),
                           model.strength("you", "are"))
        self.assertEqual(model.strength("unknown", "can"), 0.0)

    def test_missing_or_corrupt_file_is_not_an_input_blocker(self):
        self.assertEqual(StaticNextWords.load("/nonexistent/firefly-table").rows, {})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.tsv"
            path.write_text("broken row\\nhello\\tthere:bad!!\\nknown\\tgood:2\\n", encoding="utf-8")
            model = StaticNextWords.load(str(path))
            self.assertEqual(model.candidates("known"), (("good", 2),))
            self.assertEqual(model.candidates("hello"), ())


if __name__ == "__main__":
    unittest.main()
