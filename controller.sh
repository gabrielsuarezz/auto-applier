#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/daemon.pid"
LOG_FILE="$SCRIPT_DIR/system.log"

case "$1" in
  start)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "Daemon already running (PID $PID)."
        exit 1
      else
        echo "Stale PID file found. Cleaning up."
        rm -f "$PID_FILE"
      fi
    fi
    cd "$SCRIPT_DIR"
    setsid ./autopilot.sh > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Daemon started (PID $(cat "$PID_FILE")). Logging to $LOG_FILE."
    ;;

  stop)
    if [ ! -f "$PID_FILE" ]; then
      echo "No PID file found. Is the daemon running?"
      exit 1
    fi
    PID=$(cat "$PID_FILE")
    if kill -TERM -$PID 2>/dev/null || pkill -P "$PID"; then
      echo "Daemon stopped (PID $PID)."
    else
      echo "Process $PID not found. Cleaning up stale PID file."
    fi
    rm -f "$PID_FILE"
    ;;

  status)
    if [ ! -f "$PID_FILE" ]; then
      echo "Daemon is not running (no PID file)."
      exit 1
    fi
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "Daemon is running (PID $PID)."
    else
      echo "Daemon is not running (stale PID $PID). Run './controller.sh stop' to clean up."
      exit 1
    fi
    ;;

  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
