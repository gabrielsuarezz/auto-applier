"""
Robinhood – Software Engineer, Money Platform
Greenhouse Job ID: 7754143
URL: https://job-boards.greenhouse.io/robinhood/jobs/7754143
Generated: 2026-05-23
Mode: DRY-RUN  (set DRY_RUN = False to submit for real)
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, Page

# ── Configuration ────────────────────────────────────────────────────────────
DRY_RUN       = False
JOB_URL       = "https://job-boards.greenhouse.io/robinhood/jobs/7754143"
DATA_DIR      = Path(__file__).parent / "job-data"
RESUME_PDF    = DATA_DIR / "resume.pdf"
TRACKING_FILE = DATA_DIR / "applied_jobs.json"

# ── Applicant profile  (Phase-3 mapped) ──────────────────────────────────────
# Role type: Backend Platform Engineering (Fintech, distributed systems).
# Alt-bullets selected from Extended Context Library:
#   • Koombea  → Data/Architecture Focus  (multi-tenant Fintech SaaS, data isolation)
#   • JMG      → Spring Boot/AWS Focus    (microservices, concurrent REST APIs)
#   • ViewGuard highlighted for "secure, high-throughput services" angle.
#   • Pantheon / swarm AI angle de-prioritised (no AI requirement in JD).
APPLICANT = {
    "first_name":  "Gabriel",
    "last_name":   "Suarez",
    "email":       "gabrielsc05131@gmail.com",
    "phone":       "3057461592",
    "country":     "United States",
    "city":        "Miami, FL",          # Open to relocation – kept as current city
    "linkedin":    "https://linkedin.com/in/gabrielsuarezz",
    "website":     "https://gabrielsuarez.dev",
    # ── Application-specific answers ──────────────────────────────────────────
    "heard_about": "LinkedIn",
    "used_robinhood":         "Yes",
    "prior_robinhood_employ": "No",
    "us_work_auth":           "Yes",     # Auto-answer per clearance/eligibility rule
    "needs_sponsorship":      "No",
    "willing_office":         "Yes",
    "preferred_office":       "New York, NY",
    "has_conflict":           "No",
    "is_govt_official":       "No",
    # EEO (self-report – defaults to prefer-not-to-say)
    "gender":   "Prefer not to say",
    "ethnicity":"Prefer not to say",
    "veteran":  "I am not a protected veteran",
    "disability":"I don't wish to answer",
    "lgbtq":    "Prefer not to say",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}")


async def safe_fill(page: Page, selector: str, value: str, label: str) -> None:
    """Fill a text input if it exists; warn otherwise."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5_000)
        await locator.fill(value)
        log(f"  FILL  [{label}] → '{value}'")
    except Exception as exc:
        log(f"  WARN  [{label}] selector not found or timeout ({exc})")


async def safe_select(page: Page, selector: str, label_text: str, value: str) -> None:
    """
    Select an option in a <select> element.
    Tries both exact value match and partial label match.
    """
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5_000)
        try:
            await locator.select_option(label=value)
        except Exception:
            await locator.select_option(value=value)
        log(f"  SELECT [{label_text}] → '{value}'")
    except Exception as exc:
        log(f"  WARN  [{label_text}] could not select '{value}' ({exc})")


async def safe_upload(page: Page, selector: str, path: Path, label: str) -> None:
    """Attach a file to a file-input element using setInputFiles()."""
    if not path.exists():
        log(f"  ERROR [{label}] file not found: {path}")
        return
    try:
        locator = page.locator(selector).first
        await locator.set_input_files(str(path))
        log(f"  UPLOAD [{label}] → '{path.name}'")
    except Exception as exc:
        log(f"  WARN  [{label}] upload failed ({exc})")


def append_tracking(dry_run: bool) -> None:
    """Append this application's metadata to applied_jobs.json."""
    record = {
        "company":    "Robinhood",
        "role":       "Software Engineer, Money Platform",
        "url":        JOB_URL,
        "date":       datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "dry_run":    dry_run,
        "job_id":     "7754143",
        "resume_used": str(RESUME_PDF),
        "profile_mapping": {
            "koombea_bullet": "Data/Architecture Focus",
            "jmg_bullet":     "Spring Boot/AWS Focus",
            "secondary_project": "ViewGuard",
        },
    }
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE) as f:
            data = json.load(f)
    else:
        data = []
    data.append(record)
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)
    log(f"  TRACKED → {TRACKING_FILE}  (total records: {len(data)})")


# ── Main application flow ─────────────────────────────────────────────────────

async def run() -> None:
    log("=" * 68)
    log(f"AUTO-APPLIER  |  Robinhood – Software Engineer, Money Platform")
    log(f"Mode: {'DRY-RUN (submit() intercepted)' if DRY_RUN else '*** LIVE SUBMIT ***'}")
    log("=" * 68)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx     = await browser.new_context(accept_downloads=False)
        page    = await ctx.new_page()

        # ── Navigate ──────────────────────────────────────────────────────────
        log(f"NAV → {JOB_URL}")
        await page.goto(JOB_URL, wait_until="networkidle", timeout=60_000)
        log("Page loaded.")

        # ── Basic information ─────────────────────────────────────────────────
        log("--- Basic Information ---")
        await safe_fill(page, "input#first_name",                 APPLICANT["first_name"],  "First Name")
        await safe_fill(page, "input#last_name",                  APPLICANT["last_name"],   "Last Name")
        await safe_fill(page, "input#email",                      APPLICANT["email"],       "Email")
        await safe_fill(page, "input#phone",                      APPLICANT["phone"],       "Phone")

        # Country dropdown
        await safe_select(page, "select#job_application_answers_country", "Country", APPLICANT["country"])
        # Some Greenhouse forms expose country as a different selector:
        await safe_select(page, "select[name='job_application[country]']", "Country (alt)", APPLICANT["country"])

        await safe_fill(page, "input#job_application_location",   APPLICANT["city"],        "City/Location")

        # ── Document uploads ──────────────────────────────────────────────────
        log("--- Document Uploads ---")
        # Resume (required) – always use resume.pdf
        await safe_upload(page, "input#resume",              RESUME_PDF, "Resume/CV")
        # Cover letter (optional) – upload resume.pdf per resource-saving rule
        # (no cover letter generated; resume.pdf used as stand-in)
        await safe_upload(page, "input#cover_letter",        RESUME_PDF, "Cover Letter (resume.pdf stand-in)")

        # Greenhouse sometimes uses data-source-param selectors for file inputs:
        await safe_upload(
            page, "input[data-source-param='resume']",       RESUME_PDF, "Resume (alt selector)")
        await safe_upload(
            page, "input[data-source-param='cover_letter']", RESUME_PDF, "Cover Letter (alt selector)")

        # ── Professional profile ──────────────────────────────────────────────
        log("--- Professional Profile ---")
        await safe_fill(page, "input#job_application_answers_linkedin_profile_url",
                        APPLICANT["linkedin"], "LinkedIn")
        await safe_fill(page, "input#job_application_answers_website",
                        APPLICANT["website"],  "Website")

        # ── Job-related questions ─────────────────────────────────────────────
        log("--- Job-Related Questions ---")
        # "How did you hear about this job?"
        await safe_fill(
            page,
            "input[aria-label*='hear about'], textarea[aria-label*='hear about'], "
            "input[id*='hear_about'], input[name*='hear_about']",
            APPLICANT["heard_about"],
            "How did you hear about this job",
        )

        # "Have you used Robinhood?"
        await safe_select(
            page,
            "select[id*='used_robinhood'], select[name*='used_robinhood']",
            "Used Robinhood",
            APPLICANT["used_robinhood"],
        )

        # Prior employment at Robinhood (required)
        await safe_select(
            page,
            "select[id*='prior_robinhood'], select[name*='prior_robinhood'], "
            "select[id*='previous_employee']",
            "Prior Robinhood Employment",
            APPLICANT["prior_robinhood_employ"],
        )

        # US work authorization (required) – auto-answer Yes
        await safe_select(
            page,
            "select[id*='work_auth'], select[name*='work_auth'], "
            "select[id*='authorized'], select[name*='authorized']",
            "US Work Authorization",
            APPLICANT["us_work_auth"],
        )

        # Visa sponsorship (required)
        await safe_select(
            page,
            "select[id*='sponsorship'], select[name*='sponsorship'], "
            "select[id*='visa'], select[name*='visa']",
            "Visa Sponsorship",
            APPLICANT["needs_sponsorship"],
        )

        # Willing to work from listed offices
        await safe_select(
            page,
            "select[id*='office'], select[name*='office'], "
            "select[id*='in_person'], select[name*='in_person']",
            "Willing – Office",
            APPLICANT["willing_office"],
        )

        # Preferred office location
        await safe_select(
            page,
            "select[id*='preferred_office'], select[name*='preferred_office'], "
            "select[id*='location_preference']",
            "Preferred Office Location",
            APPLICANT["preferred_office"],
        )

        # ── Disclosure questions ──────────────────────────────────────────────
        log("--- Disclosure Questions ---")
        await safe_select(
            page,
            "select[id*='conflict'], select[name*='conflict']",
            "Personal/Familial Conflict",
            APPLICANT["has_conflict"],
        )
        await safe_select(
            page,
            "select[id*='government'], select[name*='government']",
            "Government Official",
            APPLICANT["is_govt_official"],
        )

        # ── EEO demographic fields ────────────────────────────────────────────
        log("--- EEO Demographic Information ---")
        await safe_select(page, "select#job_application_gender_id",       "Gender",     APPLICANT["gender"])
        await safe_select(page, "select#job_application_race_ethnicity_id","Ethnicity",  APPLICANT["ethnicity"])
        await safe_select(page, "select#job_application_veteran_status_id","Veteran",    APPLICANT["veteran"])
        await safe_select(page, "select#job_application_disability_status_id","Disability", APPLICANT["disability"])

        # ── Salary (if forced field appears) ─────────────────────────────────
        log("--- Salary (if present) ---")
        await safe_fill(
            page,
            "input[id*='salary'], input[name*='salary'], "
            "input[placeholder*='salary'], input[placeholder*='Salary']",
            "90000",
            "Desired Salary",
        )

        # ── Intercept / Submit ────────────────────────────────────────────────
        log("--- Submit Phase ---")
        submit_btn = page.locator("button[type='submit'], input[type='submit'], "
                                  "button:has-text('Submit application')").first

        if DRY_RUN:
            # Intercept: evaluate button text / form state without clicking
            try:
                btn_text = await submit_btn.inner_text(timeout=5_000)
                log(f"  DRY-RUN: Submit button found → '{btn_text.strip()}'")
                log("  DRY-RUN: submit() INTERCEPTED — form NOT submitted.")
            except Exception as exc:
                log(f"  DRY-RUN: Submit button not located ({exc}); form NOT submitted.")

            # Capture filled form state for verification
            log("--- Dry-Run Form State Snapshot ---")
            fields_snapshot = await page.evaluate("""() => {
                const inputs   = [...document.querySelectorAll('input:not([type=file]), textarea')];
                const selects  = [...document.querySelectorAll('select')];
                const snapshot = {};
                inputs.forEach(el  => { if (el.id || el.name) snapshot[el.id || el.name] = el.value; });
                selects.forEach(el => { if (el.id || el.name) snapshot[el.id || el.name] = el.value; });
                return snapshot;
            }""")
            log("  Snapshot (non-empty fields):")
            for k, v in fields_snapshot.items():
                if v:
                    log(f"    {k}: {v}")
        else:
            log("  LIVE: clicking Submit application …")
            await submit_btn.click()
            await page.wait_for_load_state("networkidle", timeout=30_000)
            log("  LIVE: form submitted. Final URL → " + page.url)

        await browser.close()

    # ── Append tracking record ────────────────────────────────────────────────
    log("--- Tracking ---")
    append_tracking(dry_run=DRY_RUN)
    log("Done.")
    log("=" * 68)


if __name__ == "__main__":
    asyncio.run(run())
