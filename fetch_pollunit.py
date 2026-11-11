import argparse
import html
import json
import os
import random
import re
import shlex
import sys
import time
from datetime import date, datetime
import zipfile

import requests

BASE_URL = "https://pollunit.com/en/polls"
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:159.0) Gecko/20100101 Firefox/159.0"

parser = argparse.ArgumentParser(
    description="Download the Images/Submissions Excel export and all image files for PollUnit polls",
)
parser.add_argument("polls", nargs="*", help="PollUnit admin links or poll admin hashes. If omitted, polls are found by --month")
parser.add_argument("--month", default=date.today().strftime("%B %Y"), help="Find polls whose title starts with this, e.g. 'November 2026'. Defaults to the current month")
parser.add_argument("--out-dir", default=os.path.expanduser("~/Downloads"), help="Directory to write the .xlsx and .zip files to")
parser.add_argument("--delay", type=float, default=1.0, help="Average seconds to wait before each request. Each wait is randomized between half and one and a half times this")
parser.add_argument("--timeout", type=int, default=120, help="Seconds to wait for the Excel export to be generated")
args = parser.parse_args()

session_cookie = os.environ.get("POLLUNIT_SESSION")
if not session_cookie:
    sys.exit("Set POLLUNIT_SESSION to the value of the _pollunit_session cookie from a logged-in browser")



class DelayedSession(requests.Session):
    def request(self, *request_args, **request_kwargs):
        time.sleep(random.uniform(0.5 * args.delay, 1.5 * args.delay))
        return super().request(*request_args, **request_kwargs)


session = DelayedSession()
session.headers["User-Agent"] = USER_AGENT
session.cookies.set("_pollunit_session", session_cookie, domain="pollunit.com")

xhr_headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "text/javascript, application/javascript, */*; q=0.01",
}


def poll_hash(poll):
    match = re.search(r"/polls/([A-Za-z0-9_-]+)", poll)
    return match.group(1) if match else poll


def unescape_js(text):
    return text.replace('\\"', '"').replace("\\/", "/").replace("\\n", "\n")


def list_polls():
    polls = []
    page = 1
    while True:
        params = {"page": page, "paging": "true"} if page > 1 else None
        response = session.get(BASE_URL, params=params, headers=xhr_headers if page > 1 else None)
        response.raise_for_status()
        found = re.findall(r'href="/polls/([A-Za-z0-9_-]+)\?ADMIN_LINK=DO_NOT_SHARE">([^<]*)', unescape_js(response.text))
        if not found:
            break
        polls.extend((poll_id, html.unescape(title).strip()) for poll_id, title in found)
        page += 1
    if not polls:
        sys.exit("Could not find any polls. Is the session cookie still valid?")
    return polls


def find_polls_for_month(month):
    polls = list_polls()
    matches = [(poll_id, title) for poll_id, title in polls if title.lower().startswith(month.lower())]
    if not matches:
        recent = "\n".join(f"  {title}" for _, title in polls[:10])
        sys.exit(f"No polls found with a title starting with '{month}'. Most recent polls:\n{recent}")
    print(f"Found {len(matches)} poll(s) for '{month}':")
    for _, title in matches:
        print(f"  {title}")
    if input("Download these polls? [y/N] ").strip().lower() not in ("y", "yes"):
        sys.exit("Cancelled")
    return matches


def get_download_list(poll_id):
    response = session.get(f"{BASE_URL}/{poll_id}/exports/download_all_files", headers=xhr_headers)
    response.raise_for_status()
    text = unescape_js(response.text)
    files_match = re.search(r'data-download-and-zip-files="([^"]*)"', text)
    name_match = re.search(r'data-download-and-zip-filename="([^"]*)"', text)
    if not files_match or not name_match:
        sys.exit(f"Could not find the file list for poll {poll_id}. Is the session cookie still valid and is this an admin link?")
    batches = json.loads(html.unescape(files_match.group(1)))
    files = [entry for batch in batches for entry in batch]
    return html.unescape(name_match.group(1)), files


def download_images_zip(poll_id, out_dir):
    name, files = get_download_list(poll_id)
    zip_path = os.path.join(out_dir, f"{name}.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for index, (url, filename) in enumerate(files, start=1):
            print(f"  [{index}/{len(files)}] {filename}")
            image = session.get(url)
            image.raise_for_status()
            zf.writestr(filename, image.content)
    return name, zip_path


def get_csrf_token(poll_id):
    response = session.get(f"{BASE_URL}/{poll_id}")
    response.raise_for_status()
    match = re.search(r'name="csrf-token" content="([^"]+)"', response.text)
    if not match:
        sys.exit(f"Could not find a CSRF token for poll {poll_id}. Is the session cookie still valid?")
    return match.group(1)


def download_xlsx(poll_id, name, out_dir):
    token = get_csrf_token(poll_id)
    response = session.post(
        f"{BASE_URL}/{poll_id}/exports",
        params={"export_format": "xlsx", "export_type": "options"},
        headers={**xhr_headers, "X-CSRF-Token": token, "Origin": "https://pollunit.com"},
    )
    response.raise_for_status()
    export_ids = [int(i) for i in re.findall(r'id=\\?"export-(\d+)', response.text)]
    if not export_ids:
        sys.exit(f"Export request for poll {poll_id} did not return an export id")
    export_id = max(export_ids)

    deadline = time.time() + args.timeout
    while True:
        result = session.get(f"{BASE_URL}/{poll_id}/exports/{export_id}.xlsx")
        if result.ok and result.headers.get("Content-Type", "").startswith(XLSX_CONTENT_TYPE):
            break
        if time.time() > deadline:
            sys.exit(f"Timed out waiting for export {export_id} of poll {poll_id}")
        time.sleep(3)

    xlsx_path = os.path.join(out_dir, f"{name}-images_submissions.xlsx")
    with open(xlsx_path, "wb") as f:
        f.write(result.content)
    return xlsx_path


os.makedirs(args.out_dir, exist_ok=True)


def titles_for(poll_ids):
    titles = dict(list_polls())
    return [(poll_id, titles.get(poll_id, poll_id)) for poll_id in poll_ids]


def print_next_command(downloads):
    open_polls = [d for d in downloads if re.search(r"\bopen\b", d["title"], re.IGNORECASE)]
    assigned_polls = [d for d in downloads if re.search(r"\bassigned\b", d["title"], re.IGNORECASE)]
    if len(open_polls) != 1 or len(assigned_polls) != 1:
        print("\nCould not pick out exactly one Open and one Assigned poll, so no create_members_choice_ppt.py command was generated")
        return

    open_poll, assigned_poll = open_polls[0], assigned_polls[0]
    date_match = re.match(r"([A-Za-z]+ \d{4})", assigned_poll["title"])
    topic_match = re.search(r"\bassigned\s*-\s*(.+)$", assigned_poll["title"], re.IGNORECASE)
    if not date_match or not topic_match:
        print(f"\nCould not read the month and topic from '{assigned_poll['title']}', so no create_members_choice_ppt.py command was generated")
        return

    event_date = date_match.group(1)
    month = datetime.strptime(event_date, "%B %Y")
    key_prefix = month.strftime("%Y_%m")
    out = lambda filename: shlex.quote(os.path.join(args.out_dir, filename))
    lines = [
        "python3 create_members_choice_ppt.py",
        f"--date {shlex.quote(event_date)}",
        f"--assigned-topic-name {shlex.quote(topic_match.group(1).strip())}",
        f"--open-zip {shlex.quote(open_poll['zip'])}",
        f"--assigned-zip {shlex.quote(assigned_poll['zip'])}",
        f"--open-excel {shlex.quote(open_poll['xlsx'])}",
        f"--assigned-excel {shlex.quote(assigned_poll['xlsx'])}",
        f"--open-with-names {out(f'{key_prefix}_MC Open.txt')}",
        f"--assigned-with-names {out(f'{key_prefix}_MC Assigned.txt')}",
        f"--output {out(month.strftime('%B%YMembersChoice.pptx'))}",
    ]
    print("\nNext, save the key files from the email to the paths below and run:\n")
    print(" \\\n    ".join(lines))


if args.polls:
    polls = titles_for([poll_hash(poll) for poll in args.polls])
else:
    polls = find_polls_for_month(args.month)

downloads = []
for poll_id, title in polls:
    print(f"{title}: downloading images")
    name, zip_path = download_images_zip(poll_id, args.out_dir)
    print(f"{title}: generating Excel export")
    xlsx_path = download_xlsx(poll_id, name, args.out_dir)
    print(f"Wrote {zip_path}")
    print(f"Wrote {xlsx_path}")
    downloads.append({"title": title, "zip": zip_path, "xlsx": xlsx_path})

print_next_command(downloads)
