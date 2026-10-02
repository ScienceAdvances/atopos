"""Small filesystem helpers for analysis output."""

from pathlib import Path


def mkdir(directory, *, parents=True, exist_ok=True):
    """Create an output directory and return its absolute path."""
    if isinstance(directory, str) and not directory.strip():
        raise ValueError("directory must not be empty.")
    path = Path(directory).expanduser().resolve()
    path.mkdir(parents=parents, exist_ok=exist_ok)
    return path
