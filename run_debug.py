import subprocess

proc = subprocess.Popen(
    ["python", "debug_clip_server.py"],
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

    # Check if the message is not empty after the log level
    if any(s.startswith(level) or level in s for level in log_levels):
        # Skip the line if it consists only of the log level and date
        if s in [f"{level}{s[-19:]}" for level in log_levels]:
            continue

    print(line, end="")