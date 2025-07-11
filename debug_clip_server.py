import debugpy
import sys
import os


debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger attach to clip_server...")
debugpy.wait_for_client()
print("Debugger attached, starting clip_server...")


sys.argv = ["clip_server", "clip.yml"]
from clip_server.__main__ import main
main()