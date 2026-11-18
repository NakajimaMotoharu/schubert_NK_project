"""Use exact past scan positions, current Git blobs, and the WebLog compile/run receipt."""
from collections import Counter
from pathlib import Path
import re

import importlib.util

ENTRY = Path(__file__).resolve()
spec = importlib.util.spec_from_file_location('g07_weblog_range', ENTRY.with_name('5206_g07_weblog_session_delta.py'))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
p = r.load('g07_weblog_cached_origins', '5182_g07_jdbc_metrics_cached_classification.py')
r.configure(p.t.WRAPPER)
p.OUT = p.t.OUT = p.B.OUT = r.OUT
p.WORK = p.t.WORK = p.B.WORK = r.TEMP
p.t.PREPARE_RUNS = ('PG39672',)
p.t.ORDINARY_BUILD_RUNS = ()
B = p.B
BEFORE = r.EVIDENCE / 'PG39660-g07-business-outbox-four-module-public-delta-v1/manifest.json'
POST = r.EVIDENCE / 'PG39684-bug3300-weblog-outbox-post-v1/manifest.json'


def previous_lines():
    previous = B.load(BEFORE)
    assert previous['qualifiedRangeOnly'] and previous['confirmedSecrets'] == previous['unresolvedCandidates'] == 0
    pin = previous['exactPrivateProofFiles']['classified-findings.json']
    file = Path(pin['path'])
    assert file.is_relative_to(r.RETAIN.parent) and B.ref(file) == pin
    rows = B.load(file)
    assert len(rows) == previous['findingsCount'] and all(item['ground'] for item in rows)
    return {(item['rule'], item['lineSha256'], item['startColumn'], item['endColumn']) for item in rows}, B.ref(BEFORE)


def weblog_measurement():
    old = B.load(POST)
    execinfo = POST.with_name('unit-execinfo.stdout')
    assert B.ref(execinfo)['sha256'] == old['files'][execinfo.name]
    lines = execinfo.read_text().splitlines()
    assert old['tests'] == 23 and old['actualExit'] == 0 and old['oldExecCombined'] is False
    sessions = [line for line in lines if line.startswith('Session ')]
    assert len(sessions) == 1 and old['run'] in sessions[0]
    return old, lines


def crc_match(location, key, value):
    if location != POST or len(value) != 16:
        return None
    old, lines = weblog_measurement()
    if old['classIds'].get(key) != value:
        return None
    probes = [line.split() for line in lines if line.split() and line.split()[-1] == key]
    if len(probes) == 1 and probes[0][0] == value:
        return dict(kind='Measured class identity in the original WebLog session',
                    currentPost=B.ref(POST), originalClassReference=key)
    return None


def binary(rows, by_key, scan):
    result = []
    for row in rows:
        file = Path(row['path'])
        if row.get('actualExit') == 0 or file != POST.with_name('jacoco.exec'):
            continue
        props = by_key[(row['path'], row['blob'])]
        projected = r.TEMP / props['relativeProjection']
        old, lines = weblog_measurement()
        assert B.ref(projected)['sha256'] == props['blobSha256'] == old['files']['jacoco.exec']
        classes = [line for line in lines if re.fullmatch(r'[0-9a-f]{16}\s+\d+ of\s+\d+\s+\S+', line)]
        assert len(classes) >= len(old['classIds']) - len(old['naturalNoCodeClasses'])
        result.append(dict(row, actualExit=0, owner=B.ref(POST), derivedRows=len(classes),
                           scope='Original fixed local WebLog 23-test JaCoCo receipt; no new execution'))
    return result


if __name__ == '__main__':
    p.exact_previous = previous_lines
    p.t.checked_run_id = crc_match
    p.t.extra_binary = binary
    p.main()
