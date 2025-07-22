import subprocess
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if log_level in ["DEBUG", "INFO", "WARNING"]:
    os.environ["JINA_LOG_LEVEL"] = log_level

proc = subprocess.Popen(
    ["python", "-m", "clip_server", "clip.yml"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

for line in proc.stdout:
    s = line.strip()

    # Remove empty lines
    if not s:
        continue
    
    log_levels = ["INFO", "DEBUG", "WARNING", "ERROR"]

    # Skip /dry_run request logs unless DEBUG mode is enabled
    if log_level != "DEBUG" and "/dry_run" in s:
        continue

    # Check if the message is not empty after the log level
    if any(s.startswith(level) or level in s for level in log_levels):
        # Skip the line if it consists only of the log level and date
        if s in [f"{level}{s[-19:]}" for level in log_levels]:
            continue

    print(line, end="")