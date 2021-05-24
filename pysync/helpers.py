from glob import glob
from pathlib import Path


def expand_path(path: str or Path) -> Path:
    path = glob(str(Path(path).expanduser()))
    return path


def flatten_list(nested_list: list or tuple) -> list:

    supported_types = (list, tuple)

    results = []
    for item in nested_list:
        if not isinstance(item, supported_types):
            results.append(item)
        else:
            results.extend(flatten_list(item))

    return results
