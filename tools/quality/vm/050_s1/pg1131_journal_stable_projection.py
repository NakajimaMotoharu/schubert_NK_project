"""Independent journal JSON projection: all fields and event order retained.

Only JSON object key order is nonsemantic. Raw input is preserved separately.
BUG1035/YKT804; no Production method, cursor stripping or field exclusions.
"""
import json


def pairs(items):
    result = {}
    for key, value in items:
        if key in result: raise ValueError('duplicate journal field refused')
        result[key] = value
    return result


def project(raw):
    if type(raw) is not bytes: raise ValueError('journal byte input refused')
    rows = []
    for line in raw.splitlines():
        row = json.loads(line, object_pairs_hook=pairs)
        if type(row) is not dict or type(row.get('__CURSOR')) is not str or not row['__CURSOR']:
            raise ValueError('journal event cursor refused')
        if any(type(value) not in (str, list) or
               (type(value) is list and any(type(item) not in (str, int) for item in value))
               for value in row.values()):
            raise ValueError('journal field representation refused')
        rows.append(row)
    cursors = [row['__CURSOR'] for row in rows]
    if len(set(cursors)) != len(cursors): raise ValueError('duplicate journal cursor refused')
    return (json.dumps(rows, sort_keys=True, ensure_ascii=True, separators=(',', ':')) + '\n').encode()
