#!/usr/bin/env python3
"""
Script to regenerate rating screen images with Italian translations.

Rating Screen 1: Prior exposure question
Rating Screen 2: Content familiarity question
Rating Screen 3: Text difficulty question (subject_difficulty_screen)

IMPORTANT: The option text positions must match the selection box coordinates
defined in config_neologism_it.py:
    option_1 = (89.1, 306.9, 604.3, 336.9)
    option_2 = (89.1, 405.9, 604.3, 435.9)
    option_3 = (89.1, 504.9, 604.3, 534.9)
    option_4 = (89.1, 603.9, 604.3, 633.9)
    option_5 = (89.1, 702.9, 604.3, 732.9)
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Configuration - matching lab config (config_neologism_it.py)
IMAGE_WIDTH_PX = 1310
IMAGE_HEIGHT_PX = 992
IMAGE_BGC = (231, 230, 230)
FGC = (0, 0, 0)
FONT_SIZE = 24

# Option box Y positions from config_neologism_it.py
# These are the Y coordinates where the selection boxes are drawn
# Format: (x1, y1, x2, y2) - we need to center text vertically in each box
OPTION_BOX_Y_POSITIONS = [
    (306.9, 336.9),   # option_1: y1=306.9, y2=336.9, center=321.9
    (405.9, 435.9),   # option_2: y1=405.9, y2=435.9, center=420.9
    (504.9, 534.9),   # option_3: y1=504.9, y2=534.9, center=519.9
    (603.9, 633.9),   # option_4: y1=603.9, y2=633.9, center=618.9
    (702.9, 732.9),   # option_5: y1=702.9, y2=732.9, center=717.9
]

OPTION_X = 90  # X position for option text (slightly indented)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "fonts/JetBrainsMono-Regular.ttf")
OUTPUT_DIR = os.path.join(BASE_DIR, "data/stimuli_neologism_it/participant_instructions_images_neologism_it")

# Italian translations for rating screens
RATING_SCREENS = {
    "familiarity_rating_screen_1": {
        "question": "Hai già letto o ascoltato questo testo in precedenza?",
        "options": [
            "- Sì",
            "- No",
            "- Non ricordo"
        ]
    },
    "familiarity_rating_screen_2": {
        "question": "Valuta la tua familiarità con il contenuto del testo. Quanto del contenuto ti era familiare?",
        "options": [
            "1 - 0%",
            "2 - 25%",
            "3 - 50%",
            "4 - 75%",
            "5 - 100%"
        ]
    },
    "subject_difficulty_screen": {
        "question": "Valuta la difficoltà del testo che hai appena letto. Quanto è stato difficile leggere e comprendere il testo?",
        "options": [
            "1 - molto facile",
            "2 - facile",
            "3 - né facile né difficile",
            "4 - difficile",
            "5 - molto difficile"
        ]
    }
}


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def generate_rating_screen(screen_name, screen_data, font, output_dir):
    """Generate a rating screen image.

    Option text is positioned to align with the selection box coordinates
    defined in config_neologism_it.py so the highlight boxes appear correctly.
    """
    # Create image
    img = Image.new('RGB', (IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX), IMAGE_BGC)
    draw = ImageDraw.Draw(img)

    question = screen_data["question"]
    options = screen_data["options"]

    # Draw question text at top (with wrapping)
    max_text_width = IMAGE_WIDTH_PX - 140  # margins
    lines = wrap_text(question, font, max_text_width, draw)

    line_height = font.size + 16
    start_y = 80

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = 70  # Left aligned
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=FGC)

    # Draw options at the Y positions that match the selection boxes
    # The selection boxes are defined in config_neologism_it.py
    for i, option in enumerate(options):
        if i < len(OPTION_BOX_Y_POSITIONS):
            y1, y2 = OPTION_BOX_Y_POSITIONS[i]
            # Center text vertically within the box
            text_height = font.size
            y = y1 + (y2 - y1 - text_height) / 2
        else:
            # Fallback for more than 5 options (shouldn't happen)
            y = 306.9 + i * 99

        draw.text((OPTION_X, y), option, font=font, fill=FGC)

    # Draw hollow dot in bottom right (black circle with white center)
    circle_x = IMAGE_WIDTH_PX - 70
    circle_y = IMAGE_HEIGHT_PX - 70
    outer_radius = 10
    inner_radius = 4
    # Outer black circle
    draw.ellipse(
        [circle_x - outer_radius, circle_y - outer_radius,
         circle_x + outer_radius, circle_y + outer_radius],
        fill=FGC
    )
    # Inner white circle
    draw.ellipse(
        [circle_x - inner_radius, circle_y - inner_radius,
         circle_x + inner_radius, circle_y + inner_radius],
        fill=(255, 255, 255)
    )

    # Save image
    output_path = os.path.join(output_dir, f"{screen_name}_neologism_it.png")
    img.save(output_path)
    print(f"Generated: {output_path}")
    return output_path


def main():
    # Load font
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        print(f"Loaded font from {FONT_PATH}")
    except Exception as e:
        print(f"Warning: Could not load font from {FONT_PATH}: {e}")
        print("Using default font")
        font = ImageFont.load_default()

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\nGenerating Italian rating screens...")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Image size: {IMAGE_WIDTH_PX}x{IMAGE_HEIGHT_PX}")
    print()

    # Generate each rating screen
    for screen_name, screen_data in RATING_SCREENS.items():
        generate_rating_screen(screen_name, screen_data, font, OUTPUT_DIR)

    print("\nDone! All rating screens have been regenerated with Italian translations.")


if __name__ == "__main__":
    main()
