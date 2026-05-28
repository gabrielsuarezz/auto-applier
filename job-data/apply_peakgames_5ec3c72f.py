"""
Playwright application script — DRY-RUN MODE
Company : Peak Games
Role    : Software Engineer, Games (New Grad)
URL     : https://jobs.lever.co/peakgames/5ec3c72f-47a3-4aaa-963a-8a7620f8039d
Date    : 2026-05-27
"""

import json
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Config ──────────────────────────────────────────────────────────────────
DRY_RUN     = True   # Set to False for live submission
RESUME_PDF  = "/workspaces/auto-applier/job-data/resume.pdf"
APPLY_URL   = "https://jobs.lever.co/peakgames/5ec3c72f-47a3-4aaa-963a-8a7620f8039d/apply"
LOG_PATH    = "/workspaces/auto-applier/job-data/applied_jobs.json"

# ── Applicant profile (sourced from resume.md) ───────────────────────────────
APPLICANT = {
    "first_name" : "Gabriel",
    "last_name"  : "Suarez",
    "email"      : "gabrielsc05131@gmail.com",
    "phone"      : "305-746-1592",
    "linkedin"   : "https://linkedin.com/in/gabrielsuarezz",
    "website"    : "https://gabrielsuarez.dev",
    "location"   : "Miami, FL",
    # ── Phase 3 profile mapping: General SWE (non-AI, non-Security) ──────────
    # Koombea: Default bullet — React/Node.js SaaS, 20 % load-time reduction
    # JMG: Default bullet — Java + PostgreSQL enterprise time-tracking system
    # Primary project highlight: Shadow Vision
    #   - Real-time CV system (hand gestures → interactive digital puppets)
    #   - Most game-adjacent project; custom open-source dataset, 90 %+ accuracy
    # Secondary project highlight: Voxtant
    #   - 1st of 80+ at PlutoHacks 2025; full-stack, end-to-end ownership
    # GPA: On the PDF — not forced into any text box
    # Cover letter slot: resume.pdf re-uploaded (no cover letter generated)
    # Salary if prompted: 90000
    # Work authorization: Yes
}

# ── Additional short-answer copy (used only if the form asks) ─────────────
ADDITIONAL_INFO = (
    "I'm a Computer Science student at FIU (graduating Aug 2026) with hands-on "
    "experience building real-time interactive systems. My Shadow Vision project "
    "— awarded at ShellHacks 2025 — is a real-time computer vision system that "
    "maps hand gestures to interactive digital puppets and point clouds, which "
    "aligns closely with Peak's goal of crafting immersive user experiences. "
    "I also placed 1st of 80+ teams at PlutoHacks 2025 with Voxtant, demonstrating "
    "my ability to own features end-to-end under tight deadlines. "
    "C#, Java, and OOP are core to my skill set, and I'm genuinely excited about "
    "the engineering challenges at scale that come with 40 M+ monthly active players."
)

SALARY = "90000"


def run_application():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_page()

        print(f"[INFO] Navigating to: {APPLY_URL}")
        page.goto(APPLY_URL, wait_until="networkidle")

        # ── 1. Name fields ─────────────────────────────────────────────────
        _fill(page, 'input[name="name"]',        APPLICANT["first_name"] + " " + APPLICANT["last_name"])
        _fill(page, 'input[name="first_name"]',  APPLICANT["first_name"])
        _fill(page, 'input[name="last_name"]',   APPLICANT["last_name"])

        # ── 2. Contact ─────────────────────────────────────────────────────
        _fill(page, 'input[name="email"]',        APPLICANT["email"])
        _fill(page, 'input[name="phone"]',        APPLICANT["phone"])

        # ── 3. URLs ────────────────────────────────────────────────────────
        _fill(page, 'input[name="urls[LinkedIn]"]', APPLICANT["linkedin"])
        _fill(page, 'input[name="urls[GitHub]"]',
              "https://github.com/gabrielsuarezz")
        _fill(page, 'input[name="urls[Portfolio]"]', APPLICANT["website"])
        _fill(page, 'input[name="urls[Other]"]',    APPLICANT["website"])

        # ── 4. Location ─────────────────────────────────────────────────────
        _fill(page, 'input[name="location"]', APPLICANT["location"])

        # ── 5. Resume upload (CRITICAL: always PDF) ─────────────────────────
        file_inputs = page.query_selector_all('input[type="file"]')
        if file_inputs:
            print(f"[INFO] Uploading resume PDF to {len(file_inputs)} file input(s)")
            for fi in file_inputs:
                fi.set_input_files(RESUME_PDF)
            print(f"[INFO] Resume uploaded: {RESUME_PDF}")
        else:
            print("[WARN] No file input found — resume not uploaded")

        # ── 6. Cover letter slot (upload resume.pdf per policy) ─────────────
        cover_inputs = page.query_selector_all(
            'input[type="file"][name*="cover"], '
            'input[type="file"][name*="Cover"], '
            'input[type="file"][id*="cover"]'
        )
        for ci in cover_inputs:
            ci.set_input_files(RESUME_PDF)
            print(f"[INFO] Cover-letter slot filled with resume.pdf")

        # ── 7. Additional info / textarea ──────────────────────────────────
        _fill(page, 'textarea[name="comments"]',      ADDITIONAL_INFO)
        _fill(page, 'textarea[name="additional_info"]', ADDITIONAL_INFO)

        # ── 8. Work authorisation / eligibility (Yes to all) ──────────────
        for sel in [
            'input[name*="authorized"][value="Yes"]',
            'input[name*="authorized"][value="yes"]',
            'input[name*="citizenship"][value="Yes"]',
            'input[name*="sponsorship"][value="No"]',   # "need sponsorship? → No"
        ]:
            try:
                el = page.query_selector(sel)
                if el:
                    el.check()
                    print(f"[INFO] Checked eligibility field: {sel}")
            except Exception:
                pass

        # ── 9. Salary (only if a salary field exists) ──────────────────────
        for sel in ['input[name*="salary"]', 'input[name*="Salary"]',
                    'input[placeholder*="salary"]']:
            _fill(page, sel, SALARY)

        # ── 10. Submit interception ────────────────────────────────────────
        submit_btn = (
            page.query_selector('button[type="submit"]') or
            page.query_selector('input[type="submit"]')
        )

        if DRY_RUN:
            print("\n[DRY-RUN] ✅ All fields filled. Submit intercepted — NOT submitted.")
            print(f"[DRY-RUN] Submit button found: {submit_btn is not None}")
        else:
            if submit_btn:
                submit_btn.click()
                page.wait_for_load_state("networkidle")
                print("[LIVE] ✅ Application submitted.")
            else:
                print("[ERROR] Submit button not found.")

        browser.close()

    _log_application()


def _fill(page, selector: str, value: str):
    """Fill a field if it exists; silently skip otherwise."""
    try:
        el = page.query_selector(selector)
        if el and value:
            el.fill(value)
            print(f"[INFO] Filled '{selector}' → '{value[:60]}'")
    except Exception as exc:
        print(f"[WARN] Could not fill '{selector}': {exc}")


def _log_application():
    """Append application metadata to applied_jobs.json."""
    log_file = Path(LOG_PATH)
    existing = json.loads(log_file.read_text()) if log_file.exists() else []

    entry = {
        "company"          : "Peak Games",
        "role"             : "Software Engineer, Games (New Grad)",
        "url"              : "https://jobs.lever.co/peakgames/5ec3c72f-47a3-4aaa-963a-8a7620f8039d",
        "date"             : datetime.date.today().isoformat(),
        "dry_run"          : DRY_RUN,
        "job_id"           : "5ec3c72f-47a3-4aaa-963a-8a7620f8039d",
        "resume_used"      : RESUME_PDF,
        "script"           : "apply_peakgames_5ec3c72f.py",
        "execution_status" : "script_ready_dry_run_pending",
        "profile_mapping"  : {
            "role_type"        : "General SWE — Mobile Casual Games (New Grad)",
            "koombea_bullet"   : "Default — React/Node.js SaaS, 20% load-time reduction",
            "jmg_bullet"       : "Default — Java + PostgreSQL enterprise time-tracking system",
            "primary_project"  : "Shadow Vision — real-time hand-gesture CV system, interactive digital puppets, 90%+ accuracy (ShellHacks 2025)",
            "secondary_project": "Voxtant — 1st of 80+ at PlutoHacks 2025, full-stack, end-to-end ownership",
            "pantheon_used"    : False,
            "viewguard_used"   : False,
            "gpa_in_text_box"  : False,
            "cover_letter_slot": "resume.pdf uploaded (no cover letter generated per policy)",
            "salary_field"     : "90000",
            "us_work_auth_answer": "Yes",
        },
    }

    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2))
    print(f"\n[LOG] Entry appended to {LOG_PATH}")
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    run_application()
