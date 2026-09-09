import argparse
from ast import arg

import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from PIL import Image
import tempfile
import zipfile
import os

import pprint

# example usage:
"""
python3 create_members_choice_ppt.py \
    --date "July 2026" \
    --assigned-topic-name "Eyes" \
    --open-zip ~/Downloads/july_2026_open.zip \
    --assigned-zip ~/Downloads/july_2026_assigned_eyes.zip \
    --open-excel ~/Downloads/july_2026_open-images_submissions.xlsx \
    --assigned-excel ~/Downloads/july_2026_assigned_eyes-images_submissions.xlsx \
    --open-with-names ~/Downloads/"2026_07_MC Open.txt" \
    --assigned-with-names ~/Downloads/"2026_07_MC Assigned.txt" \
    --output ~/Downloads/July2026MembersChoice.pptx
"""


# TODO: implement photographer name lookup

# add argparse for input file paths and output file path
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="Date of the Members' Choice event (e.g., 'June 2026')")
parser.add_argument("--assigned-topic-name", help="Name of the assigned topic (e.g., 'Getting Around')")
parser.add_argument("--open-zip", help="Path to the open category zip file")
parser.add_argument("--assigned-zip", help="Path to the assigned category zip file")
parser.add_argument("--open-excel", help="Path to the open category Excel file")
parser.add_argument("--assigned-excel", help="Path to the assigned category Excel file")
parser.add_argument("--open-with-names",  help="Path to the open lookup file with photographer names (.txt or .xlsx supported)")
parser.add_argument("--assigned-with-names", help="Path to the assigned lookup file with photographer names (.txt or .xlsx supported)")
parser.add_argument("--output", help="Path to the output PowerPoint file")
args = parser.parse_args()


open_photographer_lookup = {}
assigned_photographer_lookup = {}

with open(args.open_with_names, 'r') as f:
    if args.open_with_names.endswith(".txt"):
        for line in f.readlines()[1:]:
            split = line.strip().split('\t')

            print(split[2])

            title = split[2]
            photographer_name = split[3]
            open_photographer_lookup[title] = photographer_name
    elif args.open_with_names.endswith(".xlsx"):
        df = pd.read_excel(args.open_with_names)
        for _, row in df.iterrows():
            title = row['Title']
            photographer_name = row['Name']
            open_photographer_lookup[title] = photographer_name
    else:
        raise ValueError("Unsupported file format for --open-with-names. Please provide a .txt or .xlsx file.")

with open(args.assigned_with_names, 'r') as f:
    if args.assigned_with_names.endswith(".txt"):
        for line in f.readlines()[1:]:
            split = line.strip().split('\t')

            title = split[2]
            photographer_name = split[3]
            assigned_photographer_lookup[title] = photographer_name
    elif args.assigned_with_names.endswith(".xlsx"):
        df = pd.read_excel(args.assigned_with_names)
        for _, row in df.iterrows():
            title = row['Title']
            photographer_name = row['Name']
            assigned_photographer_lookup[title] = photographer_name
    else:
        raise ValueError("Unsupported file format for --assigned-with-names. Please provide a .txt or .xlsx file.")

pprint.pprint(open_photographer_lookup)
pprint.pprint(assigned_photographer_lookup)

# 1. Load the spreadsheet into memory
df = pd.read_excel(args.open_excel)
open_category_poll_data = [row.to_dict() for _, row in df.iterrows()]

open_category_poll_data.sort(key=lambda x: x['Voters'], reverse=True)

print(open_category_poll_data[9]['Voters'])

tenth_place_score = open_category_poll_data[9]['Voters']
# grab the top 10 plus any tiebreakers for 10th place
open_category_poll_data = [photo for photo in open_category_poll_data if photo['Voters'] >= tenth_place_score]


df = pd.read_excel(args.assigned_excel)
assigned_category_poll_data = [row.to_dict() for _, row in df.iterrows()]

assigned_category_poll_data.sort(key=lambda x: x['Voters'], reverse=True)
tenth_place_score = assigned_category_poll_data[9]['Voters']
# grab the top 10 plus any tiebreakers for 10th place
assigned_category_poll_data = [photo for photo in assigned_category_poll_data if photo['Voters'] >= tenth_place_score]

def add_assigned_photos_section(prs):
    # --- SLIDE 1: Title Slide ---
    # slide_layouts[0] is the standard Title Slide layout
    title_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(title_layout)

    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0, 0, 0)

    # Populate standard title placeholders
    title = slide1.shapes.title

    subtitle = slide1.placeholders[1]

    title.text = f"Members’ Choice Top {len(assigned_category_poll_data)}"
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(247, 203, 121)
    subtitle.text = f"{args.assigned_topic_name}\n{args.date}"
    subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(247, 203, 121)
    subtitle.text_frame.paragraphs[1].font.color.rgb = RGBColor(247, 203, 121)

def add_open_photos_section(prs):
    # --- SLIDE 1: Title Slide ---
    # slide_layouts[0] is the standard Title Slide layout
    title_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(title_layout)

    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0, 0, 0)

    # Populate standard title placeholders
    title = slide1.shapes.title
    subtitle = slide1.placeholders[1]

    title.text = f"Members’ Choice Top {len(open_category_poll_data)}"
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(247, 203, 121)
    subtitle.text = f"Open\n{args.date}"
    subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(247, 203, 121)
    subtitle.text_frame.paragraphs[1].font.color.rgb = RGBColor(247, 203, 121)

def add_end_slide(prs):
    # --- SLIDE 1: Title Slide ---
    # slide_layouts[0] is the standard Title Slide layout
    title_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(title_layout)

    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0, 0, 0)

    # Populate standard title placeholders
    title = slide1.shapes.title
    subtitle = slide1.placeholders[1]

    title.text = "CHARLOTTESVILLE CAMERA CLUB"
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(247, 203, 121)
    subtitle.text = "Charlottesville, Virginia"
    subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(247, 203, 121)


def add_image_slide(prs, image_path, title_text):
    # add a new blank slide with a title at the top and an image centered below it
    blank_slide_layout = prs.slide_layouts[6]  # 6 is usually a blank layout
    slide = prs.slides.add_slide(blank_slide_layout)
    # Add title
    title_shape = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
    title_shape.text = title_text

    title_shape.text_frame.paragraphs[0].font.size = Pt(18) if len(title_text) > 60 else Pt(24) if len(title_text) > 40 else Pt(32)

    with Image.open(image_path) as img:
        img_width, img_height = img.size

    target_height = Inches(5.5)
    aspect_ratio = img_width / img_height
    target_width = target_height * aspect_ratio

    # Resize the image if it's wider than the slide width
    if target_width > prs.slide_width - Inches(1):
        target_width = prs.slide_width - Inches(1)
        target_height = target_width / aspect_ratio

    left = (prs.slide_width - target_width) / 2
    top = (prs.slide_height - target_height) / 2 + Inches(0.1)  # Adjust top to account for title
    slide.shapes.add_picture(image_path, left, top, height=target_height)


def add_images(prs, zip_file_path, poll_data, lookup_dict):
    # lookup image path by ID
    path_lookup = {}

    # 1. Create a temporary directory that cleans up automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        # 2. Open and extract the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        for filename in os.listdir(temp_dir):
            img_id = int(filename.split('-')[0])
            path_lookup[img_id] = os.path.join(temp_dir, filename)
            
        # 3. Process the unzipped files here
        # All files inside temp_dir will be deleted when exiting this "with" block
        for photo in poll_data:
            path = path_lookup.get(photo['ID'])
            num_votes = photo['Voters']
            title = photo['Option']
            print(title)
            photographer = lookup_dict[title]

            add_image_slide(prs, path, f'{num_votes} ❤ "{title}" {photographer}')

def add_applause_image_slide(prs):
    applause_image_path = os.path.join(os.path.dirname(__file__), "applause.png")
    add_image_slide(prs, applause_image_path, "")

prs = Presentation()
assigned_zip_file_path = args.assigned_zip
open_zip_file_path = args.open_zip
add_assigned_photos_section(prs)
add_images(prs, assigned_zip_file_path, assigned_category_poll_data, assigned_photographer_lookup)
add_open_photos_section(prs)
add_images(prs, open_zip_file_path, open_category_poll_data, open_photographer_lookup)
add_applause_image_slide(prs)
add_end_slide(prs)

with open(args.output, "wb") as f:
    prs.save(f)

print("PowerPoint presentation created successfully at:", args.output)
