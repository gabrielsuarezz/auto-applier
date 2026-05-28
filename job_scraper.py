import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SERPER_API_KEY")
QUEUE_DIR = "job-data/queue"

def scrape_jobs():
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    VALID_DOMAINS = ("boards.greenhouse.io", "job-boards.greenhouse.io", "jobs.lever.co")

    queries = [
        "software engineer new grad 2025 boards.greenhouse.io",
        "software engineer entry level 2025 jobs.lever.co",
    ]

    raw_results = []
    for q in queries:
        payload = {"q": q, "num": 20}
        response = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
        response.raise_for_status()
        raw_results.extend(response.json().get("organic", []))

    REJECT_KEYWORDS = [
        "senior", "sr.", "staff", "principal", "lead", "manager", "director",
        "3+ years", "4+ years", "5+ years", "3-5 years", "4-6 years", "5-7 years",
        "3 years of", "4 years of", "5 years of",
        "3+ yrs", "4+ yrs", "5+ yrs",
    ]
    ACCEPT_KEYWORDS = [
        "new grad", "new-grad", "entry level", "entry-level", "junior",
        "0-2 years", "0-1 year", "early career", "graduate", "intern",
        "university grad", "campus hire",
    ]

    seen_links = set()
    valid_results = []
    filtered_out = []
    for result in raw_results:
        link = result.get("link", "")
        snippet = result.get("snippet", "").lower()
        title = result.get("title", "").lower()
        text = snippet + " " + title

        if not any(domain in link for domain in VALID_DOMAINS):
            continue
        if link in seen_links:
            continue

        if any(kw in text for kw in REJECT_KEYWORDS):
            filtered_out.append((link, "senior/experienced role"))
            continue

        seen_links.add(link)
        valid_results.append(result)

    existing = [
        f for f in os.listdir(QUEUE_DIR)
        if f.startswith("job_") and f.endswith(".md")
    ]
    next_index = max(
        (int(f.replace("job_", "").replace(".md", "")) for f in existing),
        default=0
    ) + 1

    jobs_added = 0
    skipped = 0
    for i, result in enumerate(valid_results, start=next_index):
        link = result.get("link", "")
        snippet = result.get("snippet", "")

        file_path = os.path.join(QUEUE_DIR, f"job_{i}.md")
        with open(file_path, "w") as f:
            f.write(f"URL: {link}\n\n{snippet}")

        jobs_added += 1

    print(f"✅ Scrape complete. {jobs_added} job(s) added to {QUEUE_DIR}/")
    print(f"   Filtered out: {len(filtered_out)} senior/experienced roles, {len(raw_results) - len(valid_results) - len(filtered_out)} non-job-board URLs")

if __name__ == "__main__":
    scrape_jobs()
