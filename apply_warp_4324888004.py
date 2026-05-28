"""
LIVE Playwright Application Script
Company  : Warp
Role     : Software Engineer
Job ID   : 4324888004
Portal   : Greenhouse
URL      : https://job-boards.greenhouse.io/warp/jobs/4324888004
Date     : 2026-05-28
Mode     : LIVE — form is fully filled and the final submit button IS clicked.

Dry-run findings (fields actually present on this form):
  - first_name, last_name, email, phone, resume file-input, work-auth radio
  - Submit button text confirmed as "Submit application"
  - NOT present: linkedin, github, website, cover-letter slot, country select,
                 salary input, why-Warp textarea, EEO selects

Profile Mapping (AI/Agent role — Warp is an agentic terminal product):
  - Primary project  : Voxtant / Pantheon — LLM/Agent swarm architecture
  - Secondary project: Helios AI (autonomous CNN tracking, TensorFlow)
  - Koombea bullet   : API Focus — React/TypeScript/Node.js, GraphQL
  - JMG bullet       : Spring Boot/AWS Focus — microservices, REST APIs
  - Resume upload    : /workspaces/auto-applier/job-data/resume.pdf
  - Cover letter     : not present on this form
  - Work auth        : Yes / Eligible (US)
"""

import asyncio
import json
import os
from datetime import date
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

# ── Config ─────────────────────────────────────────────────────────────────────
JOB_URL     = "https://job-boards.greenhouse.io/warp/jobs/4324888004"
RESUME_PATH = Path("/workspaces/auto-applier/job-data/resume.pdf")
APPLIED_LOG = Path("/workspaces/auto-applier/job-data/applied_jobs.json")
PROCESSED   = Path("/workspaces/auto-applier/job-data/processed")
DOMAIN      = "job-boards.greenhouse.io"

APPLICANT = {
    "first_name": "Gabriel",
    "last_name":  "Suarez",
    "email":      "gabrielsc05131@gmail.com",
    "phone":      "305-746-1592",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[apply_warp_4324888004] {msg}")


async def safe_fill(page, selector: str, value: str, label: str = "") -> bool:
    """Fill a field if it exists; return True on success."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5_000)
        await locator.fill(value)
        log(f"  ✔  Filled '{label or selector}' → {value!r}")
        return True
    except PWTimeoutError:
        log(f"  –  Field not found / not visible: '{label or selector}'")
        return False


async def safe_upload(page, selector: str, file_path: Path, label: str = "") -> bool:
    """Attach a file to a file-input; return True on success."""
    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="attached", timeout=6_000)
        await locator.set_input_files(str(file_path))
        log(f"  ✔  Uploaded '{label or selector}' → {file_path.name}")
        return True
    except PWTimeoutError:
        log(f"  –  File input not found: '{label or selector}'")
        return False


# ── Main application flow ──────────────────────────────────────────────────────

async def run():
    assert RESUME_PATH.exists(), f"Resume PDF not found at {RESUME_PATH}"
    PROCESSED.mkdir(parents=True, exist_ok=True)

    PRE_SS  = PROCESSED / f"pre_submit_{DOMAIN}.png"
    POST_SS = PROCESSED / f"post_submit_{DOMAIN}.png"

    log("═══════════════════════════════════════════════════")
    log("  LIVE MODE — Warp / Software Engineer application")
    log(f"  URL    : {JOB_URL}")
    log(f"  Resume : {RESUME_PATH}")
    log("═══════════════════════════════════════════════════")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            accept_downloads=False,
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        page.set_default_timeout(15_000)

        # ── Step 1: Navigate to the job listing ───────────────────────────────
        log("Step 1 — Navigating to job listing …")
        await page.goto(JOB_URL, wait_until="domcontentloaded", timeout=30_000)
        log(f"         Page title: {await page.title()}")

        # ── Step 2: Click "Apply for this job" if present ─────────────────────
        log("Step 2 — Looking for 'Apply for this job' button …")
        try:
            apply_btn = page.get_by_role("link", name="Apply for this job")
            await apply_btn.first.wait_for(state="visible", timeout=6_000)
            log("         Clicking 'Apply for this job' …")
            await apply_btn.first.click()
            await page.wait_for_load_state("domcontentloaded", timeout=15_000)
        except PWTimeoutError:
            log("         Button not found — current page IS the form.")

        log(f"         Form page title: {await page.title()}")

        # ── Step 3: Identity fields ───────────────────────────────────────────
        log("Step 3 — Filling identity fields …")
        await safe_fill(page, "input#first_name",  APPLICANT["first_name"], "First name")
        await safe_fill(page, "input#last_name",   APPLICANT["last_name"],  "Last name")
        await safe_fill(page, "input#email",       APPLICANT["email"],      "Email")
        await safe_fill(page, "input#phone",       APPLICANT["phone"],      "Phone")

        # Greenhouse alternate name attributes
        for field, value, label in [
            ("job_application[first_name]", APPLICANT["first_name"], "First name (alt)"),
            ("job_application[last_name]",  APPLICANT["last_name"],  "Last name (alt)"),
            ("job_application[email]",      APPLICANT["email"],      "Email (alt)"),
            ("job_application[phone]",      APPLICANT["phone"],      "Phone (alt)"),
        ]:
            await safe_fill(page, f"input[name='{field}']", value, label)

        # ── Step 4: Resume upload ─────────────────────────────────────────────
        log("Step 4 — Uploading resume PDF …")
        uploaded = False
        for selector in [
            "input[type='file']",
            "input#resume",
            "input[name='job_application[resume]']",
            "input[accept*='pdf']",
        ]:
            if await safe_upload(page, selector, RESUME_PATH, "Resume PDF"):
                uploaded = True
                break
        if not uploaded:
            log("  ⚠  No resume file-input found — proceeding anyway.")

        # ── Step 5: Work-authorization radio ──────────────────────────────────
        log("Step 5 — Setting work-authorization …")
        work_auth_set = False
        for selector in [
            "input[type='radio'][value='Yes']",
            "input[type='radio'][value='yes']",
            "input[type='radio'][value='1']",
            "input[type='radio'][value='true']",
        ]:
            try:
                radio = page.locator(selector).first
                await radio.wait_for(state="visible", timeout=3_000)
                await radio.check()
                log(f"  ✔  Checked work-auth radio: {selector}")
                work_auth_set = True
                break
            except PWTimeoutError:
                pass
        if not work_auth_set:
            log("  –  Work-auth radio not found (may not be on this form).")

        # ── Step 6: Optional fields (safe — skip silently if absent) ──────────
        log("Step 6 — Optional link / salary / textarea fields …")
        await safe_fill(page, "input#job_application_linkedin_profile_url",
                        "https://www.linkedin.com/in/gabrielsuarezz", "LinkedIn")
        await safe_fill(page, "input[name*='linkedin']",
                        "https://www.linkedin.com/in/gabrielsuarezz", "LinkedIn (alt)")
        await safe_fill(page, "input[name*='website']",
                        "https://gabrielsuarez.dev", "Website")
        await safe_fill(page, "input[name*='github']",
                        "https://github.com/gabrielsuarezz", "GitHub")
        for sel in ["input[name*='salary']", "input[id*='salary']"]:
            await safe_fill(page, sel, "90000", "Salary")

        # EEO / voluntary self-ID — prefer "Prefer not to answer"
        log("Step 7 — Voluntary self-ID fields …")
        for sel in [
            "select[name*='gender']", "select[name*='race']",
            "select[name*='veteran']", "select[name*='disability']",
        ]:
            for pref in ["Prefer not to say", "Decline to self identify",
                         "I don't wish to answer", "prefer_not_to_say"]:
                try:
                    elem = page.locator(sel).first
                    await elem.wait_for(state="visible", timeout=2_000)
                    await elem.select_option(label=pref)
                    log(f"  ✔  EEO '{sel}' → '{pref}'")
                    break
                except Exception:
                    pass

        # ── Step 8: Pre-submit screenshot ─────────────────────────────────────
        log("Step 8 — Taking PRE-SUBMIT screenshot …")
        await page.screenshot(path=str(PRE_SS), full_page=True)
        log(f"  ✔  Saved: {PRE_SS}")

        # ── Step 9: Locate and click Submit ───────────────────────────────────
        log("Step 9 — Locating submit button …")
        submit_btn = None

        # Try confirmed text first (from dry-run), then fallbacks
        for btn_name in ["Submit application", "Submit Application", "Apply"]:
            try:
                candidate = page.get_by_role("button", name=btn_name)
                await candidate.first.wait_for(state="visible", timeout=5_000)
                submit_btn = candidate.first
                log(f"  ✔  Found submit button: '{btn_name}'")
                break
            except PWTimeoutError:
                pass

        if submit_btn is None:
            # Broader fallback
            try:
                submit_btn = page.locator("input[type='submit'], button[type='submit']").first
                await submit_btn.wait_for(state="visible", timeout=5_000)
                log("  ✔  Found submit via type=submit fallback")
            except PWTimeoutError:
                log("  ✗  Submit button NOT FOUND — aborting.")
                await browser.close()
                return

        log("  → CLICKING SUBMIT NOW …")
        await submit_btn.click()

        # ── Step 10: Wait 5 s then post-submit screenshot ─────────────────────
        log("Step 10 — Waiting 5 s for post-submit page to load …")
        await asyncio.sleep(5)
        log(f"          Post-submit page title: {await page.title()}")
        await page.screenshot(path=str(POST_SS), full_page=True)
        log(f"  ✔  Saved: {POST_SS}")

        await browser.close()

    # ── Step 11: Update applied_jobs.json ─────────────────────────────────────
    log("Step 11 — Appending metadata to applied_jobs.json …")
    new_record = {
        "company":          "Warp",
        "role":             "Software Engineer",
        "job_id":           "4324888004",
        "url":              JOB_URL,
        "date_applied":     str(date.today()),
        "dry_run":          False,
        "resume_used":      str(RESUME_PATH),
        "script":           "apply_warp_4324888004.py",
        "execution_status": "submitted_live",
        "screenshots": {
            "pre_submit":  str(PRE_SS),
            "post_submit": str(POST_SS),
        },
        "profile_mapping": {
            "role_type":           "AI / Agent Engineering (Agentic Dev Tools)",
            "koombea_bullet":      "API Focus — React/TypeScript/Node.js, GraphQL, 20% load-time reduction",
            "jmg_bullet":          "Spring Boot/AWS Focus — microservices, concurrent REST APIs",
            "primary_project":     (
                "Voxtant / Pantheon — LLM/Agent swarm architecture, multi-agent "
                "coordination, production LLM integrations, structured output "
                "parsing, streaming (1st of 80+ at PlutoHacks 2025)"
            ),
            "secondary_project":   "Helios AI (1st at Knight Hacks VIII, CNN-based autonomous tracking)",
            "tertiary_project":    "ViewGuard (real-time async security pipeline, YOLO + Gemini)",
            "pantheon_used":       True,
            "viewguard_used":      False,
            "bonus_skills":        ["Rust", "Go", "Linux"],
            "cover_letter":        "not present on this form",
            "salary_field":        "not present on this form",
            "us_work_auth_answer": "Yes",
            "visa_sponsorship":    "No",
        },
    }

    existing: list = []
    if APPLIED_LOG.exists():
        try:
            existing = json.loads(APPLIED_LOG.read_text())
        except json.JSONDecodeError:
            existing = []

    existing.append(new_record)
    APPLIED_LOG.write_text(json.dumps(existing, indent=2))
    log(f"  ✔  Metadata appended to {APPLIED_LOG}")

    log("")
    log("═══════════════════════════════════════════════════")
    log("  APPLICATION COMPLETE — Warp / Software Engineer")
    log("═══════════════════════════════════════════════════")


if __name__ == "__main__":
    asyncio.run(run())
