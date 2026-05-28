#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUEUE_DIR="$SCRIPT_DIR/job-data/queue"
PROCESSED_DIR="$SCRIPT_DIR/job-data/processed"
PROMPT_FILE="$SCRIPT_DIR/agent-prompt.md"

echo "Starting Autonomous Application Loop..."

for job_file in "$QUEUE_DIR"/*.md; do
  if [ ! -f "$job_file" ]; then
    echo "Queue is empty! Waiting for scraper to find more jobs..."
    break
  fi

  echo "========================================"
  echo "Processing: $(basename "$job_file")"
  echo "========================================"

  while true; do
    # Verify internet connectivity before calling claude
    if ! curl -s --connect-timeout 5 https://www.google.com &>/dev/null; then
      echo "No internet connection. Sleeping 5 minutes..."
      sleep 300
      continue
    fi

    TEMP_LOG=$(mktemp /tmp/claude_job_XXXXXX.log)
    cat "$job_file" | claude \
      --effort max \
      -p "LIVE MODE: Process and fully submit this job application. Do not dry-run. Fill every single field." \
      --system-prompt-file "$PROMPT_FILE" \
      --dangerously-skip-permissions > "$TEMP_LOG" 2>&1

    if grep -qi "usage limit exceeded\|out of messages\|wait until" "$TEMP_LOG"; then
      echo "Pro Limit Hit: Sleeping for 5 hours"
      rm -f "$TEMP_LOG"
      sleep 18000
      continue
    fi

    JOB_URL=$(grep "^URL:" "$job_file" | awk '{print $2}')
    DOMAIN=$(echo "$JOB_URL" | sed 's|https\?://||' | cut -d'/' -f1)
    ERROR_SCREENSHOT="$PROCESSED_DIR/error_${DOMAIN}.png"
    SUCCESS_SCREENSHOT="$PROCESSED_DIR/post_submit_${DOMAIN}.png"

    # Playwright reported CAPTCHA or validation errors via sys.exit(1)
    if [ -f "$ERROR_SCREENSHOT" ]; then
      echo "=== PLAYWRIGHT ERROR LOG FOR $(basename "$job_file") ==="
      cat "$TEMP_LOG"
      echo "============================================="
      echo "ERROR: Playwright detected CAPTCHA or form validation errors. Screenshot saved to $ERROR_SCREENSHOT. Job stays in queue."
      rm -f "$TEMP_LOG"
      continue 2
    fi

    # No screenshot at all — script crashed or agent failed to run Playwright
    if [ ! -f "$SUCCESS_SCREENSHOT" ]; then
      echo "=== PLAYWRIGHT ERROR LOG FOR $(basename "$job_file") ==="
      cat "$TEMP_LOG"
      echo "============================================="
      echo "ERROR: No submission screenshot found at $SUCCESS_SCREENSHOT. Job stays in queue."
      rm -f "$TEMP_LOG"
      continue 2
    fi

    # Success
    mv "$job_file" "$PROCESSED_DIR/"
    rm -f "$TEMP_LOG"
    echo "SUCCESS: $(basename "$job_file") submitted and verified. Cooling down for 15 seconds..."
    sleep 15
    break
  done
done

echo "Queue processing complete."
