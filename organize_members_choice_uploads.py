import argparse
import os
import shutil

parser = argparse.ArgumentParser()

# usage: python3 organize_members_choice_uploads.py --directory ~/Downloads/"To Judge"
parser.add_argument('--directory', help='The directory containing Members Choice files to organize', required=True)

args = parser.parse_args()

# print out the files in the directory
files = sorted(os.listdir(args.directory))
print(files)

# create two new dirs: Assigned and Open under the directory
assigned_dir = os.path.join(args.directory, "Pollunit Assigned")
open_dir = os.path.join(args.directory, "Pollunit Open")

if not os.path.exists(assigned_dir):
    os.makedirs(assigned_dir)

if not os.path.exists(open_dir):
    os.makedirs(open_dir)

# copy the files from /Open A to /Open

def copy_contents(src_dir, dest_dir):
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        # remove the numeric prefix: 001_
        d = os.path.join(dest_dir, item[4:])
        print(item[4:])
        shutil.copy2(s, d)

copy_contents(os.path.join(args.directory, "Open A"), open_dir)
copy_contents(os.path.join(args.directory, "Open B"), open_dir)
copy_contents(os.path.join(args.directory, "Assigned A"), assigned_dir)
copy_contents(os.path.join(args.directory, "Assigned B"), assigned_dir)
