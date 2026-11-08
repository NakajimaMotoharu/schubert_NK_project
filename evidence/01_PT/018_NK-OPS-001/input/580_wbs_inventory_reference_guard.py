"""Validate only the public 485 byte digest referenced by 486, without other worktree IO."""
from pathlib import Path
import hashlib
import json
import re

INVENTORY = 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
ACCEPTANCE = 'documents/400_PGPT/470_PMO/486_WBS現行実績.json'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def validate_bytes(inventory, acceptance):
    source = json.loads(inventory, object_pairs_hook=unique_object)
    target = json.loads(acceptance, object_pairs_hook=unique_object)
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise ValueError('WBS documents must be objects')
    expected = target.get('inventorySha256')
    if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
        raise ValueError('inventorySha256 must be a lowercase SHA256 string')
    observed = hashlib.sha256(inventory).hexdigest()
    if expected != observed:
        raise ValueError('486 inventory reference is stale')
    return dict(bindingValid=True, inventorySha256=observed, productTestsExecuted=0)


def verify_files(root):
    paths = [Path(root) / INVENTORY, Path(root) / ACCEPTANCE]
    for path in paths:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('only fixed regular public WBS documents are accepted')
    return validate_bytes(paths[0].read_bytes(), paths[1].read_bytes())


if __name__ == '__main__':
    print(json.dumps(verify_files(Path.cwd())))
