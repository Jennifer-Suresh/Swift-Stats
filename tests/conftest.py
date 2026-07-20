from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FOLDER = REPOSITORY_ROOT / "src"

if str(SOURCE_FOLDER) not in sys.path:
    sys.path.insert(0, str(SOURCE_FOLDER))
