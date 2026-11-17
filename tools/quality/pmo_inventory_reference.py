"""BUG3189/YKT2657: check one public WBS reference; explicit repair changes only its hash.

This never validates coverage, artifacts, ownership, runtime evidence or acceptance.
It reads only the fixed 485/486 JSON pair, not paths named by their contents.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PMO = ROOT / 'documents/400_PGPT/470_PMO'


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def check(rebind=False):
    inventory = PMO / '485_WBS網羅性・受入対応.json'
    snapshot = PMO / '486_WBS現行実績.json'
    if inventory.is_symlink() or snapshot.is_symlink():
        raise ValueError('fixed regular public JSON inputs required')
    raw_inventory, raw_snapshot = inventory.read_bytes(), snapshot.read_bytes()
    json.loads(raw_inventory, object_pairs_hook=unique)
    before = json.loads(raw_snapshot, object_pairs_hook=unique)
    previous = before['inventorySha256']
    if not isinstance(previous, str) or not re.fullmatch('[0-9a-f]{64}', previous):
        raise ValueError('explicit previous SHA256 required')
    actual = hashlib.sha256(raw_inventory).hexdigest()
    matched = previous == actual
    if rebind and not matched:
        pattern = rb'("inventorySha256"\s*:\s*")' + previous.encode() + rb'(")'
        if len(re.findall(pattern, raw_snapshot)) != 1:
            raise ValueError('unambiguous single reference required')
        changed = re.sub(pattern, lambda m: m[1] + actual.encode() + m[2], raw_snapshot)
        after = json.loads(changed, object_pairs_hook=unique)
        expected = dict(before, inventorySha256=actual)
        if after != expected or inventory.read_bytes() != raw_inventory or snapshot.read_bytes() != raw_snapshot:
            raise ValueError('other fields or inputs changed')
        snapshot.write_bytes(changed)
        if snapshot.read_bytes() != changed:
            raise ValueError('reference write not confirmed')
        matched = True
    return dict(actualExit=0 if matched else 1, referenceMatches=matched,
                previousReference=previous, actualInventorySha256=actual,
                referenceRebound=bool(rebind and previous != actual),
                snapshotOtherFieldsUnchanged=True, wholeWbsAccepted=False,
                formalUpdated=False, newAcceptance=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebind', action='store_true', help='explicitly repair only inventorySha256')
    result = check(parser.parse_args().rebind)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(result['actualExit'])
