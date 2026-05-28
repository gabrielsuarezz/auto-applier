"""
SmithRx – Software Engineer, New Grad
Greenhouse Job ID: 8477698002
URL: https://job-boards.greenhouse.io/smithrx/jobs/8477698002
Generated: 2026-05-23
Mode: DRY-RUN  (set DRY_RUN = False to submit for real)

── Phase-3 Profile Mapping ──────────────────────────────────────────────────
Role type : AI / Agent Engineering (RAG pipelines, LLM safety, GenAI)
Primary   : Voxtant – LLM/Agent Focus
             "Engineered production LLM integrations using OpenAI API and
              Groq, implementing advanced prompt engineering, structured
              output parsing, and streaming responses."
             (Closest available mapping to Pantheon swarm-agent framing)
Koombea   : API Focus – GraphQL integration, optimised API efficiency
JMG       : FastAPI Focus – PostgreSQL, automated backend services
GPA       : 3.5 / 4.0  (explicitly required field – included)
Cover Ltr : resume.pdf uploaded in cover-letter slot (none generated)
Salary    : 90000 (if forced field appears)
Work Auth : Yes  (auto-answer per clearance/eligibility rule)
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright, Page

# ── Configuration ─────────────────────────────────────────────────────────────
DRY_RUN       = True
JOB_URL       = "https://job-boards.greenhouse.io/smithrx/jobs/8477698002"
DATA_DIR      = Path(__file__).parent / "job-data"
RESUME_PDF    = DATA_DIR / "resume.pdf"
TRACKING_FILE = DATA_DIR / "applied_jobs.json"

# ── Applicant profile (Phase-3 mapped) ───────────────────────────────────────
APPLICANT = {
    # ── Personal info ─────────────────────────────────────────────────────────
    "first_name":       "Gabriel",
    "last_name":        "Suarez",
    "email":            "gabrielsc05131@gmail.com",
    "phone":            "3057461592",
    "country":          "United States",
    "city":             "Miami, FL",          # Open to nationwide relocation
    "linkedin":         "https://linkedin.com/in/gabrielsuarezz",
    "website":          "https://gabrielsuarez.dev",
    # ── Academic ──────────────────────────────────────────────────────────────
    "gpa":              "3.5",                # Explicitly required field
    "graduation_year":  "2026",
    "graduation_month": "August",
    "graduation_date":  "08/2026",            # Aug 2026 per resume
    "degree":           "Bachelor of Science in Computer Science",
    "university":       "Florida International University",
    # ── Application-specific answers ─────────────────────────────────────────
    "heard_about":       "LinkedIn",
    "us_work_auth":      "Yes",               # Auto-answer per clearance/eligibility rule
    "needs_sponsorship": "No",
    "available_fulltime":"Yes",               # Role asks for immediate availability
    "start_date":        "Immediately",
    # ── EEO (self-report – prefer-not-to-say defaults) ───────────────────────
    "gender":      "Prefer not to say",
    "ethnicity":   "Prefer not to say",
    "veteran":     "I am not a protected veteran",
    "disability":  "I don't wish to answer",
}

# ── Cover letter text (NOT used – resume.pdf uploaded instead) ───────────────
# Per policy: no cover letter generated; resume.pdf used in that slot.


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}")


async def safe_fill(page: Page, selector: str, value: str, label: str) -> None:
    """Fill a visible text/textarea input; warn if not found."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5_000)
        await locator.fill(value)
        log(f"  FILL   [{label}] → '{value}'")
    except Exception as exc:
        log(f"  WARN   [{label}] not found or timeout — {exc}")


async def safe_select(page: Page, selector: str, label: str, value: str) -> None:
    """Select an option in a <select>; tries label then value match."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5_000)
        try:
            await locator.select_option(label=value)
        except Exception:
            await locator.select_option(value=value)
        log(f"  SELECT [{label}] → '{value}'")
    except Exception as exc:
        log(f"  WARN   [{label}] could not select '{value}' — {exc}")


async def safe_radio(page: Page, selector: str, label: str) -> None:
    """Click a radio button or checkbox by selector."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5_000)
        await locator.check()
        log(f"  CHECK  [{label}]")
    except Exception as exc:
        log(f"  WARN   [{label}] radio/checkbox not found — {exc}")


async def safe_upload(page: Page, selector: str, path: Path, label: str) -> None:
    """Attach a file to a file-input using setInputFiles()."""
    if not path.exists():
        log(f"  ERROR  [{label}] file not found: {path}")
        return
    try:
        locator = page.locator(selector).first
        await locator.set_input_files(str(path))
        log(f"  UPLOAD [{label}] → '{path.name}'")
    except Exception as exc:
        log(f"  WARN   [{label}] upload failed — {exc}")


def append_tracking(dry_run: bool) -> None:
    """Append this application's metadata to applied_jobs.json."""
    record = {
        "company":          "SmithRx",
        "role":             "Software Engineer, New Grad",
        "url":              JOB_URL,
        "date":             datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "dry_run":          dry_run,
        "job_id":           "8477698002",
        "resume_used":      str(RESUME_PDF),
        "script":           "apply_smithrx_8477698002.py",
        "execution_status": "script_ready_playwright_unavailable_in_sandbox",
        "profile_mapping": {
            "role_type":        "AI / Agent Engineering (RAG, LLM safety, GenAI)",
            "koombea_bullet":   "API Focus — GraphQL integration, optimised API efficiency",
            "jmg_bullet":       "FastAPI Focus — PostgreSQL, automated backend services",
            "primary_project":  "Voxtant (LLM/Agent Focus) — production LLM integrations, "
                                "agent workflows, prompt engineering (Pantheon proxy)",
            "secondary_project":"Helios AI (autonomous system, CNN-based tracking)",
            "viewguard_used":   False,
            "pantheon_used":    True,   # Voxtant used as closest Pantheon proxy
            "gpa_in_text_box":  True,   # GPA field explicitly required on this form
            "gpa_value":        "3.5",
            "cover_letter_slot":"resume.pdf uploaded (no cover letter generated)",
            "salary_field":     "90000",
            "us_work_auth_answer": "Yes",
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
    log("AUTO-APPLIER  |  SmithRx – Software Engineer, New Grad")
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
        await safe_fill(page, "input#first_name",  APPLICANT["first_name"], "First Name")
        await safe_fill(page, "input#last_name",   APPLICANT["last_name"],  "Last Name")
        await safe_fill(page, "input#email",        APPLICANT["email"],      "Email")
        await safe_fill(page, "input#phone",        APPLICANT["phone"],      "Phone")

        # Location / city
        await safe_fill(page, "input#job_application_location",
                        APPLICANT["city"], "City/Location")

        # Country dropdown (standard Greenhouse selector + alt)
        await safe_select(page, "select#job_application_answers_country",
                          "Country", APPLICANT["country"])
        await safe_select(page, "select[name='job_application[country]']",
                          "Country (alt)", APPLICANT["country"])

        # ── Document uploads ──────────────────────────────────────────────────
        log("--- Document Uploads ---")
        # Resume (required) – ALWAYS use resume.pdf
        await safe_upload(page, "input#resume",                       RESUME_PDF, "Resume/CV")
        await safe_upload(page, "input[data-source-param='resume']",  RESUME_PDF, "Resume (alt)")

        # Cover letter (optional) – upload resume.pdf per resource-saving policy
        await safe_upload(page, "input#cover_letter",                           RESUME_PDF,
                          "Cover Letter (resume.pdf stand-in)")
        await safe_upload(page, "input[data-source-param='cover_letter']",      RESUME_PDF,
                          "Cover Letter (alt selector, resume.pdf stand-in)")

        # ── Professional profile links ─────────────────────────────────────────
        log("--- Professional Profile ---")
        await safe_fill(
            page,
            "input#job_application_answers_linkedin_profile_url, "
            "input[id*='linkedin']",
            APPLICANT["linkedin"], "LinkedIn",
        )
        await safe_fill(
            page,
            "input#job_application_answers_website, "
            "input[id*='website'], input[id*='portfolio']",
            APPLICANT["website"], "Website / Portfolio",
        )

        # ── Academic information ───────────────────────────────────────────────
        log("--- Academic Information ---")
        # GPA – explicitly required on this form → fill per policy
        await safe_fill(
            page,
            "input[id*='gpa'], input[name*='gpa'], "
            "input[placeholder*='GPA'], input[placeholder*='gpa']",
            APPLICANT["gpa"], "GPA",
        )
        # Graduation year / date
        await safe_fill(
            page,
            "input[id*='graduation'], input[name*='graduation'], "
            "input[placeholder*='graduation'], input[placeholder*='Graduation']",
            APPLICANT["graduation_date"], "Graduation Date",
        )
        await safe_select(
            page,
            "select[id*='graduation'], select[name*='graduation']",
            "Graduation Year (select)", APPLICANT["graduation_year"],
        )
        # University / school name
        await safe_fill(
            page,
            "input[id*='university'], input[id*='school'], "
            "input[name*='university'], input[name*='school']",
            APPLICANT["university"], "University",
        )
        # Degree field
        await safe_fill(
            page,
            "input[id*='degree'], input[name*='degree']",
            APPLICANT["degree"], "Degree",
        )

        # ── How did you hear about this job ───────────────────────────────────
        log("--- Source Question ---")
        await safe_fill(
            page,
            "input[aria-label*='hear'], textarea[aria-label*='hear'], "
            "input[id*='hear'], input[name*='hear'], "
            "input[id*='source'], input[name*='source']",
            APPLICANT["heard_about"], "How did you hear about this job",
        )

        # ── Work authorisation / eligibility ──────────────────────────────────
        log("--- Work Authorization (auto-answer per policy) ---")
        # Select-based auth question
        await safe_select(
            page,
            "select[id*='work_auth'], select[name*='work_auth'], "
            "select[id*='authorized'], select[name*='authorized'], "
            "select[id*='eligible'], select[name*='eligible']",
            "US Work Authorization", APPLICANT["us_work_auth"],
        )
        # Radio-based auth question (Yes)
        await safe_radio(
            page,
            "input[type='radio'][value='Yes'][name*='auth'], "
            "input[type='radio'][value='yes'][name*='auth'], "
            "input[type='radio'][id*='auth_yes']",
            "US Work Auth – Yes (radio)",
        )
        # Sponsorship
        await safe_select(
            page,
            "select[id*='sponsorship'], select[name*='sponsorship'], "
            "select[id*='visa'], select[name*='visa']",
            "Visa Sponsorship", APPLICANT["needs_sponsorship"],
        )
        await safe_radio(
            page,
            "input[type='radio'][value='No'][name*='sponsor'], "
            "input[type='radio'][value='no'][name*='sponsor']",
            "Visa Sponsorship – No (radio)",
        )

        # ── Availability / start date ─────────────────────────────────────────
        log("--- Availability ---")
        await safe_select(
            page,
            "select[id*='available'], select[name*='available'], "
            "select[id*='start'], select[name*='start']",
            "Full-time Availability", APPLICANT["available_fulltime"],
        )
        await safe_fill(
            page,
            "input[id*='start_date'], input[name*='start_date'], "
            "input[placeholder*='start']",
            APPLICANT["start_date"], "Start Date",
        )

        # ── Salary (if a forced field appears) ────────────────────────────────
        log("--- Salary (if present) ---")
        await safe_fill(
            page,
            "input[id*='salary'], input[name*='salary'], "
            "input[placeholder*='salary'], input[placeholder*='Salary'], "
            "input[placeholder*='compensation']",
            "90000", "Desired Salary",
        )

        # ── EEO / demographic fields ──────────────────────────────────────────
        log("--- EEO Demographic Information ---")
        await safe_select(page, "select#job_application_gender_id",
                          "Gender",    APPLICANT["gender"])
        await safe_select(page, "select#job_application_race_ethnicity_id",
                          "Ethnicity", APPLICANT["ethnicity"])
        await safe_select(page, "select#job_application_veteran_status_id",
                          "Veteran",   APPLICANT["veteran"])
        await safe_select(page, "select#job_application_disability_status_id",
                          "Disability",APPLICANT["disability"])

        # ── Intercept / Submit ────────────────────────────────────────────────
        log("--- Submit Phase ---")
        submit_btn = page.locator(
            "button[type='submit'], input[type='submit'], "
            "button:has-text('Submit application'), "
            "button:has-text('Submit Application')"
        ).first

        if DRY_RUN:
            # Locate the button and log its state without clicking
            try:
                btn_text = await submit_btn.inner_text(timeout=5_000)
                log(f"  DRY-RUN: Submit button found → '{btn_text.strip()}'")
                log("  DRY-RUN: submit() INTERCEPTED — form NOT submitted.")
            except Exception as exc:
                log(f"  DRY-RUN: Submit button not located ({exc}); form NOT submitted.")

            # Capture a snapshot of all filled form fields for verification
            log("--- Dry-Run Form State Snapshot ---")
            fields_snapshot = await page.evaluate("""() => {
                const inputs  = [...document.querySelectorAll('input:not([type=file]), textarea')];
                const selects = [...document.querySelectorAll('select')];
                const snap = {};
                inputs.forEach(el  => { if (el.id || el.name) snap[el.id || el.name] = el.value; });
                selects.forEach(el => { if (el.id || el.name) snap[el.id || el.name] = el.value; });
                return snap;
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
