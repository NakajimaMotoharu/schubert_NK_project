"""Bind metric records to public completed manifest source, never to a copied caller literal."""
import hashlib
import json
import re
from pathlib import PurePosixPath


def bind_named_sources(root, inventory, selected_paths, allowed_paths, reader=None):
    """Read only explicitly named sources; validate every name before any file I/O.

    An old snapshot inventory can include the entire repository, including held files.
    It is a hash lookup, never an implicit instruction to read each inventory entry.
    """
    denied = {
        'SnapshotKeyCloseWitness.java',
        'pg9892_snapshot_key_close_witness.py',
        'RootFailedStartRecoveryTest.java',
        'RootFailedStartPairRecoveryTest.java',
    }
    selected = list(selected_paths)
    if not selected or len(set(selected)) != len(selected):
        raise ValueError('explicit unique source selection required')
    permitted = set(allowed_paths)
    for name in selected:
        if not isinstance(name, str):
            raise ValueError('relative source name required')
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or path.name in denied:
            raise ValueError('source name is outside permitted selection')
        if name not in permitted or name not in inventory:
            raise ValueError('source must be explicitly allowed and pinned')
        if not re.fullmatch(r'[0-9a-f]{64}', inventory[name]):
            raise ValueError('source checksum required')
    read = reader if reader is not None else lambda path: path.read_bytes()
    result = []
    for name in selected:
        content = read(root / name)
        if hashlib.sha256(content).hexdigest() != inventory[name]:
            raise ValueError('selected source checksum mismatch')
        result.append(dict(path=name, sha256=inventory[name]))
    return result


def bind(records, expected_source):
    if not re.fullmatch(r'[0-9a-f]{40}', expected_source) or not records:
        raise ValueError('explicit source and evidence required')
    output = []
    for path, expected_hash in records:
        if not re.fullmatch(r'[0-9a-f]{64}', expected_hash):
            raise ValueError('exact manifest checksum required')
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError('manifest checksum mismatch')
        manifest = json.loads(content)
        if manifest.get('actualExit') != 0 or type(manifest.get('actualExit')) is not int:
            raise ValueError('completed successful proof required')
        if manifest.get('source') != expected_source:
            raise ValueError('metric source must equal actual proof source')
        output.append(dict(path=str(path), sha256=expected_hash, source=expected_source))
    return output
