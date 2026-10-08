"""BUG859/YKT628: explicit raw journal -> typed true-PID1 list join, no authority."""
import json
from pg556_parent_receipt import completed


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate PID1 journal key')
        result[key] = value
    return result


def completed_journal(raw, done):
    if type(raw) is not bytes or not 1 <= len(raw) <= 1048576 or not raw.endswith(b'\n'):
        raise ValueError('PID1 raw journal must be bounded LF bytes')
    rows = [json.loads(line.decode('utf-8'), object_pairs_hook=unique) for line in raw.splitlines()]
    if not rows or any(type(row) is not dict for row in rows):
        raise ValueError('PID1 parsed rows must be objects')
    return rows, completed(rows, done)
