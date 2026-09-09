import argparse
from datetime import date
import os
import shutil
import tempfile
import zipfile

parser = argparse.ArgumentParser(
                    prog='CCC File Parser',
                    description='Parses CCC photo files',
                    epilog='Made by William Edmisten')

parser.add_argument('zip_file', help='The zip file containing CCC files to parse')
parser.add_argument('out_directory', help='The directory to write renamed files to')

args = parser.parse_args()

with tempfile.TemporaryDirectory() as temp_dir:
    # 2. Open and extract the zip file
    with zipfile.ZipFile(args.zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    print(f"Parsing CCC files from: {args.zip_file}")
    print(f"Renamed files will be written to: {args.out_directory}")

    # list files

    files = sorted(os.listdir(temp_dir))
    print(len(files), "files found in directory")
    top_rated = [file for file in files if file.endswith("4.jpg") or file.endswith("5.jpg")]

    print(len(top_rated), "top-rated files found")

    def get_category(file):
        if "Assigned A" in file:
            return "Assigned A"
        elif "Assigned B" in file:
            return "Assigned B"
        elif "Open A" in file:
            return "Open A"
        elif "Open B" in file:
            return "Open B"
        else:
            raise ValueError(f"Unknown category in file name: {file}")

    parsed_files = []

    for file in top_rated:
        splits = file.split("_")
        title = splits[1]
        photographer = splits[2]
        category = get_category(file)
        score = splits[3].replace(".jpg", "")

        parsed_files.append({
            "title": title,
            "photographer": photographer,
            "category": category,
            "score": score,
            "original_file": file,
            "new_filename": file
        })

    today = date.today()
    month = today.strftime("%B")
    year = today.strftime("%Y")

    def truncate_title_to_n_chars(title, n):
        # truncate the title based on the words separated by spaces, not just to exactly n chars
        words = title.split(" ")
        truncated_title = ""
        for word in words:
            if len(truncated_title) + len(word) + 1 > n:
                break
            truncated_title += word + " "
        return truncated_title.strip()

    # correct fields that are too long
    for file in parsed_files:
        if len(file["title"]) > 40:
            old_title = file["title"]
            file["title"] = truncate_title_to_n_chars(file["title"], 40)
            file["new_filename"] = file["new_filename"].replace(old_title, file["title"])

            print(f"⚠️ Truncated title from '{old_title}' to '{file['title']}' ({len(old_title)} chars to {len(file['title'])} chars)\n")

        file["new_filename"] = f"{year}_{month}-{file['category']}-{file['photographer']}-{file['title']}-{file['score']}.jpg"

        if len(file["new_filename"]) - file["new_filename"].count(" ") > 60:
            length_diff = len(file["new_filename"]) - 60
            # truncate the title by the length difference
            new_title = truncate_title_to_n_chars(file["title"], len(file["title"]) - length_diff - 1)

            old_filename = file["new_filename"]
            file["new_filename"] = file["new_filename"].replace(file["title"], new_title)

            print(f"⚠️ Truncated filename from '{old_filename}' to '{file['new_filename']}' ({len(old_filename)} chars to {len(file['new_filename'])} chars)\n")

            # file["new_filename"] = input(f"Filename is {len(file['new_filename'])} characters long (max 60). Enter new filename for {file['new_filename']}: ")

        file["new_filename"] = file["new_filename"].replace(" ", "")

    os.makedirs(args.out_directory, exist_ok=True)

    import json

    items = []

    for idx, file in enumerate(parsed_files):
        # Safely combine the folder path and the new file name
        full_source_path = os.path.join(temp_dir, file["original_file"])
        full_destination_path = os.path.join(args.out_directory, file["new_filename"])

        # Execute the copy operation
        # print(f"Copying '{full_source_path}' to '{full_destination_path}'")
        shutil.copy(full_source_path, full_destination_path)

    for idx, file in enumerate(sorted(parsed_files, key=lambda x: x["new_filename"])):
        if idx % 4 == 0:
            print(json.dumps(items))
            print("========================================")
            items = []
        items.append(file)

    print(json.dumps(items))
    print("========================================")