import os
from pathlib import Path


def workbench_root():
    return Path(__file__).resolve().parents[4]


def data_dir():
    override = os.environ.get("HR_COLLECTOR_DATA_DIR") or os.environ.get("BEANNOTE_DATA_DIR")
    root = Path(override).expanduser() if override else workbench_root() / ".agents/local-config/source-collector"
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    return root


def inbox_dir():
    override = os.environ.get("HR_SOURCE_DIR")
    if override:
        root = Path(override).expanduser()
    elif os.environ.get("HR_COLLECTOR_DATA_DIR") or os.environ.get("BEANNOTE_DATA_DIR"):
        root = data_dir() / "inbox"
    else:
        root = workbench_root() / "source/collected"
    root.mkdir(parents=True, exist_ok=True)
    return root
