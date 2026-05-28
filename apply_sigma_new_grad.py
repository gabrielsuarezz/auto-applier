"""
Job Application Script — DRY-RUN MODE
======================================
Company  : Sigma Computing
Role     : Software Engineer (New Grad Program)
Job ID   : 7690411003
URL      : https://job-boards.greenhouse.io/sigmacomputing/jobs/7690411003
Date     : 2026-05-27
Mode     : DRY-RUN (form is filled and navigated; submit() is intercepted, not executed)

IMPORTANT PATH NOTE:
  The canonical data directory per agent config is /job-data/.
  That path was not writable in this environment; /workspaces/auto-applier/job-data/
  is used as the functional equivalent. Place resume.pdf at that location before
  switching to live mode.

Phase 3 Mapping Applied:
  - Role type  : General Software Engineering (full-stack / scalability focus)
  - No AI/Agent boost (not an AI-specific role)
  - No Security boost (not a security role)
  - Cover letter slot → resume.pdf upload (no cover letter generated)
  - GPA         : Not forced into short-answer fields (present on PDF)
  - Work auth   : "No" to H-1B sponsorship requirement (auto-eligible)
  - Relocation  : "Yes"
  - Salary      : Not applicable (hourly rate role, no salary input field)
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, Page

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
DRY_RUN = True  # Set to False for live submission

DATA_DIR     = Path("/workspaces/auto-applier/job-data")
RESUME_PDF   = DATA_DIR / "resume.pdf"
APPLIED_JSON = DATA_DIR / "applied_jobs.json"

JOB_URL   = "https://job-boards.greenhouse.io/sigmacomputing/jobs/7690411003"
COMPANY   = "Sigma Computing"
ROLE      = "Software Engineer (New Grad Program)"
JOB_ID    = "7690411003"

# ─────────────────────────────────────────────
# APPLICANT PROFILE  (sourced from resume.md)
# Replace placeholders if resume.md is not yet
# present in the data directory.
# ─────────────────────────────────────────────
PROFILE = {
    "first_name"    : "FIRST_NAME_FROM_RESUME",   # e.g. "Gabriel"
    "last_name"     : "LAST_NAME_FROM_RESUME",    # e.g. "Suarez"
    "email"         : "gsuar092@fiu.edu",
    "phone"         : "PHONE_FROM_RESUME",
    "country"       : "United States",
    "city"          : "Miami",                    # current city; open to relocation
    "linkedin"      : "LINKEDIN_URL_FROM_RESUME",
    "website"       : "",                         # optional
    "pronouns"      : "He/Him",                   # adjust from resume if different
    "school"        : "Florida International University",
    "degree"        : "Bachelor of Science",
    "current_company": "",                        # new grad; leave blank / "N/A"
    # Position-specific answers
    "onsite_open"   : "Yes",                      # "Are you open to 4 days onsite?"
    "willing_to_relocate": "Yes",                 # "Willing to relocate?"
    "h1b_sponsorship_required": "No",             # "Would you require H-1B sponsorship?"
    # Voluntary demographics — leave blank to skip
    "gender"        : "",
    "hispanic_latino": "",
    "veteran_status": "",
    "disability"    : "",
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC] {msg}")


async def safe_fill(page: Page, selector: str, value: str, label: str = "") -> None:
    """Fill a text input if it exists, log the action."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5000)
        await locator.fill(value)
        log(f"  FILL  [{label or selector}] = '{value}'")
    except Exception as exc:
        log(f"  SKIP  [{label or selector}] — not found or timeout ({exc})")


async def safe_select(page: Page, selector: str, value: str, label: str = "") -> None:
    """Select a dropdown option by label text."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5000)
        await locator.select_option(label=value)
        log(f"  SELECT [{label or selector}] = '{value}'")
    except Exception as exc:
        log(f"  SKIP  [{label or selector}] — {exc}")


async def safe_upload(page: Page, selector: str, file_path: Path, label: str = "") -> None:
    """Upload a file to a file-input element."""
    if not file_path.exists():
        log(f"  ERROR [{label}] — file not found: {file_path}")
        return
    try:
        locator = page.locator(selector).first
        await locator.set_input_files(str(file_path))
        log(f"  UPLOAD [{label}] = {file_path.name}")
    except Exception as exc:
        log(f"  SKIP  [{label}] — {exc}")


async def update_applied_jobs(dry_run: bool) -> None:
    """Append this application's metadata to applied_jobs.json."""
    record = {
        "company"    : COMPANY,
        "role"       : ROLE,
        "job_id"     : JOB_ID,
        "url"        : JOB_URL,
        "date_applied": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "dry_run"    : dry_run,
    }
    existing: list = []
    if APPLIED_JSON.exists():
        try:
            with open(APPLIED_JSON, "r") as fh:
                existing = json.load(fh)
        except json.JSONDecodeError:
            existing = []
    existing.append(record)
    with open(APPLIED_JSON, "w") as fh:
        json.dump(existing, fh, indent=2)
    log(f"  LOGGED → {APPLIED_JSON} (dry_run={dry_run})")


# ─────────────────────────────────────────────
# MAIN APPLICATION FLOW
# ─────────────────────────────────────────────

async def run() -> None:
    log("=" * 60)
    log(f"JOB APPLICATION  {'[DRY-RUN]' if DRY_RUN else '[LIVE]'}")
    log(f"Company  : {COMPANY}")
    log(f"Role     : {ROLE}")
    log(f"URL      : {JOB_URL}")
    log("=" * 60)

    if not RESUME_PDF.exists():
        log(f"CRITICAL: resume.pdf not found at {RESUME_PDF}")
        log("Place resume.pdf in the data directory before running.")
        return

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page    = await context.new_page()

        # ── Navigate ──────────────────────────────────────────────
        log(f"Navigating to {JOB_URL} ...")
        await page.goto(JOB_URL, wait_until="networkidle", timeout=30000)
        log("Page loaded.")

        # ── Personal Information ──────────────────────────────────
        log("\n── Section: Personal Information ──")
        await safe_fill(page, "input[name='first_name'], #first_name",
                        PROFILE["first_name"], "First Name")
        await safe_fill(page, "input[name='last_name'], #last_name",
                        PROFILE["last_name"], "Last Name")
        await safe_fill(page, "input[name='email'], #email",
                        PROFILE["email"], "Email")
        await safe_fill(page, "input[name='phone'], #phone",
                        PROFILE["phone"], "Phone")

        # Country dropdown
        await safe_select(page,
                          "select[name='job_application[location_preference]'], "
                          "select[id*='country']",
                          PROFILE["country"], "Country")

        # City / location
        await safe_fill(page, "input[id*='location'], input[name*='location']",
                        PROFILE["city"], "Location (City)")

        # ── Resume Upload ─────────────────────────────────────────
        log("\n── Section: Resume / CV Upload ──")
        # Greenhouse file input is typically hidden; trigger via label click or direct
        await safe_upload(
            page,
            "input[type='file'][name*='resume'], "
            "input[type='file'][id*='resume'], "
            "input[type='file']",
            RESUME_PDF,
            "Resume/CV"
        )

        # ── Cover Letter Slot ─────────────────────────────────────
        # Per agent policy: upload resume.pdf here instead of generating a letter
        log("\n── Section: Cover Letter (uploading resume.pdf per policy) ──")
        await safe_upload(
            page,
            "input[type='file'][name*='cover'], "
            "input[type='file'][id*='cover']",
            RESUME_PDF,
            "Cover Letter → resume.pdf"
        )

        # ── Education ─────────────────────────────────────────────
        log("\n── Section: Education ──")
        await safe_select(page,
                          "select[id*='school'], select[name*='school']",
                          PROFILE["school"], "School")
        await safe_select(page,
                          "select[id*='degree'], select[name*='degree']",
                          PROFILE["degree"], "Degree")

        # ── Additional Profile ────────────────────────────────────
        log("\n── Section: Additional Profile ──")
        await safe_select(page,
                          "select[id*='pronoun'], select[name*='pronoun']",
                          PROFILE["pronouns"], "Personal Pronouns")
        await safe_fill(page,
                        "input[id*='linkedin'], input[name*='linkedin']",
                        PROFILE["linkedin"], "LinkedIn Profile")
        if PROFILE["website"]:
            await safe_fill(page,
                            "input[id*='website'], input[name*='website']",
                            PROFILE["website"], "Website")

        # ── Position-Specific Questions ───────────────────────────
        log("\n── Section: Position-Specific Questions ──")

        # "Are you open to working 4 days onsite?"
        await safe_select(
            page,
            "select[id*='onsite'], select[id*='4_day'], "
            "select[id*='office']",
            PROFILE["onsite_open"],
            "Open to 4 days onsite?"
        )

        # "Willing to relocate?"
        await safe_select(
            page,
            "select[id*='relocat']",
            PROFILE["willing_to_relocate"],
            "Willing to relocate?"
        )

        # "Current company"
        await safe_fill(page,
                        "input[id*='current_company'], input[name*='company']",
                        PROFILE["current_company"] or "N/A",
                        "Current Company")

        # ── Legal / Compliance ────────────────────────────────────
        log("\n── Section: Legal / Compliance ──")

        # H-1B sponsorship required? → "No" (agent auto-eligible rule)
        await safe_select(
            page,
            "select[id*='h1b'], select[id*='sponsor'], select[id*='visa']",
            PROFILE["h1b_sponsorship_required"],
            "Require H-1B sponsorship?"
        )

        # Privacy notice checkbox
        try:
            cb = page.locator(
                "input[type='checkbox'][id*='privacy'], "
                "input[type='checkbox'][id*='tos'], "
                "input[type='checkbox'][id*='agree']"
            ).first
            await cb.check()
            log("  CHECK  [Privacy / Truthfulness acknowledgment]")
        except Exception as exc:
            log(f"  SKIP  [Privacy checkbox] — {exc}")

        # ── Voluntary Demographics (leave blank = not answering) ──
        log("\n── Section: Voluntary Demographics (skipped per applicant preference) ──")
        log("  INFO  Demographic dropdowns left at default (prefer not to answer).")

        # ── Submit Interception ───────────────────────────────────
        log("\n── Section: Form Submission ──")
        if DRY_RUN:
            log("  DRY-RUN: Intercepting submit — NOT submitting the form.")
            log("  Would have clicked: button[type='submit'], input[type='submit']")

            # Snapshot current form state for audit
            form_data = await page.evaluate("""() => {
                const form = document.querySelector('form');
                if (!form) return {};
                const data = {};
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(el => {
                    const key = el.name || el.id || el.type;
                    if (key && el.type !== 'file') {
                        data[key] = el.value || (el.checked ? 'checked' : '');
                    } else if (el.type === 'file' && el.files.length > 0) {
                        data[key] = '[FILE: ' + el.files[0].name + ']';
                    }
                });
                return data;
            }""")
            log("\n  ── Form State Snapshot ──")
            for k, v in form_data.items():
                if v:
                    log(f"    {k}: {v}")
        else:
            # LIVE MODE: actually click submit
            submit_btn = page.locator("button[type='submit'], input[type='submit']").first
            await submit_btn.click()
            await page.wait_for_load_state("networkidle", timeout=15000)
            log("  SUBMITTED. Final URL: " + page.url)

        await browser.close()

    # ── Append to applied_jobs.json ───────────────────────────────
    log("\n── Logging application metadata ──")
    await update_applied_jobs(dry_run=DRY_RUN)

    log("\n" + "=" * 60)
    log(f"COMPLETE — {'DRY-RUN' if DRY_RUN else 'LIVE'} application finished.")
    log("=" * 60)


if __name__ == "__main__":
    asyncio.run(run())
