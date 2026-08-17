from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


OUTPUT = Path("data/source-prepped.png")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: photo not found: {input_path}")
        sys.exit(1)

    print("Removing background...")

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    output_bytes = remove(input_bytes)

    # Load image with alpha channel
    image = Image.open(__import__("io").BytesIO(output_bytes)).convert("RGBA")

    # Convert to numpy
    rgba = np.array(image)

    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # Convert RGB → grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    print("Improving contrast...")

    # CLAHE improves local facial contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Composite onto white background
    alpha_float = alpha.astype(np.float32) / 255.0

    white = np.full_like(enhanced, 255)

    composited = (
        enhanced.astype(np.float32) * alpha_float
        + white.astype(np.float32) * (1 - alpha_float)
    )

    composited = np.clip(composited, 0, 255).astype(np.uint8)

    # Save
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    Image.fromarray(composited).save(
        OUTPUT,
        format="PNG"
    )

    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
