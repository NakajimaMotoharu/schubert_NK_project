"""Read16 existing5944 class/XML counters for next PG planning only; never replay tests."""
import hashlib
import json
import os
import shlex
import types
from lan_server import run
import pg5936_monitor_baseline_coverage as previous
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5944_private_lock_whole import SOURCE


def reader(data):
    raw = previous.reader(data).replace('PG5926', 'PG5944')
    if 'PG5926' in raw or any(s in raw for s in ('Popen', 'subprocess', 'socket.connect', 'systemctl')):
        raise ValueError('original5944 bounded artifact read only')
    compile(raw, '<bounded original5944 reader>', 'exec')
    return raw


def main():
    qp = BASE/'PG5944-current3973-cases/qualification.json'; pp = BASE/'PG5964-api-sql21-plan-v1/manifest.json'
    if sha(qp) != '6370d6c31b7ac1124c6cb3abce653f7441ce0fa87b291f948cef5ddcb2977225' or sha(pp) != '56b461725810f8a706b0c1e9dd092dabf68f631a99593462bc01b7ca9784c2b8':
        raise ValueError('actual current3973 and original21-condition plan')
    q, plan = (json.loads(p.read_bytes()) for p in (qp, pp))
    if q['productionSource'] != SOURCE or plan['source'] != SOURCE or q['projectionActualExit'] != 0 or q['mainClasses'] != 1666 or q['FESFlakyNotRun'] != 0:
        raise ValueError('genuine same-source qualified original only')
    targets = []
    for row in plan['sourcePlans']:
        if sha(ROOT/row['path']) != row['beforeSha256']:
            raise ValueError('next PG not applied and no source drift')
        targets.append(dict(module='api', **{'class': row['path'].split('/src/main/java/')[1][:-5]}))
    scope = {**vars(previous), 'SOURCE': SOURCE, 'reader': reader}
    raw = types.FunctionType(previous.bounded_reader.__code__, scope, 'current_bounded_reader')(q, targets)
    os.umask(0o077); private = W/'pg5962-api-sql16-baseline-v1'; private.mkdir()
    with (private/'reader.private.py').open('x') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    code, text = run('python3 -B -c '+shlex.quote(raw), timeout=90)
    with (private/'observer.private.log').open('x') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    if code:
        raise ValueError('original artifact read failed; no test or alternate execution')
    result = json.loads(next(s for s in reversed(text.splitlines()) if s.startswith('{')))
    if result['actualExit'] != 0 or result['source'] != SOURCE or len(result['targets']) != 16:
        raise ValueError('all16 actual original counters')
    out = BASE/'PG5962-api-sql16-baseline-v1'; out.mkdir()
    value = {**result, 'currentWholeQualificationSha256': sha(qp), 'nextPgPlanSha256': sha(pp),
             'readerSha256': hashlib.sha256(raw.encode()).hexdigest(), 'readerPayloadBytes': len(raw.encode()),
             'baselineOnlyNotNewPgAcceptance': True, 'qualifiedTargets': sum(r['baselineFour100'] for r in result['targets']),
             'formalAccepted': False, 'F03Accepted': False, 'ptAlternativeCompleted': 0}
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, actualOriginalTargets=16, baselineFour100=value['qualifiedTargets'],
                         incomplete=[r for r in result['targets'] if not r['baselineFour100']], manifestSha256=sha(out/'manifest.json'), newPgAccepted=False)))


if __name__ == '__main__':
    main()
