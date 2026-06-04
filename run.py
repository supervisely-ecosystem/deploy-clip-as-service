import subprocess
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if log_level in ["DEBUG", "INFO", "WARNING"]:
    os.environ["JINA_LOG_LEVEL"] = log_level


def gpu_available():
    """Return True if a usable CUDA device is visible to PyTorch."""
    try:
        import torch

        return torch.cuda.is_available()
    except Exception as e:  # torch missing / driver mismatch / etc.
        print(f"Could not detect CUDA availability, assuming CPU: {e}")
        return False


def resolve_backend():
    """Pick the CLIP backend flow based on the modal switch.

    Modes (modal.state.deviceMode):
      - "auto" (default): PyTorch on GPU if available, otherwise ONNX on CPU.
      - "gpu":            force the PyTorch backend.
      - "cpu":            force the ONNX (CPU) backend.

    Both backends run the SAME model (ViT-B-32::openai, fp32, 512-D) with the
    same clip-server preprocessing, so the embeddings they produce are
    interchangeable and can be mixed in the same index.
    """
    mode = os.getenv("modal.state.deviceMode", "auto").strip().lower()

    if mode == "gpu":
        return "clip.yml", "PyTorch (forced GPU)"
    if mode == "cpu":
        return "clip_onnx.yml", "ONNX (forced CPU)"

    # auto
    if gpu_available():
        return "clip.yml", "PyTorch (auto: GPU detected)"
    return "clip_onnx.yml", "ONNX (auto: no GPU, using CPU)"


flow_file, backend_desc = resolve_backend()
print(f"Selected CLIP backend: {backend_desc} -> {flow_file}", flush=True)

proc = subprocess.Popen(
    ["python", "-m", "clip_server", flow_file],
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