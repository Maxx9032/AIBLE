"""PyInstaller entry point for the AIBLE sidecar.

Frozen into a standalone executable so end users need no Python install.
"""

from sidecar.main import run

if __name__ == "__main__":
    run()
