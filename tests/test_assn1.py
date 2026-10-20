"""Independent behavioral checks for the stair game (standard library only)."""

import contextlib
import importlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
assn1 = importlib.import_module("assn1")


class WinnerTests(unittest.TestCase):
    def test_all_nine_choice_pairs(self):
        expected = {
            (1, 1): "tie", (1, 2): "computer", (1, 3): "player",
            (2, 1): "player", (2, 2): "tie", (2, 3): "computer",
            (3, 1): "computer", (3, 2): "player", (3, 3): "tie",
        }
        for choices, winner in expected.items():
            with self.subTest(choices=choices):
                self.assertEqual(assn1.determine_winner(*choices), winner)

    def test_computer_uses_inclusive_random_range(self):
        for choice in (1, 2, 3):
            with self.subTest(choice=choice):
                with patch("random.randint", return_value=choice) as random_choice:
                    self.assertEqual(assn1.get_computer_choice(), choice)
                random_choice.assert_called_once_with(1, 3)


class PositionTests(unittest.TestCase):
    def test_winning_choice_determines_number_of_steps(self):
        for move in (1, 2, 3):
            with self.subTest(move=move):
                self.assertEqual(assn1.update_position(10, move), 10 - move)

    def test_exact_landing_is_zero(self):
        for position in (1, 2, 3):
            with self.subTest(position=position):
                self.assertEqual(assn1.update_position(position, position), 0)

    def test_overshoot_is_clamped_to_zero(self):
        self.assertEqual(assn1.update_position(1, 2), 0)
        self.assertEqual(assn1.update_position(1, 3), 0)
        self.assertEqual(assn1.update_position(2, 3), 0)


class StairOutputTests(unittest.TestCase):
    def capture_stairs(self, total, player, computer):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            assn1.print_stairs(total, player, computer)
        return output.getvalue()

    def test_initial_stairs_match_documented_example(self):
        output = self.capture_stairs(5, 5, 5)
        expected = (
            "○-Player ●-Computer ◐-Player & Computer\n\n"
            "[ 5]◐\n[ 4]▨\n[ 3]▨▨\n[ 2]▨▨▨\n"
            "[ 1]▨▨▨▨\n[ 0]▨▨▨▨▨\n\n"
            "Player = 5, Computer = 5"
        )
        self.assertEqual(output.strip(), expected)

    def test_separate_positions_include_top_and_ground(self):
        output = self.capture_stairs(5, 0, 5)
        self.assertIn("[ 5]●\n", output)
        self.assertIn("[ 0]▨▨▨▨▨○\n", output)
        self.assertIn("Player = 0, Computer = 5", output)
        self.assertNotIn("[ 5]◐", output)

    def test_double_digit_labels_and_computer_at_ground(self):
        output = self.capture_stairs(20, 19, 0)
        self.assertIn("[20]\n", output)
        self.assertIn("[19]▨○\n", output)
        self.assertIn("[ 0]" + "▨" * 20 + "●\n", output)
        stair_lines = [line for line in output.splitlines() if line.startswith("[")]
        self.assertEqual(len(stair_lines), 21)

    def test_shared_middle_position_uses_combined_marker(self):
        output = self.capture_stairs(5, 3, 3)
        self.assertIn("[ 3]▨▨◐\n", output)
        self.assertNotIn("[ 3]▨▨○●", output)


class PlayerInputTests(unittest.TestCase):
    def test_each_valid_choice_is_accepted(self):
        for choice in (0, 1, 2, 3):
            with self.subTest(choice=choice):
                with patch("builtins.input", return_value=str(choice)) as get_input:
                    self.assertEqual(assn1.get_player_choice(), choice)
                get_input.assert_called_once()

    def test_invalid_integer_choices_repeat_until_valid(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with patch("builtins.input", side_effect=["-1", "4", "123", "2"]) as get_input:
                self.assertEqual(assn1.get_player_choice(), 2)
        self.assertEqual(output.getvalue().count("Invalid input!"), 3)
        self.assertEqual(get_input.call_count, 4)


class GameFlowTests(unittest.TestCase):
    def run_game(self, replies, computer_choices=()):
        output = io.StringIO()
        prompts = []
        replies = iter(replies)

        def respond(prompt=""):
            prompts.append(prompt)
            return next(replies)

        with contextlib.redirect_stdout(output):
            with patch("builtins.input", side_effect=respond):
                with patch.object(assn1, "get_computer_choice", side_effect=computer_choices) as computer:
                    assn1.play_game()
        return output.getvalue(), prompts, computer

    def test_step_input_rejects_both_out_of_range_sides(self):
        output, prompts, computer = self.run_game(["4", "21", "-10", "5", "0", "yes"])
        self.assertEqual(output.count("Invalid input!"), 3)
        self.assertIn("Player = 5, Computer = 5", output)
        self.assertEqual(sum("Enter the number of steps" in p for p in prompts), 4)
        self.assertIn("=== Rock-Paper-Scissors Stair Game ===", output)
        computer.assert_not_called()

    def test_upper_step_boundary_is_accepted(self):
        output, prompts, computer = self.run_game(["20", "0", "yes"])
        self.assertNotIn("Invalid input!", output)
        self.assertIn("Player = 20, Computer = 20", output)
        self.assertEqual(sum("Enter the number of steps" in p for p in prompts), 1)
        computer.assert_not_called()

    def test_quit_reprompts_invalid_confirmation_and_accepts_mixed_case(self):
        output, prompts, computer = self.run_game(["5", "0", "yse", "y", "YeS"])
        self.assertEqual(output.count("Invalid input!"), 2)
        self.assertEqual(sum("Are you sure you want to quit? (yes/no): " in p for p in prompts), 3)
        self.assertTrue(output.rstrip().endswith("Game Over!"))
        self.assertNotIn("Finished!", output)
        computer.assert_not_called()

    def test_each_quit_is_confirmed_again_after_canceling(self):
        output, prompts, computer = self.run_game(["5", "0", "NO", "0", "nO", "0", "YES"])
        self.assertEqual(sum("Are you sure you want to quit?" in p for p in prompts), 3)
        self.assertEqual(sum("Rock (1), Paper (2), Scissors (3), Quit (0): " in p for p in prompts), 3)
        self.assertEqual(output.count("Game Over!"), 1)
        computer.assert_not_called()

    def test_invalid_choices_and_canceled_quit_do_not_draw_random_choice(self):
        output, prompts, computer = self.run_game(
            ["5", "4", "-1", "0", "no", "1", "", "0", "yes"], [3]
        )
        self.assertEqual(output.count("Invalid input!"), 2)
        computer.assert_called_once_with()
        self.assertIn("Player = 4, Computer = 5", output)

    def test_player_can_finish_with_overshoot_and_no_extra_input(self):
        output, prompts, computer = self.run_game(["5", "3", "", "3", ""], [2, 2])
        self.assertEqual(computer.call_count, 2)
        self.assertIn("Player = 2, Computer = 5", output)
        self.assertIn("Player = 0, Computer = 5", output)
        self.assertIn("[ 0]▨▨▨▨▨○", output)
        self.assertTrue(output.rstrip().endswith("Finished! PLAYER WINS!"))
        self.assertEqual(sum("Rock (1), Paper (2), Scissors (3), Quit (0): " in p for p in prompts), 2)
        self.assertEqual(sum("Press ENTER to continue..." in p for p in prompts), 2)

    def test_computer_can_finish_with_overshoot_and_no_extra_input(self):
        output, prompts, computer = self.run_game(["5", "2", "", "2", ""], [3, 3])
        self.assertEqual(computer.call_count, 2)
        self.assertIn("Player = 5, Computer = 2", output)
        self.assertIn("Player = 5, Computer = 0", output)
        self.assertIn("[ 0]▨▨▨▨▨●", output)
        self.assertTrue(output.rstrip().endswith("Finished! COMPUTER WINS!"))
        self.assertEqual(sum("Rock (1), Paper (2), Scissors (3), Quit (0): " in p for p in prompts), 2)

    def test_tie_does_not_change_either_position(self):
        output, prompts, computer = self.run_game(["5", "2", "", "0", "yes"], [2])
        self.assertEqual(output.count("Player = 5, Computer = 5"), 2)
        self.assertIn("Player: Paper", output)
        self.assertIn("Computer: Paper", output)
        self.assertIn("Tie!", output)
        self.assertEqual(sum("Press ENTER to continue..." in p for p in prompts), 1)
        computer.assert_called_once_with()

    def test_player_and_computer_use_their_own_winning_values(self):
        output, prompts, computer = self.run_game(
            ["10", "1", "", "1", "", "2", "", "0", "yes"], [3, 2, 2]
        )
        self.assertIn("Player: Rock", output)
        self.assertIn("Computer: Scissors", output)
        self.assertIn("Player wins!", output)
        self.assertIn("Player = 9, Computer = 10", output)
        self.assertIn("Computer wins!", output)
        self.assertIn("Player = 9, Computer = 8", output)
        self.assertEqual(output.count("Player = 9, Computer = 8"), 2)
        self.assertEqual(computer.call_count, 3)

    def test_movement_and_redraw_happen_after_enter(self):
        events = []
        replies = iter(["5", "1", "", "0", "yes"])
        output = io.StringIO()
        original_update = assn1.update_position
        original_stairs = assn1.print_stairs

        def respond(prompt=""):
            if "Press ENTER" in prompt:
                events.append("enter")
                self.assertIn("Player wins!", output.getvalue())
                self.assertEqual(events, ["stairs", "enter"])
            return next(replies)

        def update(*args):
            events.append("update")
            return original_update(*args)

        def stairs(*args):
            events.append("stairs")
            return original_stairs(*args)

        with contextlib.redirect_stdout(output):
            with patch("builtins.input", side_effect=respond):
                with patch.object(assn1, "get_computer_choice", return_value=3):
                    with patch.object(assn1, "update_position", side_effect=update):
                        with patch.object(assn1, "print_stairs", side_effect=stairs):
                            assn1.play_game()
        self.assertEqual(events, ["stairs", "enter", "update", "stairs"])


class CommandLineTests(unittest.TestCase):
    def test_real_python_process_starts_and_quits_successfully(self):
        result = subprocess.run(
            [sys.executable, "assn1.py"], cwd=ROOT, input="5\n0\nyes\n",
            text=True, capture_output=True, timeout=5, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("[ 5]◐", result.stdout)
        self.assertIn("Are you sure you want to quit? (yes/no): ", result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith("Game Over!"))

    def test_import_has_no_interactive_side_effects(self):
        result = subprocess.run(
            [sys.executable, "-c", "import assn1"], cwd=ROOT,
            input="", text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
