#!/usr/bin/env python3
"""
Script to regenerate question images for neologism_it dataset.

The original images only had 2 images per stimulus (question 1 and question 2),
but there are 6 different questions per stimulus (3 conditions × 2 questions).

This script generates all 168 unique question images with proper naming:
- {stimulus_name}_id{stimulus_id}_question_{stimulus_id}{condition_no}{question_no}_neologism_it.png

Example: NeoFin_Unicorno_id1A_question_1A31_neologism_it.png
         (stimulus 1A, condition 3 global, question 1)
"""

import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import shutil

# Configuration from config_neologism_it.py
IMAGE_WIDTH_PX = 1310
IMAGE_HEIGHT_PX = 992
IMAGE_BGC = (231, 230, 230)
FGC = (0, 0, 0)
FONT_SIZE = 24

# Answer box positions (TOP_X, TOP_Y, BOTTOM_X, BOTTOM_Y)
BOX_UP = (188.4, 248.0, 1117.55, 416.64)
BOX_DOWN = (188.4, 744.0, 1117.55, 912.64)
BOX_LEFT = (72.9, 436.48, 622.15, 714.24)
BOX_RIGHT = (686.2, 436.48, 1235.45, 714.24)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "fonts/JetBrainsMono-Regular.ttf")
OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "data/stimuli_neologism_it/question_images_neologism_it")
AOI_OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "data/stimuli_neologism_it/aoi_question_images_neologism_it")


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


def draw_text_in_box(draw, text, box, font, fgc):
    """Draw wrapped text centered in a box."""
    x1, y1, x2, y2 = box
    box_width = x2 - x1
    box_height = y2 - y1

    # Wrap text
    lines = wrap_text(text, font, box_width - 20, draw)

    # Calculate total text height
    line_height = font.size + 8
    total_height = len(lines) * line_height

    # Start y position (centered vertically)
    start_y = y1 + (box_height - total_height) / 2

    # Draw each line
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = x1 + (box_width - text_width) / 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=fgc)


def draw_box_outline(draw, box, color=(100, 100, 100), width=2):
    """Draw a rectangle outline."""
    x1, y1, x2, y2 = box
    draw.rectangle([x1, y1, x2, y2], outline=color, width=width)


def generate_question_image_from_row(row, output_path, font):
    """Generate a question image from a DataFrame row."""
    # Create image
    img = Image.new('RGB', (IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX), IMAGE_BGC)
    draw = ImageDraw.Draw(img)

    # Map keys to boxes
    key_to_box = {
        'up': BOX_UP,
        'down': BOX_DOWN,
        'left': BOX_LEFT,
        'right': BOX_RIGHT
    }

    # Map answers to their positions
    answer_positions = {
        row['target_key']: row['target'],
        row['distractor_a_key']: row['distractor_a'],
        row['distractor_b_key']: row['distractor_b'],
        row['distractor_c_key']: row['distractor_c'],
    }

    # Draw question text at top
    question_text = row['question']
    lines = wrap_text(question_text, font, IMAGE_WIDTH_PX - 100, draw)
    line_height = font.size + 8
    start_y = 80
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (IMAGE_WIDTH_PX - text_width) / 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=FGC)

    # Draw answer boxes with text
    for key, answer in answer_positions.items():
        box = key_to_box[key]
        draw_box_outline(draw, box, color=(100, 100, 100), width=2)
        draw_text_in_box(draw, answer, box, font, FGC)

    # Save image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    return output_path


def get_new_filename(stimulus_name, stimulus_id, condition_no, question_no):
    """Generate new filename with condition encoded."""
    return f"{stimulus_name}_id{stimulus_id}_question_{stimulus_id}{condition_no}{question_no}_neologism_it.png"


def main():
    # Load font
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        print(f"Loaded font from {FONT_PATH}")
    except Exception as e:
        print(f"Warning: Could not load font from {FONT_PATH}: {e}")
        print("Using default font")
        font = ImageFont.load_default()

    # Process each version (1-10)
    for version in range(1, 11):
        version_dir = os.path.join(OUTPUT_BASE_DIR, f"question_images_version_{version}")
        csv_path = os.path.join(version_dir, f"neologism_it_comprehension_questions_question_images_version_{version}_with_img_paths.csv")

        if not os.path.exists(csv_path):
            print(f"Warning: CSV not found at {csv_path}, skipping version {version}")
            continue

        print(f"\n=== Processing version {version} ===")
        print(f"Reading CSV from {csv_path}")

        # Load question data from CSV
        df = pd.read_csv(csv_path)
        print(f"Total questions: {len(df)}")

        # Backup original CSV
        backup_path = csv_path + ".backup"
        if not os.path.exists(backup_path):
            shutil.copy(csv_path, backup_path)
            print(f"Backed up CSV to {backup_path}")

        # Generate images and update CSV
        generated = 0
        updated_rows = []

        for idx, row in df.iterrows():
            stimulus_name = row['stimulus_name']
            stimulus_id = row['stimulus_id']
            condition_no = int(row['condition_no'])
            question_no = int(row['question_no'])

            # Create new filename with condition encoded
            new_filename = get_new_filename(stimulus_name, stimulus_id, condition_no, question_no)
            new_relative_path = f"data/stimuli_neologism_it/question_images_neologism_it/question_images_version_{version}/{new_filename}"
            output_path = os.path.join(version_dir, new_filename)

            # Generate the image
            generate_question_image_from_row(row, output_path, font)
            generated += 1

            # Update row with new paths
            row_copy = row.copy()
            row_copy['question_img_path'] = new_relative_path
            row_copy['question_img_file'] = new_filename
            updated_rows.append(row_copy)

            if generated % 28 == 0:
                print(f"  Generated {generated} images...")

        # Save updated CSV
        updated_df = pd.DataFrame(updated_rows)
        updated_df.to_csv(csv_path, index=False)
        print(f"  Generated {generated} images in {version_dir}")
        print(f"  Updated CSV with new image paths")

        # Also update AOI CSV if it exists
        aoi_version_dir = os.path.join(AOI_OUTPUT_BASE_DIR, f"question_images_version_{version}")
        aoi_csv_path = os.path.join(aoi_version_dir, f"neologism_it_comprehension_questions_aoi_question_images_version_{version}_with_img_paths.csv")

        if os.path.exists(aoi_csv_path):
            print(f"  Updating AOI CSV at {aoi_csv_path}")
            aoi_df = pd.read_csv(aoi_csv_path)

            # Backup AOI CSV
            aoi_backup_path = aoi_csv_path + ".backup"
            if not os.path.exists(aoi_backup_path):
                shutil.copy(aoi_csv_path, aoi_backup_path)

            # Update AOI CSV with new filenames
            for idx, row in aoi_df.iterrows():
                stimulus_name = row['stimulus_name']
                stimulus_id = row['stimulus_id']
                condition_no = int(row['condition_no'])
                question_no = int(row['question_no'])

                new_filename = get_new_filename(stimulus_name, stimulus_id, condition_no, question_no).replace('.png', '_aoi.png')
                new_relative_path = f"data/stimuli_neologism_it/aoi_question_images_neologism_it/question_images_version_{version}/{new_filename}"

                aoi_df.at[idx, 'question_img_path'] = new_relative_path
                aoi_df.at[idx, 'question_img_file'] = new_filename

            aoi_df.to_csv(aoi_csv_path, index=False)
            print(f"  Updated AOI CSV")

    print("\n" + "="*60)
    print("DONE! Question images have been regenerated.")
    print("="*60)
    print("\nNew naming convention:")
    print("  {stimulus_name}_id{stimulus_id}_question_{stimulus_id}{condition_no}{question_no}_neologism_it.png")
    print("\nExamples:")
    print("  NeoFin_Unicorno_id1A_question_1A31_neologism_it.png (condition 3 global, question 1)")
    print("  NeoFin_Unicorno_id1A_question_1A21_neologism_it.png (condition 2 bridging, question 1)")
    print("  NeoFin_Unicorno_id1A_question_1A11_neologism_it.png (condition 1 local, question 1)")
    print("\nThe CSV files have been updated to point to the new images.")
    print("Original CSVs have been backed up with .backup extension.")


if __name__ == "__main__":
    main()
