"""Fast, non-UI Windows smoke checks for Firefly's remote-critical behavior."""
import runpy
import unittest

ns = runpy.run_path("firefly_keyboard.pyw", run_name="firefly_test_module")
Firefly = ns["FireflyKeyboard"]


class FireflyLogicTests(unittest.TestCase):
    def test_dock_never_uses_half_the_screen(self):
        self.assertLessEqual(ns["MAX_DOCK_FRACTION"], 0.34)

    def test_shift_key_action_follows_current_mode(self):
        keyboard = Firefly.__new__(Firefly)
        received = []
        keyboard.activate = lambda signature, action: action()
        keyboard.key_action = received.append
        keyboard.shifted = False
        keyboard._invoke_layout_key("a")
        keyboard.shifted = True
        keyboard._invoke_layout_key("a")
        self.assertEqual(received, ["a", "A"])

    def test_local_prefix_dictionary(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.corpus_counts = {}
        keyboard.completion_index = {}
        keyboard.words_by_first = {}
        keyboard._load_offline_dictionary()
        self.assertGreaterEqual(len(keyboard.corpus_counts), 8500)
        self.assertIn("com", keyboard.completion_index)
        keyboard.learned_words = {}
        keyboard.next_words = {}
        keyboard.current_word = "comp"
        keyboard.previous_word = ""
        keyboard.suggestion_buttons = []
        keyboard._update_suggestions()
        self.assertTrue(any(w.startswith("comp") and w != "comp"
                            for w in keyboard.suggestions))


if __name__ == "__main__":
    unittest.main()
