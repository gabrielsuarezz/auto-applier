import json
import os
import re
import shutil

APPLIED_JOBS_FILE = "job-data/applied_jobs.json"
PROCESSED_DIR = "job-data/processed"
QUEUE_DIR = "job-data/queue"


def get_next_queue_index():
    indices = [
        int(re.search(r"\d+", f).group())
        for f in os.listdir(QUEUE_DIR)
        if re.match(r"job_\d+\.md", f)
    ]
    return max(indices, default=0) + 1


def normalize_url(url):
    return re.sub(r"^https?://", "", url)


def find_processed_file_for_url(url):
    needle = normalize_url(url)
    for fname in sorted(os.listdir(PROCESSED_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(PROCESSED_DIR, fname)
        with open(fpath) as f:
            if needle in normalize_url(f.read()):
                return fpath
    return None


with open(APPLIED_JOBS_FILE) as f:
    jobs = json.load(f)

dry_run_jobs = [j for j in jobs if j.get("dry_run") is True]
print(f"Found {len(dry_run_jobs)} dry-run entries in applied_jobs.json.\n")

next_index = get_next_queue_index()
requeued = []
not_found = []
seen_urls = set()

for job in dry_run_jobs:
    url = job.get("url", "")
    if url in seen_urls:
        print(f"  Skipping duplicate URL: {url}")
        continue
    seen_urls.add(url)

    src = find_processed_file_for_url(url)
    if src is None:
        print(f"  WARNING: No processed file found for {job.get('company')} ({url})")
        not_found.append(job)
        continue

    dest = os.path.join(QUEUE_DIR, f"job_{next_index}.md")
    shutil.move(src, dest)
    print(f"  Requeued: {os.path.basename(src)} -> job_{next_index}.md  [{job.get('company')} - {job.get('role')}]")
    requeued.append(job)
    next_index += 1

print(f"\nDone. {len(requeued)} job(s) restored to queue. {len(not_found)} not found in processed/.")
