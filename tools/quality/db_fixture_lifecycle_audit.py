"""Audit nullable static DB-fixture AfterAll ownership, without running tests."""
import hashlib
import json
from pathlib import Path
import re

from qualified_nullable_check import LITERALS

FIXTURES = {'ApiLogDatabaseFixture', 'BatchDatabaseFixture', 'WebLogDatabaseFixture'}


def inspect_source(raw):
    clean = LITERALS.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), raw)
    fields = dict((name, kind) for kind, name in re.findall(
        r'\bstatic\s+(?:@[\w.]+\s+)*(\w+DatabaseFixture)\s+(\w+)\s*;', clean))
    nullable = dict((name, kind) for kind, name in re.findall(
        r'\bstatic\s+(?:@[\w.]+\s+)*([\w.<>\[\]]+)\s+(\w+)\s*;', clean))
    entries = []
    for annotation in re.finditer(r'@AfterAll\b', clean):
        start = clean.index('{', annotation.end()); depth = 1; end = start + 1
        while depth and end < len(clean):
            depth += (clean[end] == '{') - (clean[end] == '}'); end += 1
        if depth:
            raise ValueError('unbalanced lifecycle method')
        body = clean[start + 1:end - 1]; matched = False
        cleanup = []
        for call in re.finditer(r'\b(\w+)\.(?:stop|close)\s*\(\s*\)\s*;|\bArrays\.fill\s*\(\s*(\w+)\s*,[^;]*;', body):
            name = call.group(1) or call.group(2)
            if name not in nullable:
                continue
            guarded = re.search(r'if\s*\(\s*' + re.escape(name)
                                + r'\s*!=\s*null\s*\)\s*\{?\s*$', body[:call.start()]) is not None
            cleanup.append({'field': name, 'type': nullable[name], 'guarded': guarded,
                            'span': [start + 1 + call.start(), start + 1 + call.end()]})
        for call in re.finditer(r'\b(\w+)\.stop\s*\(\s*\)\s*;', body):
            name = call.group(1); kind = fields.get(name)
            if kind not in FIXTURES:
                continue
            matched = True
            simple = body.strip() == name + '.stop();'
            guarded = re.search(r'if\s*\(\s*' + re.escape(name)
                                + r'\s*!=\s*null\s*\)\s*\{?\s*$', body[:call.start()]) is not None
            entries.append({'fixtureType': kind, 'field': name,
                            'line': clean.count('\n', 0, start + 1 + call.start()) + 1,
                            'status': 'GUARDED' if guarded else ('UNGUARDED_SIMPLE' if simple else 'MANUAL_REVIEW'),
                            'replacementSpan': [start + 1 + call.start(), start + 1 + call.end()],
                            'cleanupCalls': cleanup})
        if not matched:
            entries.append({'line': clean.count('\n', 0, annotation.start()) + 1,
                            'status': 'NO_NULLABLE_STATIC_DB_STOP',
                            'reason': 'No direct stop of the three nullable static DB fixture types in this lifecycle method'})
    return entries


def scan(root):
    entries = []
    for path in sorted((root / 'src').rglob('*Test.java')):
        raw = path.read_text()
        for row in inspect_source(raw):
            row.update(path=str(path.relative_to(root)), sha256=hashlib.sha256(raw.encode()).hexdigest())
            entries.append(row)
    return entries


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    entries = scan(root)
    print(json.dumps({'entries': entries, 'counts': {s: sum(r['status'] == s for r in entries)
          for s in sorted({r['status'] for r in entries})}}, ensure_ascii=False))
