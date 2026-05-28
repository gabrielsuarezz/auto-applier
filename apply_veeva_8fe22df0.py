"""
Veeva Systems — Associate Software Engineer (Engineering Development Program)
Job ID  : 8fe22df0-02b4-453d-919c-c8998cf913f6
URL     : https://jobs.lever.co/veeva/8fe22df0-02b4-453d-919c-c8998cf913f6/apply
Mode    : DRY-RUN  (submit() is intercepted and logged, NOT executed)
Resume  : /workspaces/auto-applier/job-data/resume.pdf
Generated: 2026-05-27
"""

import asyncio
import json
import os
from datetime import date
from playwright.async_api import async_playwright

# ── Config ────────────────────────────────────────────────────────────────────
DRY_RUN       = True
APPLY_URL     = "https://jobs.lever.co/veeva/8fe22df0-02b4-453d-919c-c8998cf913f6/apply"
RESUME_PATH   = "/workspaces/auto-applier/job-data/resume.pdf"
APPLIED_JSON  = "/workspaces/auto-applier/job-data/applied_jobs.json"

# ── Applicant data (sourced from resume.md) ───────────────────────────────────
APPLICANT = {
    "full_name"  : "Gabriel Suarez",
    "email"      : "gabrielsc05131@gmail.com",
    "phone"      : "305-746-1592",
    "location"   : "Miami, FL",
    "linkedin"   : "https://linkedin.com/in/gabrielsuarezz",
    "github"     : "https://github.com/gabrielsuarezz",
    "website"    : "https://gabrielsuarez.dev",
    "university" : "Florida International University",
    "degree"     : "Bachelor of Science in Computer Science",
    "grad_year"  : "2026",
    # GPA: included on PDF — not forced into short-answer boxes
    # Work auth: auto-answered "Yes" per policy
    "work_auth"  : "Yes",
    # Salary (if forced): per policy
    "salary"     : "90000",
}


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=False)
        page    = await context.new_page()

        print(f"[NAV]  Navigating to {APPLY_URL}")
        await page.goto(APPLY_URL, wait_until="domcontentloaded", timeout=60_000)
        # Give JS-heavy SPA extra time to hydrate
        await page.wait_for_timeout(4_000)
        print(f"[OK]   Page loaded: {await page.title()}")

        # ── 1. Full Name ──────────────────────────────────────────────────────
        name_sel = "input[name='name'], input[placeholder*='name' i], #name"
        if await page.locator(name_sel).count():
            await page.fill(name_sel, APPLICANT["full_name"])
            print(f"[FILL] Full name → {APPLICANT['full_name']}")

        # ── 2. Email ──────────────────────────────────────────────────────────
        email_sel = "input[name='email'], input[type='email'], #email"
        if await page.locator(email_sel).count():
            await page.fill(email_sel, APPLICANT["email"])
            print(f"[FILL] Email → {APPLICANT['email']}")

        # ── 3. Phone ──────────────────────────────────────────────────────────
        phone_sel = "input[name='phone'], input[type='tel'], #phone"
        if await page.locator(phone_sel).count():
            await page.fill(phone_sel, APPLICANT["phone"])
            print(f"[FILL] Phone → {APPLICANT['phone']}")

        # ── 4. Location / Current City ────────────────────────────────────────
        loc_sel = "input[name='location'], input[placeholder*='location' i], input[placeholder*='city' i]"
        if await page.locator(loc_sel).count():
            await page.fill(loc_sel, APPLICANT["location"])
            print(f"[FILL] Location → {APPLICANT['location']}")

        # ── 5. LinkedIn ───────────────────────────────────────────────────────
        li_sel = "input[name='urls[LinkedIn]'], input[placeholder*='linkedin' i], input[name*='linkedin' i]"
        if await page.locator(li_sel).count():
            await page.fill(li_sel, APPLICANT["linkedin"])
            print(f"[FILL] LinkedIn → {APPLICANT['linkedin']}")

        # ── 6. GitHub / Portfolio ─────────────────────────────────────────────
        gh_sel = "input[name='urls[GitHub]'], input[placeholder*='github' i], input[name*='github' i]"
        if await page.locator(gh_sel).count():
            await page.fill(gh_sel, APPLICANT["github"])
            print(f"[FILL] GitHub → {APPLICANT['github']}")

        portfolio_sel = "input[name='urls[Portfolio]'], input[placeholder*='portfolio' i], input[name*='website' i]"
        if await page.locator(portfolio_sel).count():
            await page.fill(portfolio_sel, APPLICANT["website"])
            print(f"[FILL] Portfolio → {APPLICANT['website']}")

        # ── 7. Resume upload (CRITICAL: PDF only) ────────────────────────────
        resume_sel = "input[type='file'][name*='resume' i], input[type='file'][accept*='pdf' i], input[type='file']"
        resume_inputs = await page.locator(resume_sel).all()
        if resume_inputs:
            assert os.path.exists(RESUME_PATH), f"FATAL: resume not found at {RESUME_PATH}"
            await resume_inputs[0].set_input_files(RESUME_PATH)
            print(f"[FILE] Resume uploaded → {RESUME_PATH}")

            # Cover letter slot: re-upload resume.pdf (no cover letter generated per policy)
            if len(resume_inputs) > 1:
                await resume_inputs[1].set_input_files(RESUME_PATH)
                print(f"[FILE] Cover letter slot → resume.pdf re-uploaded (policy: no cover letter)")

        # ── 8. Work authorization ──────────────────────────────────────────────
        # Lever custom questions: find any radio labelled "Yes" near an
        # authorization question, or a select containing "authorized"
        try:
            # Strategy A: find a <select> whose nearest label mentions authorization
            for sel_el in await page.locator("select").all():
                parent_text = await sel_el.evaluate(
                    "el => el.closest('.application-question, .field, form')?.innerText || ''"
                )
                if any(kw in parent_text.lower() for kw in ("authorized", "work auth", "visa", "sponsorship")):
                    # Try to select "Yes" option
                    options = await sel_el.evaluate("el => [...el.options].map(o => o.label)")
                    yes_opt = next((o for o in options if "yes" in o.lower()), None)
                    if yes_opt:
                        await sel_el.select_option(label=yes_opt)
                        print(f"[SELECT] Work auth dropdown → {yes_opt}")

            # Strategy B: find radio inputs whose parent text mentions authorization
            for radio in await page.locator("input[type='radio']").all():
                parent_text = await radio.evaluate(
                    "el => el.closest('.application-question, fieldset, .field')?.innerText || ''"
                )
                radio_value = (await radio.get_attribute("value") or "").lower()
                if any(kw in parent_text.lower() for kw in ("authorized", "work auth", "visa")):
                    if radio_value in ("yes", "true", "1"):
                        await radio.click()
                        print(f"[SELECT] Work auth radio → Yes")
                        break
        except Exception as e:
            print(f"[WARN] Work auth selection skipped: {e}")

        # ── 9. Salary field (if forced) ───────────────────────────────────────
        salary_sel = "input[name*='salary' i], input[placeholder*='salary' i], input[placeholder*='compensation' i]"
        if await page.locator(salary_sel).count():
            await page.fill(salary_sel, APPLICANT["salary"])
            print(f"[FILL] Salary → {APPLICANT['salary']}")

        # ── 10. DRY-RUN: intercept submit ─────────────────────────────────────
        submit_sel = "button[type='submit'], input[type='submit'], button:has-text('Submit')"
        submit_btn = page.locator(submit_sel)
        submit_count = await submit_btn.count()

        if DRY_RUN:
            print("\n" + "="*60)
            print("  DRY-RUN MODE: Submit intercepted — NOT submitted.")
            if submit_count:
                btn_text = await submit_btn.first.inner_text()
                print(f"  Submit button found: \"{btn_text.strip()}\"")
            print("  All form fields populated and ready.")
            print("="*60 + "\n")
        else:
            if submit_count:
                await submit_btn.first.click()
                await page.wait_for_load_state("networkidle", timeout=15_000)
                print("[SUBMIT] Application submitted successfully.")
            else:
                print("[WARN] No submit button found — check DOM selectors.")

        await browser.close()

    # ── Append to applied_jobs.json ───────────────────────────────────────────
    record = {
        "company"          : "Veeva Systems",
        "role"             : "Associate Software Engineer (Engineering Development Program)",
        "job_id"           : "8fe22df0-02b4-453d-919c-c8998cf913f6",
        "url"              : "https://jobs.lever.co/veeva/8fe22df0-02b4-453d-919c-c8998cf913f6",
        "date"             : str(date.today()),
        "dry_run"          : DRY_RUN,
        "resume_used"      : RESUME_PATH,
        "script"           : "apply_veeva_8fe22df0.py",
        "execution_status" : "dry_run_intercepted_submit_not_sent" if DRY_RUN else "submitted",
        "profile_mapping"  : {
            "role_type"         : "General SWE — New Grad EDP",
            "koombea_bullet"    : "Default — React/Node.js SaaS, 20% load-time reduction",
            "jmg_bullet"        : "Default — Java + PostgreSQL, 99.9% uptime",
            "primary_project"   : "Voxtant (1st of 80+ at PlutoHacks 2025, full-stack AI interview coach)",
            "secondary_project" : "Helios AI (1st at Knight Hacks VIII, CNN solar tracking)",
            "tertiary_project"  : "ViewGuard (real-time YOLO + Gemini security pipeline)",
            "pantheon_used"     : False,
            "viewguard_used"    : True,
            "gpa_in_text_box"   : False,
            "cover_letter_slot" : "resume.pdf re-uploaded (no cover letter generated per policy)",
            "salary_field"      : "90000",
            "us_work_auth"      : "Yes",
            "visa_sponsorship"  : "No (role offers no sponsorship)",
        },
    }

    existing = []
    if os.path.exists(APPLIED_JSON):
        with open(APPLIED_JSON, "r") as f:
            existing = json.load(f)

    existing.append(record)

    with open(APPLIED_JSON, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"[LOG] Application record appended to {APPLIED_JSON}")


if __name__ == "__main__":
    asyncio.run(run())
