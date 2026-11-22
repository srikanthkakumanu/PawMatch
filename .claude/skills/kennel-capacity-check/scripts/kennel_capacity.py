#!/usr/bin/env python3
"""Computes how many more animals the shelter can safely intake this week.

Referenced by SKILL.md so Claude executes it directly instead of estimating
the arithmetic itself."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-kennels", type=int, required=True)
    parser.add_argument("--occupied-kennels", type=int, required=True)
    parser.add_argument("--expected-adoptions-this-week", type=int, default=0)
    args = parser.parse_args()

    available_now = args.total_kennels - args.occupied_kennels
    available_this_week = available_now + args.expected_adoptions_this_week
    # 80% ceiling from reference/kennel-sizing-notes.md. Integer arithmetic gives an exact floor.
    safe_ceiling = args.total_kennels * 4 // 5
    projected_occupied = args.occupied_kennels - args.expected_adoptions_this_week
    safe_intake = max(0, safe_ceiling - projected_occupied)

    print(f"Available now:             {available_now}")
    print(f"Available by end of week:  {available_this_week}")
    print(f"Safe intake ceiling (80%): {safe_ceiling}")
    print(f"Safe intake this week:     {safe_intake}")
    # Warning threshold from SKILL.md step 4.
    if safe_intake <= 2:
        print("WARNING: capacity is tight — consider pausing new intake requests.")


if __name__ == "__main__":
    main()
