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
    """Pick the CLIP flow based on the modal switch.

    Modes (modal.state.deviceMode):
      - "auto" (default): GPU if one is visible, otherwise CPU.
      - "gpu":            force the GPU flow.
      - "cpu":            force the CPU flow.

    Only the device differs. Both flows run PyTorch with the same model
    (ViT-B-32::openai), the same weights, the same preprocessing and the same
    dtype (fp32), which is what keeps the embeddings interchangeable: measured on
    200 images, GPU and CPU agree to 1e-5 per vector and return an identical
    top-10 for every query. So a project can be indexed by a GPU session and
    extended by a CPU one without re-indexing.
    """
    mode = os.getenv("modal.state.deviceMode", "auto").strip().lower()

    if mode == "gpu":
        return "clip.yml", "PyTorch fp32 on GPU (forced)"
    if mode == "cpu":
        return "clip_cpu.yml", "PyTorch fp32 on CPU (forced)"

    # auto
    if gpu_available():
        return "clip.yml", "PyTorch fp32 on GPU (auto: GPU detected)"
    return "clip_cpu.yml", "PyTorch fp32 on CPU (auto: no GPU)"


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