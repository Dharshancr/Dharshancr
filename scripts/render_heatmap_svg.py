from pathlib import Path
import json
from datetime import datetime, timedelta


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")

WIDTH = 860
HEIGHT = 190

# GitHub-style contribution colors
PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


def load_data():
    if not INPUT.exists():
        raise FileNotFoundError(
            "data/contributions.json not found. "
            "Run fetch_contributions.py first."
        )

    return json.loads(
        INPUT.read_text(encoding="utf-8")
    )


def contribution_level(count, max_count):
    if count <= 0:
        return 0

    if max_count <= 1:
        return 1

    ratio = count / max_count

    if ratio <= 0.20:
        return 1
    elif ratio <= 0.40:
        return 2
    elif ratio <= 0.60:
        return 3
    elif ratio <= 0.80:
        return 4

    return 5


def make_heatmap(days):
    # GitHub contribution graph:
    # 53 weeks × 7 days

    cell = 11
    gap = 3

    grid_width = 53 * (cell + gap)
    grid_x = 0

    # Find maximum contribution count
    max_count = max(
        [day["count"] for day in days],
        default=1
    )

    # Convert dates into lookup dictionary
    lookup = {
        day["date"]: day["count"]
        for day in days
    }

    # Find first date
    if days:
        first_date = datetime.strptime(
            days[0]["date"],
            "%Y-%m-%d"
        ).date()
    else:
        first_date = datetime.now().date()

    # Align to Sunday
    first_date -= timedelta(
        days=(first_date.weekday() + 1) % 7
    )

    cells = []

    for week in range(53):

        for weekday in range(7):

            date = first_date + timedelta(
                days=week * 7 + weekday
            )

            date_string = date.isoformat()

            count = lookup.get(
                date_string,
                0
            )

            level = contribution_level(
                count,
                max_count
            )

            x = grid_x + week * (cell + gap)
            y = 30 + weekday * (cell + gap)

            delay = (
                week * 0.025
                + weekday * 0.01
            )

            cells.append(
                f"""
                <rect
                    class="day"
                    x="{x}"
                    y="{y}"
                    width="{cell}"
                    height="{cell}"
                    rx="2"
                    fill="{PALETTE[level]}"
                    style="animation-delay:{delay:.3f}s"
                >
                    <title>
                        {count} contributions on {date_string}
                    </title>
                </rect>
                """
            )

    return "\n".join(cells)


def make_svg(data):

    days = data.get("days", [])
    stats = data.get("stats", {})

    total = stats.get("total", 0)
    current_streak = stats.get(
        "current_streak",
        0
    )
    longest_streak = stats.get(
        "longest_streak",
        0
    )

    heatmap = make_heatmap(days)

    return f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<style>

    .title {{
        font-family: monospace;
        font-size: 16px;
        font-weight: bold;
        fill: #c9d1d9;
    }}

    .stats {{
        font-family: monospace;
        font-size: 11px;
        fill: #8b949e;
    }}

    .legend {{
        font-family: monospace;
        font-size: 10px;
        fill: #8b949e;
    }}

    .day {{
        opacity: 0;
        animation: reveal 0.45s ease-out forwards;
    }}

    @keyframes reveal {{
        from {{
            opacity: 0;
            transform: translateY(-5px);
        }}

        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

</style>

<!-- Background -->

<rect
    width="{WIDTH}"
    height="{HEIGHT}"
    rx="12"
    fill="#0d1117"
    stroke="#30363d"
/>

<!-- Terminal heading -->

<text
    x="20"
    y="22"
    class="title"
>
    Dharshancr@github ~ $ ./contributions.sh
</text>

<!-- Contribution cells -->

<g transform="translate(20, 25)">
    {heatmap}
</g>

<!-- Stats -->

<text
    x="20"
    y="145"
    class="stats"
>
    {total:,} contributions in the last year
</text>

<text
    x="20"
    y="162"
    class="stats"
>
    Current streak: {current_streak} days
</text>

<text
    x="20"
    y="179"
    class="stats"
>
    Longest streak: {longest_streak} days
</text>

<!-- Legend -->

<text
    x="690"
    y="145"
    class="legend"
>
    Less
</text>

<rect x="720" y="137" width="11" height="11" rx="2"
fill="{PALETTE[0]}"/>

<rect x="736" y="137" width="11" height="11" rx="2"
fill="{PALETTE[1]}"/>

<rect x="752" y="137" width="11" height="11" rx="2"
fill="{PALETTE[2]}"/>

<rect x="768" y="137" width="11" height="11" rx="2"
fill="{PALETTE[3]}"/>

<rect x="784" y="137" width="11" height="11" rx="2"
fill="{PALETTE[4]}"/>

<rect x="800" y="137" width="11" height="11" rx="2"
fill="{PALETTE[5]}"/>

<text
    x="817"
    y="145"
    class="legend"
>
    More
</text>

</svg>
"""


def main():

    print("Loading contribution data...")

    data = load_data()

    svg = make_svg(data)

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
