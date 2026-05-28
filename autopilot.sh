#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Autopilot started. PID: $$"

while true; do
  echo "[$(date)] Scraping for new jobs..."
  cd "$SCRIPT_DIR"
  python job_scraper.py

  echo "[$(date)] Processing queue..."
  ./run_queue.sh

  echo "[$(date)] Cycle complete. Sleeping for 1 hour..."
  sleep 3600
done
