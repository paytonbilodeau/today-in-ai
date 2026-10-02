import unittest
from datetime import date
from pathlib import Path

from scripts.today_in_ai_prepare import (
    manifest,
    parse_stories,
    validate_copy,
)


def words(count: int, seed: str) -> str:
    return " ".join([seed] * count) + "."


class TodayInAIPrepareTests(unittest.TestCase):
    def test_manifests_use_postiz_with_native_copy_and_same_image(self) -> None:
        copy = "Today in AI: August 28\n\nModels Learn Patience:\n\nComplete copy."
        image = Path("/tmp/today-in-ai-final.png")

        linkedin = manifest(copy, image, "linkedin")
        x = manifest(copy, image, "x")

        self.assertEqual(linkedin["targets"]["linkedin"]["method"], "postiz")
        self.assertEqual(x["targets"]["x"]["method"], "postiz")
        self.assertEqual(linkedin["publication"], "today-in-ai")
        self.assertEqual(x["publication"], "today-in-ai")
        self.assertEqual(linkedin["targets"]["linkedin"]["caption"], copy)
        self.assertEqual(x["targets"]["x"]["caption"], copy)
        self.assertEqual(linkedin["media"]["images"], [str(image)])
        self.assertEqual(x["media"]["images"], [str(image)])
        self.assertNotIn("who_can_reply", linkedin["targets"]["linkedin"])
        self.assertEqual(x["targets"]["x"]["who_can_reply"], "everyone")
        self.assertEqual(x["targets"]["x"]["thread_policy"], "single")

    def test_three_word_headings_and_story_lengths_pass(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: July 29",
                "Models Read Rooms:",
                words(100, "lead"),
                "Browsers Learned Memory:",
                words(55, "browser"),
                "Robots Fold Laundry:",
                words(55, "robot"),
            ]
        )
        result = validate_copy(copy, date(2026, 7, 29))
        self.assertEqual(result["story_count"], 3)
        self.assertEqual(result["story_words"], [100, 55, 55])
        self.assertEqual(
            [heading for heading, _ in parse_stories(copy)],
            [
                "Models Read Rooms:",
                "Browsers Learned Memory:",
                "Robots Fold Laundry:",
            ],
        )

    def test_short_lead_fails_new_standard(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: July 29",
                "Models Read Rooms:",
                words(70, "lead"),
                "Browsers Learned Memory:",
                words(55, "browser"),
                "Robots Fold Laundry:",
                words(55, "robot"),
                "Search Found Context:",
                words(55, "search"),
            ]
        )
        with self.assertRaisesRegex(SystemExit, "lead story"):
            validate_copy(copy, date(2026, 7, 29))

    def test_slop_phrase_fails(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: July 29",
                "Models Read Rooms:",
                words(98, "lead") + " Let's dive in.",
                "Browsers Learned Memory:",
                words(45, "browser"),
                "Robots Fold Laundry:",
                words(45, "robot"),
            ]
        )
        with self.assertRaisesRegex(SystemExit, "banned text"):
            validate_copy(copy, date(2026, 7, 29))

    def test_one_story_adaptive_format_passes(self) -> None:
        body = [words(40, f"paragraph{number}") for number in range(4)]
        copy = "\n\n".join(
            ["Today in AI: August 7", "Models Learn Patience:", *body]
        )
        result = validate_copy(copy, date(2026, 8, 7))
        self.assertEqual(result["story_count"], 1)
        self.assertEqual(result["story_words"], [160])

    def test_two_story_adaptive_format_passes(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: August 7",
                "Models Learn Patience:",
                words(55, "leadone"),
                words(55, "leadtwo"),
                "Browsers Remember Context:",
                words(40, "secondone"),
                words(40, "secondtwo"),
            ]
        )
        result = validate_copy(copy, date(2026, 8, 7))
        self.assertEqual(result["story_count"], 2)
        self.assertEqual(result["story_words"], [110, 80])

    def test_three_story_adaptive_format_passes(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: August 7",
                "Models Learn Patience:",
                words(45, "leadone"),
                words(45, "leadtwo"),
                "Browsers Remember Context:",
                words(25, "secondone"),
                words(25, "secondtwo"),
                "Robots Sort Packages:",
                words(25, "thirdone"),
                words(25, "thirdtwo"),
            ]
        )
        result = validate_copy(copy, date(2026, 8, 7))
        self.assertEqual(result["story_count"], 3)
        self.assertEqual(result["story_words"], [90, 50, 50])

    def test_four_story_exception_format_passes(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: August 7",
                "Models Learn Patience:",
                words(40, "leadone"),
                words(40, "leadtwo"),
                "Browsers Remember Context:",
                words(20, "secondone"),
                words(20, "secondtwo"),
                "Robots Sort Packages:",
                words(20, "thirdone"),
                words(20, "thirdtwo"),
                "Search Finds Sources:",
                words(20, "fourthone"),
                words(20, "fourthtwo"),
            ]
        )
        result = validate_copy(copy, date(2026, 8, 7))
        self.assertEqual(result["story_count"], 4)
        self.assertEqual(result["story_words"], [80, 40, 40, 40])

    def test_future_copy_requires_blank_lines(self) -> None:
        copy = "\n".join(
            [
                "Today in AI: August 7",
                "Models Learn Patience:",
                words(80, "one"),
                words(80, "two"),
            ]
        )
        with self.assertRaisesRegex(SystemExit, "blank line"):
            validate_copy(copy, date(2026, 8, 7))

    def test_future_story_requires_spaced_paragraphs(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: August 7",
                "Models Learn Patience:",
                words(170, "body"),
            ]
        )
        with self.assertRaisesRegex(SystemExit, "at least two spaced"):
            validate_copy(copy, date(2026, 8, 7))

    def test_cliche_ending_phrase_fails(self) -> None:
        copy = "\n\n".join(
            [
                "Today in AI: August 7",
                "Models Learn Patience:",
                words(80, "one"),
                words(75, "two") + " Only time will tell.",
            ]
        )
        with self.assertRaisesRegex(SystemExit, "banned text"):
            validate_copy(copy, date(2026, 8, 7))

    def test_public_copy_urls_fail_from_august_25(self) -> None:
        body = [words(40, f"paragraph{number}") for number in range(4)]
        body[-1] += " https://example.com/source"
        copy = "\n\n".join(
            ["Today in AI: August 25", "Models Learn Patience:", *body]
        )
        with self.assertRaisesRegex(SystemExit, "public copy must not contain"):
            validate_copy(copy, date(2026, 8, 25))

    def test_public_copy_sources_footer_fails_from_august_25(self) -> None:
        body = [words(40, f"paragraph{number}") for number in range(4)]
        copy = "\n\n".join(
            ["Today in AI: August 25", "Models Learn Patience:", *body, "Sources:"]
        )
        with self.assertRaisesRegex(SystemExit, "public copy must not contain"):
            validate_copy(copy, date(2026, 8, 25))


if __name__ == "__main__":
    unittest.main()
