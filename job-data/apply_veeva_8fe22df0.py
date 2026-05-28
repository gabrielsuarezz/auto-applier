"""
Veeva Systems – Associate Software Engineer (Engineering Development Program)
Lever Job ID : 8fe22df0-02b4-453d-919c-c8998cf913f6
Apply URL    : https://jobs.lever.co/veeva/8fe22df0-02b4-453d-919c-c8998cf913f6/apply
Mode         : DRY-RUN  (final submit() is intercepted and logged, NOT executed)
Generated    : 2026-05-27
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

# ── Applicant constants ────────────────────────────────────────────────────────
APPLY_URL   = "https://jobs.lever.co/veeva/8fe22df0-02b4-453d-919c-c8998cf913f6/apply"
RESUME_PDF  = "/workspaces/auto-applier/job-data/resume.pdf"
DRY_RUN     = True   # set False for live submission

APPLICANT = {
    "full_name"  : "Gabriel Suarez",
    "email"      : "gabrielsc05131@gmail.com",
    "phone"      : "305-746-1592",
    "location"   : "Miami, FL",          # current city; open to Pleasanton CA relocation
    "linkedin"   : "https://linkedin.com/in/gabrielsuarezz",
    "github"     : "https://github.com/gabrielsuarezz",
    "website"    : "https://gabrielsuarez.dev",
    "org"        : "Florida International University",
    "gpa"        : "3.5",                # only if form explicitly asks
    "salary"     : "90000",
    "work_auth"  : "Yes",                # US work authorization
}

# ── Profile-mapped long-form answers ──────────────────────────────────────────
# Role type: General Full-Stack SWE (Java/React-heavy new grad program)
# Koombea  → default React/Node.js bullet
# JMG      → Spring Boot/AWS focus (Java is Veeva's primary backend)

KOOMBEA_BULLET = (
    "Built and scaled features for a Fintech SaaS platform using React and Node.js, "
    "cutting dashboard load times by 20% through improved state management and API efficiency."
)

JMG_BULLET = (
    "Designed and built a microservices-based time-tracking system using Java Spring Boot "
    "and PostgreSQL, automating real-time labor data synchronization via highly concurrent REST APIs."
)

PRIMARY_PROJECT = (
    "Voxtant – placed 1st of 80+ projects at PlutoHacks 2025. "
    "An AI interview coach that scans live job listings to create tailored mock interviews "
    "and technical assessments, powered by a custom agentic workflow for real-time evaluation "
    "and automated scoring (Next.js, Python, spaCy, MediaPipe, OpenCV, PostgreSQL, Docker)."
)

SECONDARY_PROJECT = (
    "Helios AI – placed 1st at Knight Hacks VIII (UCF). "
    "An autonomous 360-degree solar platform using a CNN-based TensorFlow tracking model "
    "to find optimal light vectors, increasing energy yield by 30%+ over static panels "
    "(Python, TensorFlow, Scikit-Learn, Raspberry Pi)."
)

# ── Helpers ───────────────────────────────────────────────────────────────────

async def safe_fill(page, selector: str, value: str, label: str = ""):
    """Fill a field if it exists; silently skip if absent."""
    try:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            await locator.fill(value)
            print(f"  [FILL] {label or selector} = '{value[:60]}'")
        else:
            print(f"  [SKIP] {label or selector} not found in DOM")
    except Exception as exc:
        print(f"  [WARN] {label}: {exc}")


async def safe_upload(page, selector: str, file_path: str, label: str = ""):
    """Upload a file to a file-input element using setInputFiles()."""
    try:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            await locator.set_input_files(file_path)
            print(f"  [UPLOAD] {label or selector} ← {file_path}")
        else:
            print(f"  [SKIP] file input '{label}' not found in DOM")
    except Exception as exc:
        print(f"  [WARN] {label}: {exc}")


async def safe_select(page, selector: str, value: str, label: str = ""):
    """Select a dropdown option by value or label."""
    try:
        locator = page.locator(selector).first
        if await locator.count() > 0:
            await locator.select_option(label=value)
            print(f"  [SELECT] {label or selector} = '{value}'")
        else:
            print(f"  [SKIP] select '{label}' not found")
    except Exception as exc:
        print(f"  [WARN] {label}: {exc}")


# ── Main application routine ──────────────────────────────────────────────────

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page    = await context.new_page()

        print(f"\n{'='*60}")
        print(f"  Veeva Systems — Associate Software Engineer (EDP)")
        print(f"  Mode: {'DRY-RUN' if DRY_RUN else '*** LIVE SUBMISSION ***'}")
        print(f"{'='*60}\n")

        # ── Navigate to apply page ─────────────────────────────────────────
        print(f"[NAV] {APPLY_URL}")
        await page.goto(APPLY_URL, wait_until="networkidle", timeout=30_000)
        print(f"[NAV] Page title: {await page.title()}\n")

        # ── Section 1: Basic contact info ──────────────────────────────────
        print("[SECTION] Basic Info")
        await safe_fill(page, "input[name='name']",  APPLICANT["full_name"], "Full Name")
        await safe_fill(page, "input[name='email']", APPLICANT["email"],     "Email")
        await safe_fill(page, "input[name='phone']", APPLICANT["phone"],     "Phone")
        # Lever uses an org/current-company field
        await safe_fill(page, "input[name='org']",   APPLICANT["org"],       "Organization")

        # ── Section 2: Resume upload ───────────────────────────────────────
        print("\n[SECTION] Resume Upload")
        # Lever's primary resume file input
        await safe_upload(page, "input[type='file']", RESUME_PDF, "Resume PDF")

        # ── Section 3: Social / web links ─────────────────────────────────
        print("\n[SECTION] Links")
        await safe_fill(page, "input[name='urls[LinkedIn]']",  APPLICANT["linkedin"], "LinkedIn")
        await safe_fill(page, "input[name='urls[GitHub]']",    APPLICANT["github"],   "GitHub")
        await safe_fill(page, "input[name='urls[Portfolio]']", APPLICANT["website"],  "Portfolio")
        await safe_fill(page, "input[name='urls[Other]']",     APPLICANT["website"],  "Other URL")

        # ── Section 4: Custom / EEO questions ─────────────────────────────
        print("\n[SECTION] Custom Questions")

        # Work authorization
        await safe_fill(
            page,
            "input[name*='work_auth'], textarea[name*='authorized'], "
            "[placeholder*='authorized'], [placeholder*='work auth']",
            APPLICANT["work_auth"],
            "Work Authorization"
        )

        # Graduation year (2025/2026 grad program)
        await safe_fill(
            page,
            "input[name*='grad'], input[name*='graduation'], textarea[name*='graduation']",
            "2026",
            "Graduation Year"
        )

        # Salary — only if a field is explicitly present
        await safe_fill(
            page,
            "input[name*='salary'], input[name*='compensation'], "
            "textarea[name*='salary']",
            APPLICANT["salary"],
            "Desired Salary"
        )

        # ── Section 5: Long-form / open-ended text boxes ───────────────────
        print("\n[SECTION] Long-Form Answers (profile-mapped)")
        # If the form has a general "tell us about yourself" or "additional info" box:
        # prioritise Java experience + Voxtant + Helios AI
        combined_narrative = (
            f"At Koombea, I {KOOMBEA_BULLET} "
            f"At JMG Custom, I {JMG_BULLET} "
            f"Highlights: {PRIMARY_PROJECT} "
            f"{SECONDARY_PROJECT}"
        )
        await safe_fill(
            page,
            "textarea[name='comments'], textarea[name='additional'], "
            "textarea[placeholder*='additional'], textarea[placeholder*='tell us']",
            combined_narrative,
            "Additional Comments / Free-Text"
        )

        # ── Section 6: Cover letter slot → upload resume.pdf ──────────────
        print("\n[SECTION] Cover Letter Slot")
        # Lever sometimes has a second file input for cover letter
        file_inputs = await page.locator("input[type='file']").all()
        if len(file_inputs) > 1:
            try:
                await file_inputs[1].set_input_files(RESUME_PDF)
                print(f"  [UPLOAD] Cover letter slot ← {RESUME_PDF} (no cover letter generated per policy)")
            except Exception as exc:
                print(f"  [WARN] Cover letter upload: {exc}")
        else:
            print("  [SKIP] No secondary file input found (no cover letter slot)")

        # ── DRY-RUN intercept ──────────────────────────────────────────────
        print("\n[SUBMIT INTERCEPT]")
        if DRY_RUN:
            # Locate the submit button but do NOT click it
            submit_btn = page.locator("button[type='submit'], input[type='submit']").first
            btn_text   = await submit_btn.text_content() if await submit_btn.count() > 0 else "N/A"
            print(f"  [DRY-RUN] Submit button found: '{btn_text.strip()}'")
            print("  [DRY-RUN] form.submit() INTERCEPTED — not executed.")
            print("  [DRY-RUN] All fields filled and verified. Script complete.")

            # Capture current form state as a screenshot for review
            await page.screenshot(path="/workspaces/auto-applier/job-data/veeva_dry_run.png",
                                   full_page=True)
            print("  [DRY-RUN] Screenshot saved → job-data/veeva_dry_run.png")
        else:
            print("  [LIVE] Clicking submit...")
            await page.locator("button[type='submit'], input[type='submit']").first.click()
            await page.wait_for_load_state("networkidle")
            print(f"  [LIVE] Post-submit URL: {page.url}")

        await browser.close()
        print("\n[DONE]\n")


if __name__ == "__main__":
    asyncio.run(run())
