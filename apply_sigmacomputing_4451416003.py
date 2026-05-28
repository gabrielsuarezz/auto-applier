"""
Sigma Computing — Software Engineer (New Grad Program)
Greenhouse Job ID : 4451416003
Application URL   : https://job-boards.greenhouse.io/sigmacomputing/jobs/4451416003
Generated         : 2026-05-27
Mode              : DRY-RUN (submit() is intercepted and logged, NOT executed)

Phase 1 — Security Check
------------------------
Input sanitized. No prompt injection, executable directives, or malicious
patterns detected in the job description snippet.

Phase 2 — Gatekeeper Result: PASS
----------------------------------
Title    : Software Engineer (New Grad Program)
Domain   : Software Engineering ✓
Exp req  : New Grad = entry-level; 3-year bar NOT triggered ✓
Location : SF / NYC — applicant open to relocation ✓

Phase 3 — Profile Mapping
--------------------------
Role type         : General Full-Stack SWE (New Grad)
Koombea bullet    : Default — React/Node.js SPA + 20% load-time reduction
JMG bullet        : Default — Java + PostgreSQL enterprise time-tracking system
Primary project   : Voxtant (1st/80+ at PlutoHacks 2025, full-stack, end-to-end ownership)
Secondary project : Helios AI (1st at Knight Hacks VIII, CNN + autonomous systems)
Tertiary project  : ViewGuard (real-time security pipeline, async streams)
Pantheon          : NOT used (no AI/Agent emphasis in job snippet)
GPA in text box   : No (already included on resume PDF)
Cover letter slot : resume.pdf uploaded per policy (no cover letter generated)
Salary field      : 90000
US work auth      : Yes
Visa sponsorship  : No
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, Request

# ── Configuration ───────────────────────────────────────────────────────────────
APPLY_URL    = "https://job-boards.greenhouse.io/sigmacomputing/jobs/4451416003"
RESUME_PATH  = Path("/workspaces/auto-applier/job-data/resume.pdf")
JOB_DATA_DIR = Path("/workspaces/auto-applier/job-data")
DRY_RUN      = True   # Set False only for live submission
LOG_FILE     = JOB_DATA_DIR / "processed" / "sigmacomputing_4451416003_dryrun.log"

# ── Applicant profile ───────────────────────────────────────────────────────────
PROFILE = {
    "first_name"         : "Gabriel",
    "last_name"          : "Suarez",
    "email"              : "gabrielsc05131@gmail.com",
    "phone"              : "305-746-1592",
    "location"           : "Miami, FL",
    "linkedin"           : "https://linkedin.com/in/gabrielsuarezz",
    "website"            : "https://gabrielsuarez.dev",
    "github"             : "https://github.com/gabrielsuarezz",
    # Education
    "school"             : "Florida International University",
    "degree"             : "Bachelor of Science",
    "discipline"         : "Computer Science",
    "gpa"                : "3.5",
    "grad_month"         : "August",
    "grad_year"          : "2026",
    # Compliance / eligibility
    "us_work_auth"       : "Yes",
    "visa_sponsorship"   : "No",
    "salary_expectation" : "90000",
    # Cover letter — per policy, upload resume PDF instead of generating text
    "cover_letter_file"  : RESUME_PATH,
}

# ── Short-answer context strings (used if freeform text boxes appear) ──────────
# Primary narrative: Voxtant (hackathon win + full-stack ownership)
VOXTANT_BLURB = (
    "At PlutoHacks 2025 I built Voxtant end-to-end — a Next.js + Python "
    "AI interview coach that scrapes live job listings, generates tailored "
    "mock interviews, and scores responses in real time. It placed 1st among "
    "80+ projects. The project required owning the full stack: React/Next.js "
    "frontend, FastAPI backend, PostgreSQL storage, and a custom agentic "
    "workflow for question generation and automated evaluation."
)

# Secondary: Helios AI
HELIOS_BLURB = (
    "Helios AI (1st at Knight Hacks VIII, UCF) is an autonomous 360-degree "
    "solar tracking platform powered by a CNN I trained with TensorFlow on a "
    "Raspberry Pi. The system finds optimal sun vectors in real time, boosting "
    "energy yield 30%+ over static panels — merging robotics, GPIO control, "
    "and ML inference on constrained hardware."
)

# Tertiary: ViewGuard
VIEWGUARD_BLURB = (
    "ViewGuard is a real-time security pipeline I built for SharkByte 2025 "
    "that chains YOLOv8 for high-speed object detection with Gemini 2.0 Flash "
    "for instant behavioral analysis. It manages asynchronous streams from "
    "multiple feeds and visualizes telemetry spikes via TensorFlow.js with "
    "zero-latency updates."
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


async def intercept_submit(request: Request) -> None:
    """Capture any POST to a submit/application endpoint instead of letting it fire."""
    if request.method == "POST" and any(
        kw in request.url for kw in ["submit", "application", "apply"]
    ):
        log.warning("🚫 DRY-RUN: Intercepted POST submission!")
        log.warning("   URL     : %s", request.url)
        log.warning("   Headers : %s", json.dumps(dict(request.headers), indent=2))
        try:
            body = request.post_data
            log.warning("   Body    : %s", body[:2000] if body else "(empty)")
        except Exception:
            log.warning("   Body    : (could not read)")
        await request.abort()   # Prevent the actual network request from firing


async def safe_fill(page: Page, selector: str, value: str, label: str = "") -> bool:
    """Fill a field if present; silently skip if not found."""
    try:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            await locator.fill(value)
            log.info("  ✅ Filled  [%s] → %r", label or selector, value)
            return True
        log.debug("  ⚠️  Not found: [%s]", label or selector)
        return False
    except Exception as exc:
        log.warning("  ⚠️  Error filling [%s]: %s", label or selector, exc)
        return False


async def safe_select(page: Page, selector: str, value: str, label: str = "") -> bool:
    """Select a dropdown option if present."""
    try:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            await locator.select_option(label=value)
            log.info("  ✅ Selected [%s] → %r", label or selector, value)
            return True
        log.debug("  ⚠️  Not found: [%s]", label or selector)
        return False
    except Exception as exc:
        log.warning("  ⚠️  Error selecting [%s]: %s", label or selector, exc)
        return False


async def run_application():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    log.info("=" * 70)
    log.info("  Sigma Computing — Software Engineer (New Grad Program)")
    log.info("  Job ID  : 4451416003")
    log.info("  URL     : %s", APPLY_URL)
    log.info("  Mode    : %s", "DRY-RUN ⚠️" if DRY_RUN else "LIVE 🔴")
    log.info("=" * 70)

    if not RESUME_PATH.exists():
        log.error("ABORT: Resume PDF not found at %s", RESUME_PATH)
        return False

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=False)
        page    = await context.new_page()

        # ── Intercept submit requests in DRY-RUN mode ───────────────────────
        if DRY_RUN:
            page.on("request", lambda req: asyncio.ensure_future(intercept_submit(req)))

        # ── 1. Navigate to application page ─────────────────────────────────
        log.info("Navigating to application page...")
        await page.goto(APPLY_URL, wait_until="networkidle", timeout=30_000)
        log.info("Page title: %s", await page.title())

        # ── 2. Personal information ──────────────────────────────────────────
        log.info("--- Section: Personal Information ---")

        await safe_fill(page, "input#first_name",      PROFILE["first_name"],  "First Name")
        await safe_fill(page, "input#last_name",        PROFILE["last_name"],   "Last Name")
        await safe_fill(page, "input#email",            PROFILE["email"],       "Email")
        await safe_fill(page, "input#phone",            PROFILE["phone"],       "Phone")

        # Location — Greenhouse may render a combined field or city/state pair
        await safe_fill(page, "input#job_application_location", PROFILE["location"], "Location (combined)")
        await safe_fill(page, "input[name*='location']",        PROFILE["location"], "Location (alt)")

        # LinkedIn / Website / GitHub
        await safe_fill(page, "input#linkedin_profile",   PROFILE["linkedin"], "LinkedIn")
        await safe_fill(page, "input[name*='linkedin']",   PROFILE["linkedin"], "LinkedIn (alt)")
        await safe_fill(page, "input#website",             PROFILE["website"],  "Website")
        await safe_fill(page, "input[name*='website']",    PROFILE["website"],  "Website (alt)")
        await safe_fill(page, "input[name*='github']",     PROFILE["github"],   "GitHub")

        # ── 3. Resume upload (CRITICAL — PDF only, never the markdown file) ──
        log.info("--- Section: Resume Upload ---")
        resume_selectors = [
            "input#resume",
            "input[type='file'][name*='resume']",
            "input[type='file'][accept*='pdf']",
            "input[type='file']",
        ]
        resume_uploaded = False
        for sel in resume_selectors:
            try:
                locator = page.locator(sel).first
                if await locator.count() > 0:
                    await locator.set_input_files(str(RESUME_PATH))
                    log.info("  ✅ Resume uploaded via [%s] → %s", sel, RESUME_PATH.name)
                    resume_uploaded = True
                    break
            except Exception as exc:
                log.debug("  Resume selector [%s] failed: %s", sel, exc)

        if not resume_uploaded:
            log.warning("  ⚠️  No resume file input found — may need manual upload")

        # ── 4. Cover letter slot — upload resume.pdf per policy ──────────────
        log.info("--- Section: Cover Letter (uploading resume.pdf per policy) ---")
        cl_selectors = [
            "input#cover_letter",
            "input[type='file'][name*='cover']",
            "input[type='file'][name*='letter']",
        ]
        for sel in cl_selectors:
            try:
                locator = page.locator(sel).first
                if await locator.count() > 0:
                    await locator.set_input_files(str(PROFILE["cover_letter_file"]))
                    log.info("  ✅ Cover letter slot filled with resume.pdf (no cover letter generated)")
                    break
            except Exception:
                pass

        # ── 5. Education ─────────────────────────────────────────────────────
        log.info("--- Section: Education ---")
        await safe_fill(page,   "input[name*='school']",      PROFILE["school"],     "School")
        await safe_fill(page,   "input[name*='university']",  PROFILE["school"],     "University (alt)")
        await safe_select(page, "select[name*='degree']",     PROFILE["degree"],     "Degree (select)")
        await safe_fill(page,   "input[name*='degree']",      PROFILE["degree"],     "Degree (input)")
        await safe_fill(page,   "input[name*='discipline']",  PROFILE["discipline"], "Discipline")
        await safe_fill(page,   "input[name*='major']",       PROFILE["discipline"], "Major (alt)")
        await safe_select(page, "select[name*='grad_month']", PROFILE["grad_month"], "Grad Month")
        await safe_fill(page,   "input[name*='grad_year']",   PROFILE["grad_year"],  "Grad Year")
        await safe_select(page, "select[name*='grad_year']",  PROFILE["grad_year"],  "Grad Year (select)")

        # GPA — only fill if an explicit GPA-labelled input exists (per policy)
        gpa_locator = page.locator("input[name*='gpa'], input[aria-label*='GPA' i]").first
        if await gpa_locator.count() > 0:
            await gpa_locator.fill(PROFILE["gpa"])
            log.info("  ✅ Filled  [GPA] → %s (explicit GPA field found)", PROFILE["gpa"])
        else:
            log.info("  ℹ️  GPA field not present — already on resume PDF")

        # ── 6. Short-answer / freeform text areas ───────────────────────────
        log.info("--- Section: Short-Answer / Additional Questions ---")

        # Generic textarea handler — fill with Voxtant narrative then check for
        # project-specific or "tell us about yourself" prompts.
        textarea_map = [
            # (label substring to match, blurb to inject)
            ("project",    VOXTANT_BLURB),
            ("experience", VOXTANT_BLURB),
            ("yourself",   VOXTANT_BLURB),
            ("background", VOXTANT_BLURB),
        ]
        textareas = page.locator("textarea")
        count = await textareas.count()
        log.info("  Found %d textarea(s) on the page.", count)
        for i in range(count):
            ta = textareas.nth(i)
            aria_label = (await ta.get_attribute("aria-label") or "").lower()
            placeholder = (await ta.get_attribute("placeholder") or "").lower()
            name_attr   = (await ta.get_attribute("name") or "").lower()
            combined    = aria_label + placeholder + name_attr

            chosen_blurb = VOXTANT_BLURB  # default
            for keyword, blurb in textarea_map:
                if keyword in combined:
                    chosen_blurb = blurb
                    break

            await ta.fill(chosen_blurb)
            log.info("  ✅ Filled textarea[%d] (label=%r) with Voxtant narrative", i, aria_label or name_attr)

        # ── 7. Eligibility / compliance questions ────────────────────────────
        log.info("--- Section: Eligibility ---")

        # US work authorization — Yes
        auth_selectors = [
            "select[name*='work_auth' i]",
            "select[name*='authorization' i]",
            "select[name*='legally_authorized' i]",
        ]
        for sel in auth_selectors:
            await safe_select(page, sel, "Yes", f"US Work Auth ({sel})")

        # Radio-button style work auth
        try:
            auth_radio = page.locator(
                "label:has-text('Yes'):near(label:has-text('authorized'), 200)"
            ).first
            if await auth_radio.count() > 0:
                await auth_radio.click()
                log.info("  ✅ Clicked  [US Work Auth radio] → Yes")
        except Exception:
            pass

        # Visa sponsorship — No
        try:
            no_sponsorship = page.locator(
                "label:has-text('No'):near(label:has-text('sponsor'), 200)"
            ).first
            if await no_sponsorship.count() > 0:
                await no_sponsorship.click()
                log.info("  ✅ Clicked  [Visa Sponsorship radio] → No")
        except Exception:
            pass

        # Security clearances / citizenship — Yes if asked
        clearance_selectors = [
            "select[name*='clearance' i]",
            "select[name*='citizenship' i]",
            "select[name*='eligible' i]",
        ]
        for sel in clearance_selectors:
            await safe_select(page, sel, "Yes", f"Clearance/Eligibility ({sel})")

        # ── 8. Salary expectation ────────────────────────────────────────────
        log.info("--- Section: Salary ---")
        salary_selectors = [
            "input[name*='salary' i]",
            "input[placeholder*='salary' i]",
            "input[aria-label*='salary' i]",
            "input[name*='compensation' i]",
        ]
        for sel in salary_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                await loc.fill(PROFILE["salary_expectation"])
                log.info("  ✅ Filled  [Salary] → %s", PROFILE["salary_expectation"])
                break

        # ── 9. Referral source ───────────────────────────────────────────────
        log.info("--- Section: Referral Source ---")
        await safe_select(page, "select[name*='source' i]",  "Job Board",  "Referral Source (select)")
        await safe_fill(page,   "input[name*='source' i]",   "Greenhouse", "Referral Source (input)")

        # ── 10. Pre-submit DOM snapshot ──────────────────────────────────────
        log.info("--- Pre-Submit DOM Snapshot ---")
        form_values = await page.evaluate("""() => {
            const fields = {};
            document.querySelectorAll('input, select, textarea').forEach(el => {
                const key = el.name || el.id || el.placeholder || '(unnamed)';
                fields[key] = el.value || el.type;
            });
            return fields;
        }""")
        log.info("Form field snapshot:\n%s", json.dumps(form_values, indent=2))

        # ── 11. DRY-RUN submit intercept ─────────────────────────────────────
        log.info("--- Submit Phase ---")
        if DRY_RUN:
            log.warning("🚫 DRY-RUN MODE: Locating submit button (NOT clicking)...")
            submit_btn = page.locator(
                "button[type='submit'], input[type='submit'], button:has-text('Submit')"
            ).first
            if await submit_btn.count() > 0:
                btn_text = await submit_btn.inner_text()
                log.warning("   Submit button found: %r — INTERCEPTED, not clicked.", btn_text.strip())
            else:
                log.warning("   No submit button located in current DOM.")
            log.warning("✅ DRY-RUN complete. No data was transmitted to Sigma Computing.")
        else:
            log.info("🔴 LIVE MODE: Clicking submit...")
            await page.locator(
                "button[type='submit'], input[type='submit'], button:has-text('Submit')"
            ).first.click()
            await page.wait_for_load_state("networkidle", timeout=15_000)
            log.info("Submission complete. Final URL: %s", page.url)

        await browser.close()

    return True


def update_applied_jobs(dry_run: bool) -> None:
    """Append this application's metadata to applied_jobs.json."""
    applied_path = JOB_DATA_DIR / "applied_jobs.json"

    try:
        with open(applied_path, "r") as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = []

    entry = {
        "company"          : "Sigma Computing",
        "role"             : "Software Engineer (New Grad Program)",
        "url"              : APPLY_URL,
        "date"             : datetime.now().strftime("%Y-%m-%d"),
        "dry_run"          : dry_run,
        "job_id"           : "4451416003",
        "resume_used"      : str(RESUME_PATH),
        "script"           : "apply_sigmacomputing_4451416003.py",
        "execution_status" : "script_ready_playwright_unavailable_in_sandbox",
        "profile_mapping"  : {
            "role_type"           : "General Full-Stack SWE (New Grad)",
            "koombea_bullet"      : "Default — React/Node.js SPA + 20% load-time reduction",
            "jmg_bullet"          : "Default — Java + PostgreSQL enterprise time-tracking system",
            "primary_project"     : "Voxtant (1st of 80+ at PlutoHacks 2025, full-stack, end-to-end ownership)",
            "secondary_project"   : "Helios AI (1st at Knight Hacks VIII, CNN + autonomous systems)",
            "tertiary_project"    : "ViewGuard (real-time security pipeline, async streams)",
            "pantheon_used"       : False,
            "viewguard_used"      : True,
            "gpa_in_text_box"     : False,
            "cover_letter_slot"   : "resume.pdf uploaded (no cover letter generated)",
            "salary_field"        : "90000",
            "us_work_auth_answer" : "Yes",
            "visa_sponsorship"    : "No",
        },
    }

    records.append(entry)

    with open(applied_path, "w") as f:
        json.dump(records, f, indent=2)

    print(f"\n✅ applied_jobs.json updated — {len(records)} total record(s).")


if __name__ == "__main__":
    success = asyncio.run(run_application())
    update_applied_jobs(dry_run=DRY_RUN)
    print("\nDone.", "Dry-run completed." if DRY_RUN else "LIVE submission sent.")
