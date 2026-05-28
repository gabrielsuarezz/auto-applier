import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SERPER_API_KEY")
QUEUE_DIR = "job-data/queue"
APPLIED_JOBS_FILE = "job-data/applied_jobs.json"

VALID_DOMAINS = ("boards.greenhouse.io", "job-boards.greenhouse.io", "jobs.lever.co")

REJECT_KEYWORDS = [
    "senior", "sr.", "staff", "principal", "lead", "manager", "director",
    "3+ years", "4+ years", "5+ years", "3-5 years", "4-6 years", "5-7 years",
    "3 years of", "4 years of", "5 years of",
    "3+ yrs", "4+ yrs", "5+ yrs",
]

QUERIES = [
    "software engineer new grad 2025 boards.greenhouse.io",
    "software engineer entry level 2025 jobs.lever.co",
    "new grad software engineer 2026 job-boards.greenhouse.io",
    "junior software engineer 2025 jobs.lever.co",
]


def normalize_url(url):
    return re.sub(r"^https?://", "", url.strip().rstrip("/").lower())


def load_seen_urls():
    seen = set()

    # URLs already applied to
    if os.path.exists(APPLIED_JOBS_FILE):
        with open(APPLIED_JOBS_FILE) as f:
            try:
                applied = json.load(f)
            except json.JSONDecodeError:
                applied = []
        for job in applied:
            url = job.get("url", "")
            if url:
                seen.add(normalize_url(url))
                # also add without /apply suffix in case of variant
                seen.add(normalize_url(url).rstrip("/apply").rstrip("/"))

    # URLs already sitting in the queue
    for fname in os.listdir(QUEUE_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(QUEUE_DIR, fname)
        with open(fpath) as f:
            first_line = f.readline()
        match = re.match(r"URL:\s*(.+)", first_line)
        if match:
            seen.add(normalize_url(match.group(1)))

    return seen


def scrape_jobs():
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }

    raw_results = []
    for q in QUERIES:
        payload = {"q": q, "num": 20}
        response = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
        response.raise_for_status()
        raw_results.extend(response.json().get("organic", []))

    seen_urls = load_seen_urls()

    existing_indices = [
        int(re.search(r"\d+", f).group())
        for f in os.listdir(QUEUE_DIR)
        if re.match(r"job_\d+\.md", f)
    ]
    next_index = max(existing_indices, default=0) + 1

    jobs_added = 0
    skipped_senior = 0
    skipped_seen = 0
    skipped_domain = 0

    dedup_this_run = set()

    for result in raw_results:
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        title = result.get("title", "").lower()
        text = snippet.lower() + " " + title

        if not any(domain in link for domain in VALID_DOMAINS):
            skipped_domain += 1
            continue

        normalized = normalize_url(link)
        if normalized in seen_urls or normalized in dedup_this_run:
            skipped_seen += 1
            continue

        if any(kw in text for kw in REJECT_KEYWORDS):
            skipped_senior += 1
            continue

        dedup_this_run.add(normalized)

        file_path = os.path.join(QUEUE_DIR, f"job_{next_index}.md")
        with open(file_path, "w") as f:
            f.write(f"URL: {link}\n\n{snippet}")

        jobs_added += 1
        next_index += 1

    print(f"Scrape complete.")
    print(f"  Added to queue : {jobs_added}")
    print(f"  Skipped (seen) : {skipped_seen}  (already applied or already queued)")
    print(f"  Skipped (senior): {skipped_senior}")
    print(f"  Skipped (domain): {skipped_domain}")


if __name__ == "__main__":
    scrape_jobs()
