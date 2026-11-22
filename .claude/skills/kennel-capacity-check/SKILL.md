---
name: kennel-capacity-check
description: Use when asked how many additional animals the shelter can safely intake this week, given current kennel occupancy.
---
# Kennel Capacity Playbook

Given total kennels, currently occupied kennels, and expected adoptions this week,
run `scripts/kennel_capacity.py` rather than estimating by hand:
    python3 .claude/skills/kennel-capacity-check/scripts/kennel_capacity.py --total-kennels 40 --occupied-kennels 33 --expected-adoptions-this-week 4

1. Count only the buildings that are available this week, as defined in `reference/kennel-sizing-notes.md`.
2. Never plan intake assuming more than 80% of total capacity — some kennels are always reserved for medical holds.
3. Safe intake = max(0, floor(total kennels × 0.8) − (occupied kennels − expected adoptions)).
   Example: 40 total, 33 occupied, 4 expected adoptions gives max(0, 32 − 29) = 3.
4. Warn if safe intake is 2 or fewer kennels.
5. Always show the script's output, not just the final number.

The script prints safe intake and warns from it. Its "Available by end of week" figure is not the
safe intake, so report the "Safe intake this week" line.

This skill is a staff planning aid. It is not part of the PawMatch API and never affects screening.
