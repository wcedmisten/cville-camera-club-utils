# Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Before the meeting

## Members Choice

### Members Choice Renaming for Poll Unit Upload

```bash
python3 organize_members_choice_uploads.py --directory /path/to/"To Judge"
```

### Generate Powerpoint

In Poll Unit, for each poll export the `Images / Submissions` as Excel format.

Also export `Images / Submissions` as "All Files". This will produce the .zip files used below.

Finally you'll need the "key files" for the filename lookup. This will come from an email.

```bash
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
```

# After the meeting

Download scored file from Dropbox, e.g. Scored 2026- 9 Sep

```bash
mkdir ~/Downloads/aaaScoredSeptember
python3 rename_files.py ~/Downloads/"Scored 2026- 9 Sep.zip" ~/Downloads/aaaScoredSeptember
```

