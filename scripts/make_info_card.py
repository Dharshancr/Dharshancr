from pathlib import Path
import os
import html


OUTPUT = Path("info-card.svg")

NAME = "Dharshan P"
USERNAME = "Dharshancr"

ROLE = "Full Stack Developer"
STACK = "React • Node.js • Python • AI"
FOCUS = "SaaS • Automation • APIs"
PROJECTS = "Stock Dashboard • RFQ Automation"
CURRENT = "Building AI-powered SaaS"
GOAL = "Open to Freelance Projects"


def esc(value):
    return html.escape(str(value))


def make_row(label, value, y, delay):
    return f"""
    <g class="row" style="animation-delay:{delay:.2f}s">
        <text x="35" y="{y}" class="label">{esc(label)}</text>
        <text x="150" y="{y}" class="value">{esc(value)}</text>
    </g>
    """


def make_svg():
    static = os.getenv("STATIC") == "1"

    animation = "" if static else """
    @keyframes appear {
        from {
            opacity: 0;
            transform: translateX(-8px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .row {
        opacity: 0;
        animation: appear 0.35s ease-out forwards;
    }
    """

    rows = [
        ("Role", ROLE),
        ("Stack", STACK),
        ("Focus", FOCUS),
        ("Projects", PROJECTS),
        ("Current", CURRENT),
        ("Goal", GOAL),
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
        width="490"
        height="390"
        viewBox="0 0 490 390">

    <style>
        .title {{
            font-family: monospace;
            font-size: 22px;
            font-weight: bold;
            fill: #ffffff;
        }}

        .subtitle {{
            font-family: monospace;
            font-size: 13px;
            fill: #8b949e;
        }}

        .label {{
            font-family: monospace;
            font-size: 14px;
            font-weight: bold;
            fill: #58a6ff;
        }}

        .value {{
            font-family: monospace;
            font-size: 14px;
            fill: #c9d1d9;
        }}

        .line {{
            stroke: #30363d;
            stroke-width: 1;
        }}

        {animation}
    </style>

    <rect
        width="490"
        height="390"
        rx="12"
        fill="#0d1117"
        stroke="#30363d"
    />

    <!-- Terminal title -->
    <circle cx="22" cy="22" r="6" fill="#ff5f56"/>
    <circle cx="42" cy="22" r="6" fill="#ffbd2e"/>
    <circle cx="62" cy="22" r="6" fill="#27c93f"/>

    <text x="35" y="75" class="title">
        {esc(NAME)}
    </text>

    <text x="35" y="98" class="subtitle">
        {esc(USERNAME)}@github ~ $ whoami
    </text>

    <line x1="35" y1="115" x2="455" y2="115" class="line"/>

    {make_row("Role", ROLE, 150, 0.05)}
    {make_row("Stack", STACK, 185, 0.10)}
    {make_row("Focus", FOCUS, 220, 0.15)}
    {make_row("Projects", PROJECTS, 255, 0.20)}
    {make_row("Current", CURRENT, 290, 0.25)}
    {make_row("Goal", GOAL, 325, 0.30)}

    <text x="35" y="365" class="subtitle">
        $ ./build-something-great
    </text>

    </svg>
    """

    return svg


def main():
    OUTPUT.write_text(
        make_svg(),
        encoding="utf-8"
    )

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
