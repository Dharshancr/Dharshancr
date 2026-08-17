from pathlib import Path
import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


USERNAME = "Dharshancr"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path("data/contributions.json")


def fetch_page():
    print(f"Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        },
        timeout=30,
    )

    print(f"HTTP status: {response.status_code}")
    response.raise_for_status()

    return response.text


def parse_contributions(page):
    soup = BeautifulSoup(page, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")

    print(f"Contribution cells found: {len(cells)}")

    if not cells:
        raise RuntimeError(
            "No GitHub contribution cells found."
        )

    days = []

    for cell in cells:
        date = cell.get("data-date")

        if not date:
            continue

        level = cell.get("data-level", "0")

        try:
            level = int(level)
        except ValueError:
            level = 0

        # Find the tooltip associated with this cell.
        tooltip = cell.find_next(
            "tool-tip",
            attrs={"data-type": "label"},
        )

        count = 0

        if tooltip:
            text = tooltip.get_text(
                " ",
                strip=True,
            )

            match = re.search(
                r"(\d+)\s+contribution",
                text,
                re.IGNORECASE,
            )

            if match:
                count = int(match.group(1))

        days.append(
            {
                "date": date,
                "count": count,
                "level": level,
            }
        )

    return days


def calculate_stats(days):
    total = sum(
        day["count"]
        for day in days
    )

    best_day = (
        max(
            days,
            key=lambda day: day["count"],
        )
        if days
        else None
    )

    monthly = {}

    for day in days:
        month = day["date"][:7]

        monthly[month] = (
            monthly.get(month, 0)
            + day["count"]
        )

    # Longest streak
    longest_streak = 0
    streak = 0

    for day in days:
        if day["count"] > 0:
            streak += 1
            longest_streak = max(
                longest_streak,
                streak,
            )
        else:
            streak = 0

    # Current streak
    current_streak = 0

    for day in reversed(days):
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main():
    print("Starting contribution fetch...")

    page = fetch_page()

    days = parse_contributions(page)

    stats = calculate_stats(days)

    output = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("SUCCESS")
    print(f"Days: {len(days)}")
    print(f"Total contributions: {stats['total']}")
    print(f"Current streak: {stats['current_streak']}")
    print(f"Longest streak: {stats['longest_streak']}")
    print(f"Best day: {stats['best_day']}")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()