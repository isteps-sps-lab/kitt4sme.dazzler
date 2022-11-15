from pathlib import Path


__version__ = '0.4.0'


def pyproject_file() -> Path:
    this_file = Path(__file__)
    root_dir = this_file.parent.parent
    return root_dir / 'pyproject.toml'