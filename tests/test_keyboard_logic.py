"""Fast, non-UI Windows smoke checks for Firefly's remote-critical behavior."""
import runpy
import unittest

ns = runpy.run_path("firefly_keyboard.pyw", run_name="firefly_test_module")
Firefly = ns["FireflyKeyboard"]


class FireflyLogicTests(unittest.TestCase):
    def test_dock_is_comfortable_but_still_below_half_screen(self):
        self.assertGreater(ns["DEFAULT_DOCK_FRACTION"], 0.40)
        self.assertLess(ns["MAX_DOCK_FRACTION"], 0.50)
        self.assertLessEqual(ns["DEFAULT_DOCK_FRACTION"], ns["MAX_DOCK_FRACTION"])

    def test_keyboard_position_clamps_to_both_work_area_edges(self):
        clamp = ns["clamp_dock_top"]
        self.assertEqual(clamp(-200, 20, 820, 360), 20)
        self.assertEqual(clamp(700, 20, 820, 360), 460)
        self.assertEqual(clamp(150, 20, 820, 360), 150)
        self.assertEqual(clamp(100, 20, 120, 180), 20)

    def test_move_step_can_reach_screen_top_incrementally(self):
        clamp = ns["clamp_dock_top"]
        y = 450
        for _ in range(10):
            y = clamp(y - ns["MOVE_STEP_PX"], 0, 800, 350)
        self.assertEqual(y, 0)

    def test_shift_key_action_follows_current_mode(self):
        keyboard = Firefly.__new__(Firefly)
        received = []
        keyboard.activate = lambda signature, action: action()
        keyboard.key_action = received.append
        keyboard.shifted = False
        keyboard._invoke_layout_key("a")
        keyboard.shifted = True
        keyboard._invoke_layout_key("a")
        # A prebuilt button can still capture uppercase action after the
        # one-shot toggle turns off; it must then send lowercase.
        keyboard.shifted = False
        keyboard._invoke_layout_key("A")
        self.assertEqual(received, ["a", "A", "a"])

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
