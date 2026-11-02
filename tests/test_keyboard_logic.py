"""Fast, non-UI Windows smoke checks for Firefly's remote-critical behavior."""
import runpy
import time
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

    def test_option_guard_tracks_each_control_across_other_actions(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.last_action = ("", 0.0)
        keyboard.menu_last_ms = {}
        keyboard.option_last_ms = {}
        keyboard.blocked = 0
        keyboard.guard_var = type("Status", (), {"set": lambda self, value: None})()
        fired = []
        keyboard.activate("option:CTRL", lambda: fired.append("ctrl-on"))
        keyboard.activate("option:MODE", lambda: fired.append("symbols"))
        keyboard.activate("option:CTRL", lambda: fired.append("ctrl-off"))
        self.assertEqual(fired, ["ctrl-on", "symbols"])
        self.assertEqual(keyboard.blocked, 1)

    def test_repeatable_options_use_shorter_guard(self):
        self.assertLess(ns["REPEAT_OPTION_GUARD_MS"], ns["OPTION_GUARD_MS"])
        self.assertIn("BACK", ns["REPEAT_OPTION_SUFFIXES"])
        self.assertNotIn("CTRL", ns["REPEAT_OPTION_SUFFIXES"])

    def test_pointer_bursts_map_only_when_axis_aligned(self):
        direction = ns["pointer_nav_direction"]
        self.assertEqual(direction(12, 2), "Right")
        self.assertEqual(direction(-12, 3), "Left")
        self.assertEqual(direction(1, -8), "Up")
        self.assertEqual(direction(2, 9), "Down")
        self.assertIsNone(direction(2, 0))
        self.assertIsNone(direction(8, 7))

    def test_captured_remote_stream_stays_snapped_and_repeats_slowly(self):
        """Replay the accelerated Right stream captured from the real remote."""
        decide = ns["pointer_nav_decision"]
        # Actual 15:17:36-37 capture: +8,+103,+4,+41,+2,+8 over 1.257s.
        samples = [
            (0.000, 8, 0), (0.280, 103, 0), (0.590, 4, 0),
            (0.714, 41, 0), (0.917, 2, 0), (1.257, 8, 0),
        ]
        active, lock_until, last_step = None, 0.0, -99.0
        actions = []
        for now, dx, dy in samples:
            action, direction, lock_until = decide(
                dx, dy, now, active, lock_until, last_step,
            )
            actions.append(action)
            if action == "navigate":
                active, last_step = direction, now
        self.assertEqual(actions[0], "navigate")
        self.assertNotIn("hover", actions)
        self.assertLess(actions.count("navigate"), len(samples))
        self.assertGreaterEqual(actions.count("snap"), 3)

    def test_direction_change_is_immediate_during_remote_stream(self):
        decide = ns["pointer_nav_decision"]
        action, active, lock_until = decide(12, 0, 10.0, None, 0.0, 0.0)
        self.assertEqual((action, active), ("navigate", "Right"))
        action, active, _ = decide(-12, 0, 10.1, active, lock_until, 10.0)
        self.assertEqual((action, active), ("navigate", "Left"))

    def test_hover_enter_cannot_steal_active_remote_snap(self):
        keyboard = Firefly.__new__(Firefly)
        selected, drifted = object(), object()
        keyboard.nav_selected = selected
        keyboard.pointer_nav_lock_until = time.monotonic() + 1.0
        keyboard.remote_nav_until = keyboard.pointer_nav_lock_until
        keyboard.pointer_nav_direction_active = "Right"
        changed = []
        keyboard._select_nav_button = changed.append
        keyboard._on_button_enter(drifted)
        self.assertEqual(changed, [])
        self.assertIs(keyboard.nav_selected, selected)

    def test_selected_key_uses_full_lime_fill(self):
        class Button:
            def __init__(self):
                self.options = {}
                self._firefly_base_style = {}
            def winfo_exists(self):
                return True
            def configure(self, **options):
                self.options.update(options)
        keyboard = Firefly.__new__(Firefly)
        keyboard.nav_selected = None
        button = Button()
        keyboard._select_nav_button(button)
        self.assertEqual(button.options["bg"], ns["LIME"])
        self.assertEqual(button.options["fg"], ns["BG"])
        self.assertEqual(button.options["relief"], "solid")

    def test_global_ok_guard_blocks_next_same_point_activation(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.last_ok_press = (None, 0.0)
        keyboard.suppress_ok_once = False
        keyboard.suppress_ok_until = 0.0
        keyboard.blocked = 0
        keyboard.guard_var = type("Status", (), {"set": lambda self, value: None})()
        event = type("Event", (), {"x_root": 400, "y_root": 500})()
        keyboard._on_pointer_press(event)
        keyboard._on_pointer_press(event)
        fired = []
        keyboard.activate("key:a", lambda: fired.append("a"))
        self.assertEqual(fired, [])
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

    def test_static_context_suggestions_extend_existing_ranker(self):
        # Preserve the old personal/noisy-word safeguards while adding a
        # separate general-language prior, without a large runtime model.
        static = ns["StaticNextWords"]
        self.assertIsNotNone(static)
        keyboard = Firefly.__new__(Firefly)
        keyboard.corpus_counts = {"can": 1000, "are": 1000, "the": 1000000}
        keyboard.completion_index = {}
        keyboard.words_by_first = {}
        keyboard.learned_words = {}
        keyboard.next_words = {}
        keyboard.current_word = ""
        keyboard.previous_word = "you"
        keyboard.static_next_words = static({"you": (("can", 100), ("are", 20))})
        keyboard.suggestion_buttons = []
        keyboard._update_suggestions()
        self.assertEqual(keyboard.suggestions[:2], ["can", "are"])
        self.assertNotIn("the", keyboard.suggestions[:2])

    def test_next_word_prefers_specific_association_over_global_filler(self):
        # Real failure found in a user-flow sample: "open source" was displaced
        # by "and" and "for" because unigrams dominated P(next|open).
        static = ns["StaticNextWords"]
        keyboard = Firefly.__new__(Firefly)
        keyboard.corpus_counts = {"to": 2000, "source": 100, "and": 1000000}
        keyboard.completion_index = {}
        keyboard.words_by_first = {}
        keyboard.learned_words = {}
        keyboard.next_words = {}
        keyboard.current_word = ""
        keyboard.previous_word = "open"
        keyboard.static_next_words = static({"open": (
            ("to", 100), ("source", 90), ("and", 70),
        )})
        keyboard.suggestion_buttons = []
        keyboard._update_suggestions()
        self.assertEqual(keyboard.suggestions[:2], ["to", "source"])

    def test_sentence_end_drops_static_context_but_space_preserves_it(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.current_word = ""
        keyboard.previous_word = ""
        keyboard.learned_words = {}
        keyboard.next_words = {}
        keyboard._update_suggestions = lambda: None
        keyboard._track_text("you ")
        self.assertEqual(keyboard.previous_word, "you")
        keyboard._track_text("can.")
        self.assertEqual(keyboard.previous_word, "")

    def test_single_noisy_fragment_is_not_promoted_to_suggestion(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.corpus_counts = {"cat": 1000, "car": 500}
        keyboard.completion_index = {"ca": ["cat", "car"]}
        keyboard.words_by_first = {"c": ["cat", "car"]}
        keyboard.learned_words = {"caxbroken": 1}
        keyboard.next_words = {"hello": {"caxbroken": 1}}
        keyboard.current_word = "ca"
        keyboard.previous_word = "hello"
        keyboard.suggestion_buttons = []
        keyboard._update_suggestions()
        self.assertEqual(keyboard.suggestions[:2], ["cat", "car"])
        self.assertNotIn("caxbroken", keyboard.suggestions)

    def test_repeated_custom_word_becomes_available(self):
        keyboard = Firefly.__new__(Firefly)
        keyboard.corpus_counts = {}
        keyboard.completion_index = {}
        keyboard.words_by_first = {}
        keyboard.learned_words = {"codex": 2}
        keyboard.next_words = {}
        keyboard.current_word = "cod"
        keyboard.previous_word = ""
        keyboard.suggestion_buttons = []
        keyboard._update_suggestions()
        self.assertIn("codex", keyboard.suggestions)


if __name__ == "__main__":
    unittest.main()



