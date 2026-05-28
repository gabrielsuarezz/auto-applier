#!/bin/bash
QUEUE_DIR="job-data/queue"
PROCESSED_DIR="job-data/processed"
PROMPT_FILE="agent-prompt.md"

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
    cat "$job_file" | claude -p "LIVE MODE: Process and fully submit this job application. Do not dry-run." \
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
    SCREENSHOT="$PROCESSED_DIR/post_submit_${DOMAIN}.png"
    if [ ! -f "$SCREENSHOT" ]; then
      echo "=== PLAYWRIGHT ERROR LOG FOR $(basename "$job_file") ==="
      cat "$TEMP_LOG"
      echo "============================================="
      echo "ERROR: Submission screenshot missing at $SCREENSHOT. Refusing to mark $(basename "$job_file") as processed."
      rm -f "$TEMP_LOG"
      continue 2
    fi

    mv "$job_file" "$PROCESSED_DIR/"
    rm -f "$TEMP_LOG"
    echo "Application processed. Cooling down for 15 seconds..."
    sleep 15
    break
  done
done

echo "Queue processing complete."
