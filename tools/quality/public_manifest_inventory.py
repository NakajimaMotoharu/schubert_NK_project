"""Hash only public artifact children; the final manifest is pinned by an outer reference."""
import hashlib
from pathlib import Path, PurePosixPath
import re


def inventory(directory, manifest_name='manifest.json'):
    directory = Path(directory)
    if not manifest_name or PurePosixPath(manifest_name).parts != (manifest_name,):
        raise ValueError('one manifest filename required')
    result = {}
    for path in sorted(directory.iterdir()):
        if path.name == manifest_name:
            continue
        if path.is_symlink():
            raise ValueError('public artifact symlink is not a fixed input')
        if path.is_file():
            result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def validate(directory, declared, manifest_name='manifest.json'):
    directory = Path(directory)
    if not isinstance(declared, dict):
        raise ValueError('explicit file inventory required')
    for name, expected in declared.items():
        if not isinstance(name, str) or '\\' in name:
            raise ValueError('normalized relative path required')
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or str(path) != name:
            raise ValueError('normalized relative path required')
        if name == manifest_name:
            raise ValueError('manifest must be pinned externally, never self-hashed')
        if not isinstance(expected, str) or re.fullmatch('[0-9a-f]{64}', expected) is None:
            raise ValueError('explicit SHA256 required')
        target = directory
        for part in path.parts:
            target = target / part
            if target.is_symlink():
                raise ValueError('public artifact symlink is not a fixed input')
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('artifact missing or changed')
    return True
