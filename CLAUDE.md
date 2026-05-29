# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

An autonomous 24/7 job application pipeline for Gabriel Suarez. It scrapes new-grad software engineering roles from Greenhouse and Lever job boards, then uses a Claude Code agent (via `claude -p`) to generate and execute Playwright scripts that fill and submit each application end-to-end.

## Running the daemon

```bash
./controller.sh start    # launch autopilot.sh in background via setsid, PID → daemon.pid
./controller.sh stop     # kill process group (autopilot + children)
./controller.sh status   # check if alive
tail -f system.log       # watch live output
```

**One full cycle:** `job_scraper.py` → `run_queue.sh` → sleep 1 hour → repeat.

## Running components manually

```bash
# Scrape new jobs into the queue
python job_scraper.py

# Process the queue once (without the autopilot wrapper)
./run_queue.sh

# Run a specific generated Playwright script directly
python apply_sigmacomputing_4451416003_v5.py

# Re-queue dry-run jobs from processed/ back to queue/
python requeue_missed_jobs.py
```

## Architecture

### Pipeline flow

```
job_scraper.py
  └─ Serper API search → filters senior roles → deduplicates against
     applied_jobs.json + existing queue/ files → writes job_N.md to queue/

run_queue.sh (per job file)
  ├─ curl google.com  (connectivity check, retry every 5 min)
  ├─ claude --effort max -p "LIVE MODE..." --system-prompt-file agent-prompt.md
  │    └─ Agent phases (see agent-prompt.md):
  │         1. WebFetch full JD from URL
  │         2. Gatekeeper (hard reject if senior / off-domain / generic page)
  │         3. Fill identity/demographics (hardcoded — see Phase 3 table)
  │         4. Tailor resume bullets to role type
  │         5. Answer every wildcard field (never blank)
  │         6. Write Playwright script with networkidle waits + pre-submit scroll audit
  │         7. Execute script → Validation Catcher evaluates DOM for CAPTCHA/errors
  │         8. Append result to applied_jobs.json
  ├─ Check for error_{domain}.png  → job stays in queue, log printed
  ├─ Check for post_submit_{domain}.png → job moved to processed/
  └─ Rate-limit guard: if TEMP_LOG contains "usage limit exceeded" / "out of messages"
       / "wait until" → sleep 18000s then retry same job
```

### Key files

| File | Purpose |
|---|---|
| `agent-prompt.md` | System prompt fed to the Claude agent. All 8 phases live here. **Edit this to change agent behavior.** |
| `job-data/applied_jobs.json` | Ground truth for every application attempt. Dedup source for the scraper. |
| `job-data/resume.md` | Markdown resume — the agent reads this at runtime for tailoring. |
| `job-data/resume.pdf` | Uploaded to every file input. Never replaced with the .md file. |
| `.env` | `SERPER_API_KEY` — required for scraper. Not committed. |

### Screenshot contract (how run_queue.sh knows if a job succeeded)

The Playwright script's Validation Catcher (Phase 7 of agent-prompt.md) must write to these absolute paths:
- **Success:** `/workspaces/auto-applier/job-data/processed/post_submit_{domain}.png`
- **Failure:** `/workspaces/auto-applier/job-data/processed/error_{domain}.png`

`run_queue.sh` checks for these files after `claude` exits. No screenshot = script crashed = job stays in queue. If you change the screenshot paths in agent-prompt.md, update the `SUCCESS_SCREENSHOT` / `ERROR_SCREENSHOT` variables in `run_queue.sh` to match.

### Deduplication logic

`job_scraper.py` normalizes URLs (strips `http(s)://`, trailing slashes, `/apply` suffix) and skips any URL already present in `applied_jobs.json` or the current `queue/` directory. If a job keeps re-appearing in the queue, check that its URL in `applied_jobs.json` matches the format the scraper sees from Serper.

## Known issues

**Greenhouse HTTP 428 (CAPTCHA email):** Greenhouse's bot detection can respond with a 428 status mid-submission, triggering an email with a security code to `gabrielsc05131@gmail.com`. When this happens, `submission_status` in `applied_jobs.json` will be `"failed_captcha"`. The diagnostic scripts (`sigma_post428_diagnostic.py`, `sigma_btn_diagnostic.py`) were written to investigate this — they can be used as a template for re-attempting a specific job with a code passed as a CLI argument.

**Duplicate `applied_jobs.json` entries:** The agent appends to this file on every run. If a job is retried (e.g., after a CAPTCHA failure), it will appear multiple times. The scraper deduplicates on URL only, so multiple attempts at the same URL are normal and expected.

**`apply_*.py` versioned scripts:** Files like `apply_sigmacomputing_4451416003_v3.py` through `v8.py` are debugging artifacts from manual iteration on a single job. The pipeline generates a fresh script per run — old versioned files can be deleted freely.

## Modifying agent behavior

All agent logic lives in `agent-prompt.md`. The phases map directly to what the agent does:
- Change hard-reject rules → Phase 2
- Change identity/demographic answers → Phase 3 table
- Change which projects get highlighted per role type → Phase 4
- Change how wildcard fields are answered → Phase 5
- Change Playwright script structure → Phase 6
- Change CAPTCHA/error detection selectors → Phase 7 Validation Catcher
