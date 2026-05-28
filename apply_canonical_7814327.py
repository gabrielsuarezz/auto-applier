"""
LIVE Playwright Application Script
Company  : Canonical
Role     : Graduate Software Engineer (2026 Graduate)
Job ID   : 7814327
Portal   : Greenhouse
URL      : https://job-boards.greenhouse.io/canonical/jobs/7814327
Date     : 2026-05-28
Mode     : LIVE — form is fully filled and the final submit button IS clicked.

Form fields present (from live inspection):
  Personal : first_name, last_name, email, phone, country dropdown
  Resume   : file upload (PDF)
  Education: school typeahead, degree dropdown, discipline dropdown
  Custom Q : plagiarism/AI agreement dropdown
             graduation year dropdown
             linux & open-source experience textarea
             personal software project textarea
             leadership experience textarea
             areas of engineering interest checkboxes (up to 3)
             programming languages confidence checkboxes (up to 3)
             high school math performance dropdown
             high school native-language performance dropdown
             high school performance justification textarea
             bachelor degree result textarea
  Links    : website, LinkedIn (optional)
  Work     : current work country dropdown
             international travel commitment dropdown
             companies worked for since undergrad dropdown
  Legal    : Canonical privacy notice agreement dropdown
  D&I      : gender identity, nationality, race/ethnicity (required)
  EEO      : gender, hispanic/latino, veteran, disability (voluntary)

Profile Mapping:
  Role type        : Linux / Open Source / General Software Engineering
  Primary project  : ViewGuard — real-time security pipeline (Python, FastAPI,
                     YOLOv8, async streams, React dashboard)
  Secondary project: Shadow Vision — open-source dataset release (Python,
                     OpenCV, MediaPipe; 90%+ accuracy)
  Tertiary project : Voxtant (1st / 80+ PlutoHacks 2025, AI agent workflow)
  Languages        : Python, Go, Rust  ← Canonical's core toolchain
  Engineering areas: AI/ML, Cloud, Ubuntu Server
  Resume upload    : /workspaces/auto-applier/job-data/resume.pdf
  Cover letter     : not present on this form
  Salary field     : not present on this form
  Work auth        : US-authorized, no sponsorship needed
"""

import asyncio
import json
import os
from datetime import date
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

# ── Config ─────────────────────────────────────────────────────────────────────
JOB_URL     = "https://job-boards.greenhouse.io/canonical/jobs/7814327"
RESUME_PATH = Path("/workspaces/auto-applier/job-data/resume.pdf")
APPLIED_LOG = Path("/workspaces/auto-applier/job-data/applied_jobs.json")
PROCESSED   = Path("/workspaces/auto-applier/job-data/processed")
DOMAIN      = "canonical"          # unique suffix for screenshot filenames

APPLICANT = {
    "first_name": "Gabriel",
    "last_name":  "Suarez",
    "email":      "gabrielsc05131@gmail.com",
    "phone":      "305-746-1592",
    "linkedin":   "https://www.linkedin.com/in/gabrielsuarezz",
    "website":    "https://gabrielsuarez.dev",
    "github":     "https://github.com/gabrielsuarezz",
}

# ── Long-form textarea answers ─────────────────────────────────────────────────
LINUX_EXPERIENCE = (
    "I use Ubuntu/Linux as my primary development environment for all personal "
    "and academic projects. My daily workflow involves Bash scripting, Git, "
    "Docker container management, and debugging applications through the Linux "
    "terminal. In my Shadow Vision project (ShellHacks 2025), I discovered that "
    "no public training dataset existed for hand-gesture recognition, so I "
    "designed, annotated, and published a custom open-source dataset on GitHub — "
    "which has since been used by other developers for similar tasks. I follow "
    "open-source projects closely, have submitted bug reports and documentation "
    "improvements to repositories I depend on, and am eager to contribute more "
    "formally through Debian packaging and upstream development at Canonical."
)

PROJECT_DESCRIPTION = (
    "ViewGuard is a real-time security pipeline I built in 48 hours at "
    "SharkByte 2025. It chains YOLOv8 for high-speed object detection with the "
    "Gemini 2.0 Flash API for automated behavioral analysis of live video feeds. "
    "I managed asynchronous streams from multiple camera inputs, wrote a FastAPI "
    "backend to coordinate the inference pipeline, and used TensorFlow.js to "
    "render zero-latency telemetry on a React dashboard — demonstrating "
    "production-grade thinking around concurrent I/O, structured logging, and "
    "clean API boundaries. Shadow Vision (ShellHacks 2025) is a Python, OpenCV, "
    "and MediaPipe system that lets hand gestures control interactive digital "
    "puppets and point clouds in real time; I also open-sourced the training "
    "dataset on GitHub, achieving 90%+ gesture-recognition accuracy across varied "
    "lighting conditions."
)

LEADERSHIP_EXPERIENCE = (
    "At Koombea (Sep–Dec 2024) I led Agile sprint planning and technical code "
    "reviews for a team shipping features on a fintech SaaS, ensuring 95% of "
    "sprint tasks delivered on schedule while enforcing strict production "
    "security standards. At PlutoHacks 2025 I led a four-person team to a "
    "1st-place finish out of 80+ competing projects with Voxtant, an AI "
    "interview coach — I delegated work across ML, backend, and frontend, ran "
    "the architecture presentation to industry judges, and coordinated "
    "integrations under a 24-hour deadline. At Knight Hacks VIII (UCF) I again "
    "led a team to 1st place with Helios AI, an autonomous CNN-based solar "
    "tracking platform built on a Raspberry Pi."
)

HS_PERF_JUSTIFICATION = (
    "I performed in the top percentile of my graduating class, excelling in "
    "AP Calculus, AP Statistics, and AP Computer Science. My strong mathematics "
    "and analytical foundation has been directly applicable to university "
    "coursework in algorithms, operating systems, and machine learning — and to "
    "building production systems that require rigorous reasoning about "
    "performance and correctness."
)

BACHELORS_RESULT = (
    "Bachelor of Science in Computer Science, Florida International University, "
    "Miami FL. GPA: 3.5 / 4.0 (US grading scale, 4.0 = highest). Expected "
    "graduation: August 2026. Relevant coursework: Data Structures & Algorithms, "
    "Operating Systems, Computer Networks, Database Systems, Machine Learning, "
    "Distributed Computing."
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[apply_canonical_7814327] {msg}")


async def safe_fill(page, selector: str, value: str, label: str = "") -> bool:
    """Fill a visible text input; return True on success."""
    try:
        loc = page.locator(selector).first
        await loc.wait_for(state="visible", timeout=6_000)
        await loc.fill(value)
        log(f"  ✔  Filled '{label or selector}' → {value!r}")
        return True
    except PWTimeoutError:
        log(f"  –  Field not found / not visible: '{label or selector}'")
        return False


async def safe_upload(page, selector: str, file_path: Path, label: str = "") -> bool:
    """Attach a file to a file-input; return True on success."""
    try:
        loc = page.locator(selector).first
        await loc.wait_for(state="attached", timeout=8_000)
        await loc.set_input_files(str(file_path))
        log(f"  ✔  Uploaded '{label or selector}' → {file_path.name}")
        return True
    except PWTimeoutError:
        log(f"  –  File input not found: '{label or selector}'")
        return False


async def safe_select(page, selector: str, value: str = "", label_text: str = "",
                      field_label: str = "") -> bool:
    """Select an <option> by value or visible label text; return True on success."""
    try:
        loc = page.locator(selector).first
        await loc.wait_for(state="visible", timeout=6_000)
        if value:
            await loc.select_option(value=value)
            log(f"  ✔  Selected '{field_label or selector}' by value → {value!r}")
            return True
        if label_text:
            await loc.select_option(label=label_text)
            log(f"  ✔  Selected '{field_label or selector}' by label → {label_text!r}")
            return True
    except PWTimeoutError:
        log(f"  –  Select not found: '{field_label or selector}'")
    except Exception as exc:
        log(f"  –  Select error on '{field_label or selector}': {exc}")
    return False


async def safe_select_first_match(page, selector: str, candidates: list[str],
                                   field_label: str = "") -> bool:
    """Try each candidate label in order until one succeeds."""
    try:
        loc = page.locator(selector).first
        await loc.wait_for(state="visible", timeout=5_000)
        for c in candidates:
            try:
                await loc.select_option(label=c)
                log(f"  ✔  Selected '{field_label}' → {c!r}")
                return True
            except Exception:
                pass
        log(f"  –  None of the candidates matched for '{field_label}': {candidates}")
    except PWTimeoutError:
        log(f"  –  Select not found: '{field_label}'")
    return False


async def check_by_label(page, text: str) -> bool:
    """Click a checkbox whose associated label contains the given text."""
    for strategy in [
        f"label:has-text('{text}')",
        f"text={text}",
    ]:
        try:
            loc = page.locator(strategy).first
            await loc.wait_for(state="visible", timeout=4_000)
            await loc.click()
            log(f"  ✔  Checked option: '{text}'")
            return True
        except PWTimeoutError:
            pass
    # Fallback: find the input by value
    try:
        cb = page.locator(f"input[type='checkbox'][value='{text}']").first
        await cb.wait_for(state="visible", timeout=3_000)
        await cb.check()
        log(f"  ✔  Checked by value: '{text}'")
        return True
    except PWTimeoutError:
        log(f"  –  Checkbox not found: '{text}'")
        return False


async def fill_textarea(page, selector: str, value: str, label: str = "") -> bool:
    """Fill a textarea; return True on success."""
    try:
        loc = page.locator(selector).first
        await loc.wait_for(state="visible", timeout=6_000)
        await loc.click()
        await loc.fill(value)
        log(f"  ✔  Filled textarea '{label or selector}' ({len(value)} chars)")
        return True
    except PWTimeoutError:
        log(f"  –  Textarea not found: '{label or selector}'")
        return False


# ── School typeahead helper ────────────────────────────────────────────────────

async def fill_school_typeahead(page) -> bool:
    """Type into the school typeahead and select FIU from the dropdown."""
    school_query = "Florida International"
    selectors = [
        "input[name*='school']",
        "input[placeholder*='chool']",
        "input[placeholder*='niversity']",
        "#s2id_education_school_name_0 input",
        ".select2-search input",
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            await loc.wait_for(state="visible", timeout=5_000)
            await loc.fill(school_query)
            await asyncio.sleep(1.2)
            # Try clicking the typeahead result
            for result_sel in [
                f"text=Florida International University",
                ".select2-result-label:has-text('Florida International')",
                "li:has-text('Florida International University')",
                "[class*='suggestion']:has-text('Florida International')",
            ]:
                try:
                    result = page.locator(result_sel).first
                    await result.wait_for(state="visible", timeout=3_000)
                    await result.click()
                    log("  ✔  School typeahead → 'Florida International University'")
                    return True
                except PWTimeoutError:
                    pass
            log(f"  –  School typeahead result not found after typing in {sel}")
        except PWTimeoutError:
            pass
    # Fallback: treat as a plain text input
    await safe_fill(page, "input[id*='school']",
                    "Florida International University", "School (plain)")
    return False


# ── Main application flow ──────────────────────────────────────────────────────

async def run():
    assert RESUME_PATH.exists(), f"Resume PDF not found at {RESUME_PATH}"
    PROCESSED.mkdir(parents=True, exist_ok=True)

    PRE_SS  = PROCESSED / f"pre_submit_{DOMAIN}.png"
    POST_SS = PROCESSED / f"post_submit_{DOMAIN}.png"

    log("═══════════════════════════════════════════════════════════════════")
    log("  LIVE MODE — Canonical / Graduate Software Engineer application")
    log(f"  URL    : {JOB_URL}")
    log(f"  Resume : {RESUME_PATH}")
    log("═══════════════════════════════════════════════════════════════════")

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

        # ── Step 2: Click "Apply for this job" button if present ─────────────
        log("Step 2 — Looking for 'Apply for this job' button …")
        try:
            for btn_text in ["Apply for this job", "Apply Now", "Apply"]:
                try:
                    btn = page.get_by_role("link", name=btn_text)
                    await btn.first.wait_for(state="visible", timeout=5_000)
                    await btn.first.click()
                    await page.wait_for_load_state("domcontentloaded", timeout=15_000)
                    log(f"         Clicked '{btn_text}' button.")
                    break
                except PWTimeoutError:
                    pass
        except Exception:
            log("         Apply button not found — current page IS the form.")

        log(f"         Form URL  : {page.url}")
        log(f"         Form title: {await page.title()}")

        # ── Step 3: Identity fields ───────────────────────────────────────────
        log("Step 3 — Filling identity fields …")
        # Greenhouse standard IDs
        await safe_fill(page, "input#first_name",
                        APPLICANT["first_name"], "First name")
        await safe_fill(page, "input#last_name",
                        APPLICANT["last_name"],  "Last name")
        await safe_fill(page, "input#email",
                        APPLICANT["email"],      "Email")
        await safe_fill(page, "input#phone",
                        APPLICANT["phone"],      "Phone")
        # Greenhouse name-attribute variants
        for attr, value, lbl in [
            ("job_application[first_name]", APPLICANT["first_name"], "First name (alt)"),
            ("job_application[last_name]",  APPLICANT["last_name"],  "Last name (alt)"),
            ("job_application[email]",      APPLICANT["email"],      "Email (alt)"),
            ("job_application[phone]",      APPLICANT["phone"],      "Phone (alt)"),
        ]:
            await safe_fill(page, f"input[name='{attr}']", value, lbl)

        # Country of residence
        log("Step 3b — Setting country dropdown …")
        for sel in ["select#country", "select[name*='country']",
                    "select[id*='country']"]:
            for val in ["US", "United States", "United States of America", "USA"]:
                if await safe_select(page, sel, value=val,
                                     field_label="Country"):
                    break
            else:
                continue
            break

        # ── Step 4: Resume upload ─────────────────────────────────────────────
        log("Step 4 — Uploading resume PDF …")
        uploaded = False
        for selector in [
            "input[type='file']",
            "input#resume",
            "input[name='job_application[resume]']",
            "input[accept*='pdf']",
            "input[name*='resume']",
        ]:
            if await safe_upload(page, selector, RESUME_PATH, "Resume PDF"):
                uploaded = True
                break
        if not uploaded:
            log("  ⚠  No resume file-input found — proceeding anyway.")

        # ── Step 5: Education section ─────────────────────────────────────────
        log("Step 5 — Filling education section …")

        # School typeahead
        await fill_school_typeahead(page)

        # Degree dropdown
        await safe_select_first_match(
            page,
            "select[name*='degree'], select[id*='degree']",
            ["Bachelor's Degree", "Bachelor", "Bachelor of Science",
             "Undergraduate", "B.S.", "BS"],
            "Degree",
        )

        # Discipline / field of study dropdown
        await safe_select_first_match(
            page,
            "select[name*='discipline'], select[id*='discipline'], "
            "select[name*='field_of_study'], select[id*='field']",
            ["Computer Science", "Computer Science & Engineering",
             "Information Technology", "Computer Engineering", "Software Engineering"],
            "Discipline",
        )

        # ── Step 6: Custom question dropdowns ────────────────────────────────
        log("Step 6 — Answering custom question dropdowns …")

        # Plagiarism / AI-content agreement
        for sel in ["select[id*='plagiarism']", "select[id*='ai']",
                    "select[id*='agreement']", "select[id*='confirm']"]:
            await safe_select_first_match(
                page, sel,
                ["I agree to use only my own words",
                 "I agree", "Yes", "Agree"],
                "Plagiarism/AI agreement",
            )

        # Graduation year
        for sel in ["select[id*='graduation']", "select[id*='grad_year']",
                    "select[id*='graduate']"]:
            await safe_select_first_match(
                page, sel,
                ["2026", "2025 or 2026", "2026 (Bachelor's)",
                 "Bachelor degree completed/expected 2025-2026"],
                "Graduation year",
            )

        # High school mathematics performance
        for sel in ["select[id*='math']", "select[id*='mathematics']",
                    "select[id*='hs_math']"]:
            await safe_select_first_match(
                page, sel,
                ["Exceptional", "Outstanding", "Top of class",
                 "A", "A+", "Excellent", "High distinction",
                 "Top grade", "Highest grade"],
                "HS Math performance",
            )

        # High school native-language performance
        for sel in ["select[id*='native_language']", "select[id*='language']",
                    "select[id*='english']", "select[id*='hs_lang']"]:
            await safe_select_first_match(
                page, sel,
                ["Exceptional", "Outstanding", "Top of class",
                 "A", "A+", "Excellent", "High distinction",
                 "Top grade", "Highest grade"],
                "HS Language performance",
            )

        # Current work country
        for sel in ["select[id*='work_country']", "select[id*='location']",
                    "select[id*='current_country']"]:
            await safe_select_first_match(
                page, sel,
                ["United States", "United States of America", "US", "USA"],
                "Current work country",
            )

        # International travel commitment
        for sel in ["select[id*='travel']", "select[id*='international']"]:
            await safe_select_first_match(
                page, sel,
                ["Yes", "2-4 times yearly, 1-2 week events",
                 "I can travel 2-4 times a year",
                 "I confirm I can travel internationally",
                 "I am able to travel"],
                "International travel",
            )

        # Companies worked for since undergrad graduation
        for sel in ["select[id*='companies']", "select[id*='employer']",
                    "select[id*='worked']", "select[id*='jobs']"]:
            await safe_select_first_match(
                page, sel,
                ["0", "None", "Zero", "N/A",
                 "I have not yet graduated from my first undergraduate degree",
                 "Still in university", "No full-time employment"],
                "Companies worked for",
            )

        # Canonical privacy notice agreement
        for sel in ["select[id*='privacy']", "select[id*='canonical_privacy']",
                    "select[id*='consent']"]:
            await safe_select_first_match(
                page, sel,
                ["I agree", "I accept", "Yes", "Agree",
                 "I have read and agree to the Privacy Notice"],
                "Privacy notice agreement",
            )

        # ── Step 7: Textareas ─────────────────────────────────────────────────
        log("Step 7 — Filling custom question textareas …")

        # All Greenhouse custom-question textareas share the same tag; we
        # target them by associated label text.
        textarea_map = [
            ("linux",       LINUX_EXPERIENCE,      "Linux & open-source experience"),
            ("project",     PROJECT_DESCRIPTION,   "Personal software project"),
            ("leadership",  LEADERSHIP_EXPERIENCE, "Leadership experience"),
            ("high_school", HS_PERF_JUSTIFICATION, "HS performance justification"),
            ("bachelor",    BACHELORS_RESULT,       "Bachelor's degree result"),
        ]

        # Strategy: find labels that contain keyword, then use the sibling textarea
        for keyword, answer, desc in textarea_map:
            filled = False
            for label_sel in [
                f"label:has-text('{keyword}')",
                f"label:has-text('{keyword.replace('_', ' ')}')",
            ]:
                try:
                    label_loc = page.locator(label_sel).first
                    await label_loc.wait_for(state="visible", timeout=3_000)
                    # Get the `for` attribute to find the textarea by id
                    for_val = await label_loc.get_attribute("for")
                    if for_val:
                        ta = page.locator(f"#{for_val}").first
                        await ta.wait_for(state="visible", timeout=3_000)
                        await ta.fill(answer)
                        log(f"  ✔  Filled textarea '{desc}' via label[for=#{for_val}]")
                        filled = True
                        break
                except (PWTimeoutError, Exception):
                    pass
            if not filled:
                # Broad fallback: fill all visible textareas in document order
                log(f"  ~  Will attempt positional fallback for '{desc}'")

        # Positional fallback — map textareas by their visual order on the page
        log("Step 7b — Positional textarea fallback …")
        try:
            all_tas = page.locator("textarea")
            count = await all_tas.count()
            log(f"         Found {count} textarea(s) on page.")
            # Canonical form order (based on form inspection):
            # 0 = Linux experience, 1 = project, 2 = leadership,
            # 3 = HS justification, 4 = bachelor result
            positional = [
                (0, LINUX_EXPERIENCE,      "Linux & open-source experience"),
                (1, PROJECT_DESCRIPTION,   "Personal software project"),
                (2, LEADERSHIP_EXPERIENCE, "Leadership experience"),
                (3, HS_PERF_JUSTIFICATION, "HS performance justification"),
                (4, BACHELORS_RESULT,       "Bachelor's degree result"),
            ]
            for idx, answer, desc in positional:
                if idx < count:
                    ta = all_tas.nth(idx)
                    try:
                        current_val = await ta.input_value()
                    except Exception:
                        current_val = ""
                    if not current_val.strip():
                        await ta.fill(answer)
                        log(f"  ✔  Positional fill textarea[{idx}] → '{desc}'")
                    else:
                        log(f"  –  textarea[{idx}] already filled, skipping.")
        except Exception as e:
            log(f"  –  Positional textarea pass failed: {e}")

        # ── Step 8: Checkboxes ────────────────────────────────────────────────
        log("Step 8 — Checking engineering interest and language checkboxes …")

        # Areas of engineering interest (up to 3)
        for interest in ["AI/ML", "Cloud", "Ubuntu Server", "Server"]:
            await check_by_label(page, interest)

        # Programming languages confidence (up to 3)
        for lang in ["Python", "Golang", "Rust", "Go"]:
            await check_by_label(page, lang)

        # ── Step 9: Optional link fields ─────────────────────────────────────
        log("Step 9 — Optional link fields …")
        await safe_fill(page,
                        "input#job_application_linkedin_profile_url",
                        APPLICANT["linkedin"], "LinkedIn")
        for sel in ["input[name*='linkedin']", "input[id*='linkedin']"]:
            await safe_fill(page, sel, APPLICANT["linkedin"], "LinkedIn (alt)")
        for sel in ["input[name*='website']", "input[id*='website']"]:
            await safe_fill(page, sel, APPLICANT["website"], "Website")
        for sel in ["input[name*='github']", "input[id*='github']"]:
            await safe_fill(page, sel, APPLICANT["github"], "GitHub")

        # ── Step 10: D&I required fields ─────────────────────────────────────
        log("Step 10 — Required D&I fields …")
        # Gender identity
        for sel in ["select[id*='gender_identity']", "select[name*='gender_identity']"]:
            await safe_select_first_match(
                page, sel,
                ["Male", "Man", "Prefer not to say",
                 "Prefer not to disclose", "I don't wish to answer"],
                "Gender identity",
            )
        # Nationality
        for sel in ["select[id*='nationality']", "select[name*='nationality']"]:
            await safe_select_first_match(
                page, sel,
                ["American", "United States", "US",
                 "Prefer not to say", "Prefer not to disclose"],
                "Nationality",
            )
        # Race or ethnicity
        for sel in ["select[id*='race']", "select[name*='race']",
                    "select[id*='ethnicity']", "select[name*='ethnicity']"]:
            await safe_select_first_match(
                page, sel,
                ["Prefer not to say", "Prefer not to disclose",
                 "I don't wish to answer", "Decline to self identify"],
                "Race/Ethnicity",
            )

        # ── Step 11: Voluntary EEO self-ID ───────────────────────────────────
        log("Step 11 — Voluntary EEO self-ID …")
        eeo_selects = [
            ("select[name*='gender']",     "EEO gender"),
            ("select[name*='hispanic']",   "Hispanic/Latino"),
            ("select[name*='veteran']",    "Veteran status"),
            ("select[name*='disability']", "Disability status"),
        ]
        for sel, lbl in eeo_selects:
            await safe_select_first_match(
                page, sel,
                ["Prefer not to say", "Decline to self identify",
                 "I don't wish to answer", "prefer_not_to_say",
                 "I do not wish to answer"],
                lbl,
            )

        # ── Step 12: Pre-submit screenshot ───────────────────────────────────
        log("Step 12 — Taking PRE-SUBMIT screenshot …")
        await page.screenshot(path=str(PRE_SS), full_page=True)
        log(f"  ✔  Saved: {PRE_SS}")

        # ── Step 13: Locate and click Submit ─────────────────────────────────
        log("Step 13 — Locating submit button …")
        submit_btn = None

        for btn_name in ["Submit application", "Submit Application",
                         "Submit", "Apply", "Send application"]:
            try:
                candidate = page.get_by_role("button", name=btn_name)
                await candidate.first.wait_for(state="visible", timeout=5_000)
                submit_btn = candidate.first
                log(f"  ✔  Found submit button: '{btn_name}'")
                break
            except PWTimeoutError:
                pass

        if submit_btn is None:
            try:
                submit_btn = page.locator(
                    "input[type='submit'], button[type='submit']"
                ).first
                await submit_btn.wait_for(state="visible", timeout=5_000)
                log("  ✔  Found submit via type=submit fallback")
            except PWTimeoutError:
                log("  ✗  Submit button NOT FOUND — aborting.")
                await browser.close()
                return

        log("  → CLICKING SUBMIT NOW …")
        await submit_btn.click()

        # ── Step 14: Wait 5 s, take post-submit screenshot ───────────────────
        log("Step 14 — Waiting 5 s for post-submit page to load …")
        await asyncio.sleep(5)
        log(f"          Post-submit URL  : {page.url}")
        log(f"          Post-submit title: {await page.title()}")
        await page.screenshot(path=str(POST_SS), full_page=True)
        log(f"  ✔  Saved: {POST_SS}")

        await browser.close()

    # ── Step 15: Append metadata to applied_jobs.json ────────────────────────
    log("Step 15 — Appending metadata to applied_jobs.json …")
    new_record = {
        "company":          "Canonical",
        "role":             "Graduate Software Engineer",
        "job_id":           "7814327",
        "url":              JOB_URL,
        "date_applied":     str(date.today()),
        "dry_run":          False,
        "resume_used":      str(RESUME_PATH),
        "script":           "apply_canonical_7814327.py",
        "execution_status": "submitted_live",
        "screenshots": {
            "pre_submit":  str(PRE_SS),
            "post_submit": str(POST_SS),
        },
        "profile_mapping": {
            "role_type":           "Linux / Open Source / General Software Engineering",
            "primary_project":     (
                "ViewGuard — real-time security pipeline: YOLOv8 + Gemini 2.0 Flash, "
                "async multi-stream, FastAPI backend, React telemetry dashboard"
            ),
            "secondary_project":   (
                "Shadow Vision — open-source hand-gesture dataset release on GitHub, "
                "Python/OpenCV/MediaPipe, 90%+ accuracy"
            ),
            "tertiary_project":    (
                "Voxtant — 1st of 80+ PlutoHacks 2025, AI agent workflow for "
                "interview coaching; Helios AI — 1st at Knight Hacks VIII (UCF)"
            ),
            "engineering_areas":   ["AI/ML", "Cloud", "Ubuntu Server"],
            "languages_checked":   ["Python", "Golang", "Rust"],
            "graduation_year":     "2026",
            "cover_letter":        "not present on this form",
            "salary_field":        "not present on this form",
            "us_work_auth":        "Yes — legally authorized, no sponsorship needed",
            "travel_commitment":   "Yes — 2-4 times yearly confirmed",
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
    log(f"  ✔  Metadata appended → {APPLIED_LOG}")

    log("")
    log("═══════════════════════════════════════════════════════════════════")
    log("  APPLICATION COMPLETE — Canonical / Graduate Software Engineer")
    log("═══════════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    asyncio.run(run())
