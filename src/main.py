import ctypes
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from ui.app import App  # noqa: E402

if __name__ == "__main__":
    App().mainloop()
