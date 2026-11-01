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


    def test_menu_guard_tracks_each_control_across_other_actions(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.last_action = ("", 0.0)
        keyboard.menu_last_ms = {}
        keyboard.blocked = 0
        keyboard.guard_var = type("Status", (), {"set": lambda self, value: None})()
        fired = []
        keyboard.activate("tool:visibility", lambda: fired.append("hide"))
        keyboard.activate("tool:MOVE ↑", lambda: fired.append("move"))
        keyboard.activate("tool:visibility", lambda: fired.append("show"))
        self.assertEqual(fired, ["hide", "move"])
        self.assertEqual(keyboard.blocked, 1)

    def test_drag_sequence_has_one_press_and_final_release(self):
        flags = ns
        start, end = (123, 456), (420, 600)
        events = ns["plan_drag_events"](start, end, (0, 0, 1920, 1080))
        self.assertEqual(len(events), 15)
        self.assertEqual(events[1][2], flags["MOUSEEVENTF_LEFTDOWN"])
        self.assertEqual(events[-1][2], flags["MOUSEEVENTF_LEFTUP"])
        self.assertEqual(sum(event[2] == flags["MOUSEEVENTF_LEFTDOWN"] for event in events), 1)
        self.assertEqual(sum(event[2] == flags["MOUSEEVENTF_LEFTUP"] for event in events), 1)
        self.assertEqual(events[0][2] & flags["MOUSEEVENTF_ABSOLUTE"], flags["MOUSEEVENTF_ABSOLUTE"])
        self.assertEqual(events[-2][2] & flags["MOUSEEVENTF_ABSOLUTE"], flags["MOUSEEVENTF_ABSOLUTE"])

    def test_drag_virtual_desktop_with_negative_origin(self):
        events = ns["plan_drag_events"]((-900, 120), (-100, 430), (-1920, 0, 3840, 1080))
        self.assertTrue(all(0 <= x <= 65535 and 0 <= y <= 65535 for x, y, _ in events))
        self.assertGreater(events[-2][0], events[0][0])

    def test_invalid_drag_screen_is_rejected(self):
        with self.assertRaises(ValueError):
            ns["plan_drag_events"]((1, 1), (3, 3), (0, 0, 0, 0))

    def test_cancel_invalidates_pending_capture(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.mouse_target_seq = 4
        keyboard.mouse_target_kind = "right"
        keyboard._cancel_mouse_targeting()
        self.assertIsNone(keyboard.mouse_target_kind)
        self.assertEqual(keyboard.mouse_target_seq, 5)

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
