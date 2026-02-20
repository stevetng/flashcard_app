"""Interactive terminal-based flashcard study session."""

import random
import sys


def _clear_line():
    sys.stdout.write("\033[2K\r")
    sys.stdout.flush()


def _print_box(text: str, width: int = 60):
    lines = []
    for raw_line in text.split("\n"):
        while len(raw_line) > width - 4:
            lines.append(raw_line[:width - 4])
            raw_line = raw_line[width - 4:]
        lines.append(raw_line)

    print("+" + "-" * (width - 2) + "+")
    for line in lines:
        padding = width - 4 - len(line)
        print(f"| {line}{' ' * padding} |")
    print("+" + "-" * (width - 2) + "+")


def run_study_session(flashcards: list[dict]):
    """Run an interactive flashcard study session in the terminal."""
    if not flashcards:
        print("No flashcards to study.")
        return

    cards = list(flashcards)
    random.shuffle(cards)
    total = len(cards)

    correct = 0
    incorrect = 0
    reviewed = 0
    missed_cards = []

    print(f"\n{'=' * 60}")
    print(f"  FLASHCARD STUDY SESSION  —  {total} cards")
    print(f"{'=' * 60}")
    print()
    print("Controls:")
    print("  [Enter]  Reveal answer")
    print("  [y]      Mark correct")
    print("  [n]      Mark incorrect")
    print("  [s]      Skip card")
    print("  [q]      Quit session")
    print()

    for i, card in enumerate(cards):
        reviewed += 1
        print(f"--- Card {i + 1}/{total}  (from slide {card['slide']}) ---")
        print()
        print("  Q:", card["front"])
        print()

        try:
            input("  Press Enter to reveal answer...")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        print()
        _print_box(card["back"])
        print()

        while True:
            try:
                choice = input("  Correct? [y/n/s/q]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = "q"

            if choice in ("y", "yes"):
                correct += 1
                print("  -> Correct!")
                break
            elif choice in ("n", "no"):
                incorrect += 1
                missed_cards.append(card)
                print("  -> Marked for review.")
                break
            elif choice == "s":
                reviewed -= 1
                print("  -> Skipped.")
                break
            elif choice == "q":
                print()
                _print_summary(correct, incorrect, reviewed, total, missed_cards)
                return
            else:
                print("  Please enter y, n, s, or q.")

        print()

    _print_summary(correct, incorrect, reviewed, total, missed_cards)

    if missed_cards:
        print()
        try:
            again = input("Review missed cards? [y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            again = "n"
        if again in ("y", "yes"):
            run_study_session(missed_cards)


def _print_summary(correct: int, incorrect: int, reviewed: int, total: int,
                    missed_cards: list[dict]):
    print(f"{'=' * 60}")
    print("  SESSION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Reviewed:   {reviewed}/{total}")
    print(f"  Correct:    {correct}")
    print(f"  Incorrect:  {incorrect}")
    if reviewed > 0:
        pct = correct / reviewed * 100
        print(f"  Score:      {pct:.0f}%")
    print(f"{'=' * 60}")

    if missed_cards:
        print()
        print("  Cards to review again:")
        for card in missed_cards:
            print(f"    - (Slide {card['slide']}) {card['front']}")
