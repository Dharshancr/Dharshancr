from pathlib import Path
import html

import numpy as np
from PIL import Image


INPUT = Path("data/source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

# Bright -> dark
RAMP = " .`:-=+*cs#%@"

# Character dimensions
COLS = 100
ROWS = 53

# Character size
CHAR_WIDTH = 7.2
CHAR_HEIGHT = 12


def brightness_to_char(value):
    """
    Convert brightness (0-255) into an ASCII character.

    White = sparse/light character
    Black = dense/dark character
    """
    index = int((255 - value) / 255 * (len(RAMP) - 1))
    return RAMP[index]


def load_and_resize():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing {INPUT}. Run prep_photo.py first."
        )

    image = Image.open(INPUT).convert("L")

    # Force desired aspect ratio.
    image = image.resize((COLS, ROWS))

    return np.array(image)


def make_svg(pixels):
    width = int(COLS * CHAR_WIDTH)
    height = int(ROWS * CHAR_HEIGHT)

    lines = []

    lines.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}">'''
    )

    lines.append("""
<style>
.ascii {
    font-family: monospace;
    font-size: 12px;
    fill: #8b949e;
}

@keyframes reveal {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.row {
    opacity: 0;
    animation: reveal 0.25s ease-out forwards;
}
</style>
""")

    # Background
    lines.append(
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>'
    )

    # Generate ASCII rows
    for y in range(ROWS):
        delay = y * 0.035

        lines.append(
            f'<g class="row" style="animation-delay:{delay:.3f}s">'
        )

        for x in range(COLS):
            value = pixels[y, x]
            char = brightness_to_char(value)

            if char == " ":
                continue

            safe_char = html.escape(char)

            px = x * CHAR_WIDTH
            py = (y + 1) * CHAR_HEIGHT

            lines.append(
                f'<text x="{px:.1f}" y="{py:.1f}" '
                f'class="ascii">{safe_char}</text>'
            )

        lines.append("</g>")

    lines.append("</svg>")

    return "\n".join(lines)


def main():
    pixels = load_and_resize()

    svg = make_svg(pixels)

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
