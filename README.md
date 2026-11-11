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

Download the `Images / Submissions` Excel export and the "All Files" zip for each poll. Set `POLLUNIT_SESSION` to the value of the `_pollunit_session` cookie from a browser logged in to Poll Unit (DevTools → Storage/Application → Cookies). The polls whose titles start with `--month` (default: the current month) are found automatically:

```bash
export POLLUNIT_SESSION=...
python3 fetch_pollunit.py --month "November 2026" --out-dir ~/Downloads
```

Admin links can be passed directly instead, e.g. `python3 fetch_pollunit.py "https://pollunit.com/polls/<admin hash>"`.

This writes `<poll_name>.zip` and `<poll_name>-images_submissions.xlsx` for each poll, then prints the `create_members_choice_ppt.py` command below filled in for that month.

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

