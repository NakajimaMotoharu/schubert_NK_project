"""Verify public Unit declarations and ordering from a frozen source, without invoking systemd."""
from collections import defaultdict
from datetime import datetime, timezone
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
import hashlib
import json
import re
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
ROOT = Path('src/deployment/systemd')
SS = next(Path('documents/300_SS').rglob('342_*.md'))
ART = 'artemis.service'
API = 'schubert-nk-api.service'
WEB = 'schubert-nk-web.service'
BACKUP = 'schubert-nk-backup.service'
ADMIN = 'schubert-nk-bootstrap-admin.service'
CLEANUP = 'schubert-nk-cleanup.service'
EXPIRY = 'schubert-nk-expiry-cleanup.service'
INBOX = 'schubert-nk-inbox-inspector.service'
MORNING = 'schubert-nk-morning-controller.service'
TARGET = 'schubert-nk-morning.target'
CADDY = 'caddy.service'
POSTGRES = 'postgresql.service'
START = 'caddy.service.d/schubert-nk-startup-policy.conf'
STOP = 'caddy.service.d/schubert-nk-stop-policy.conf'
OPTIONAL = ('optional/inbox-inspector-context-previous.conf',
            'optional/inbox-inspector-response-previous.conf')
DECLARED = {
    ART: ('simple', 'on-failure', '120s', '60s', '143'),
    API: ('simple', 'on-failure', '120s', '60s', None),
    WEB: ('simple', 'on-failure', '120s', '30s', None),
    BACKUP: ('oneshot', 'no', '30min', '60s', None),
    ADMIN: ('oneshot', 'no', '30s', '30s', '20'),
    CLEANUP: ('oneshot', 'no', '30min', '60s', '10'),
    EXPIRY: ('oneshot', 'no', '10min', '60s', '10'),
    INBOX: ('oneshot', 'no', '30min', '60s', '10'),
    MORNING: ('oneshot', 'no', '30min', '60s', '10'),
    START: ('notify', 'no', '30s', '30s', None),
}
ORDER = {
    BACKUP: {POSTGRES}, CLEANUP: {BACKUP, POSTGRES}, ART: {CLEANUP}, EXPIRY: {ART, POSTGRES},
    API: {EXPIRY, ART, POSTGRES}, WEB: {API, ART, POSTGRES},
    MORNING: {POSTGRES}, INBOX: {POSTGRES}, TARGET: {MORNING},
}
REQUIRES = {
    BACKUP: {POSTGRES}, CLEANUP: {POSTGRES}, ART: {CLEANUP}, EXPIRY: {ART, POSTGRES},
    API: {ART, POSTGRES}, WEB: {API, ART, POSTGRES},
    MORNING: {POSTGRES}, INBOX: {POSTGRES}, TARGET: {MORNING},
}
KEYS = ('Type', 'Restart', 'TimeoutStartSec', 'TimeoutStopSec', 'SuccessExitStatus')
SHAPE = re.compile(r'([A-Za-z][A-Za-z0-9]+)=(.*)')


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def require(condition, code):
    if not condition:
        raise ValueError(code)


def parse(raw):
    section = None
    result = defaultdict(list)
    for row in raw.decode().splitlines():
        line = row.strip()
        if not line or line.startswith(('#', ';')):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        match = SHAPE.fullmatch(line)
        require(bool(match and section), 'DIRECTIVE_GRAMMAR')
        key, value = match.groups()
        result[section, key].append(value)
    return dict(result)


def one(rows, section, key):
    values = rows.get((section, key), [])
    require(len(values) <= 1, 'REPEATED_DIRECTIVE')
    return next(iter(values), None)


def units(rows, key):
    return set((one(rows, 'Unit', key) or '').split())


def order_graph(by_name):
    graph = defaultdict(set)
    for name, rows in by_name.items():
        if name in (START, STOP, *OPTIONAL):
            continue
        graph[name] |= units(rows, 'After')
        for successor in units(rows, 'Before'):
            graph[successor].add(name)
    try:
        TopologicalSorter(graph).prepare()
    except CycleError as problem:
        raise ValueError('ORDER_CYCLE') from problem
    return graph


def validate(configurations):
    by_name = {name: parse(raw) for name, raw in configurations.items()}
    require(set(by_name) == {*DECLARED, TARGET, STOP, *OPTIONAL}, 'C02_INVENTORY')
    graph = order_graph(by_name)
    for unit, expect in DECLARED.items():
        row = by_name[unit]
        require(tuple(one(row, 'Service', k) for k in KEYS) == expect, 'TYPE_TIME_EXIT_POLICY')
        require(one(row, 'Service', 'SendSIGKILL') == 'no', 'SIGKILL_POLICY')
    for unit in (API, WEB, ART):
        row = by_name[unit]
        require((one(row, 'Unit', 'StartLimitIntervalSec'), one(row, 'Unit', 'StartLimitBurst'),
                 one(row, 'Service', 'RestartSec')) == ('600', '5', '5s'), 'RESTART_BUDGET')
    for unit, predecessors in ORDER.items():
        require(units(by_name[unit], 'After') == predecessors, 'SIGNED_AFTER')
        require(units(by_name[unit], 'Requires') == REQUIRES[unit], 'SIGNED_REQUIRES')
    require(not units(by_name[MORNING], 'Before') and not units(by_name[TARGET], 'Wants'),
            'NO_PARALLEL_CHILD_ACTIVATION')
    require(one(by_name[TARGET], 'Install', 'WantedBy') == 'multi-user.target', 'TARGET_INSTALL')
    require(not units(by_name[INBOX], 'Conflicts'), 'INSPECTOR_NO_FORCED_STOP')
    require({ART, API, WEB, CADDY} == units(by_name[INBOX], 'Before'), 'INSPECTOR_AFTERCARE_ORDER')
    stop = by_name[STOP]
    require(set(stop) == {('Service', 'TimeoutStopSec'), ('Service', 'SendSIGKILL')}, 'STOP_ONLY')
    require((one(stop, 'Service', 'TimeoutStopSec'), one(stop, 'Service', 'SendSIGKILL')) ==
            ('30s', 'no'), 'CADDY_STOP_INTACT')
    for optional in OPTIONAL:
        row = by_name[optional]
        require(set(row) == {('Service', 'LoadCredential')}, 'OPTIONAL_PROFILE_SCOPE')
        require(bool(one(row, 'Service', 'LoadCredential')), 'OPTIONAL_SINGLE_DECLARATION')
    return sum(len(predecessors) for predecessors in graph.values()), len(graph)


def mutate(original, file, old, replacement):
    raw = original[file]
    assert raw.count(old) == 1
    return original | {file: raw.replace(old, replacement)}


def exercise_negatives(value):
    checks = (
        ('PT-C02-TEXT-002', API, b'\nTimeoutStartSec=120s\n', b'\nTimeoutStartSec=121s\n', 'TYPE_TIME_EXIT_POLICY'),
        ('PT-C02-TEXT-003', EXPIRY, b'\nSuccessExitStatus=10\n', b'\nSuccessExitStatus=143\n', 'TYPE_TIME_EXIT_POLICY'),
        ('PT-C02-TEXT-004', ART, b'\nSendSIGKILL=no\n', b'\nSendSIGKILL=yes\n', 'SIGKILL_POLICY'),
        ('PT-C02-TEXT-005', TARGET, b'\nAfter=' + MORNING.encode() + b'\n',
         b'\nAfter=' + MORNING.encode() + b'\nWants=' + BACKUP.encode() + b'\n', 'NO_PARALLEL_CHILD_ACTIVATION'),
        ('PT-C02-TEXT-006', API, b'\nRequires=artemis.service postgresql.service\n',
         b'\nRequires=postgresql.service\n', 'SIGNED_REQUIRES'),
        ('PT-C02-TEXT-007', ART, b'\nAfter=' + CLEANUP.encode() + b'\n',
         b'\nAfter=' + CLEANUP.encode() + b' ' + API.encode() + b'\n', 'ORDER_CYCLE'),
        ('PT-C02-TEXT-008', WEB, b'\nRestartSec=5s\n', b'\nRestartSec=5s\nRestartSec=9s\n', 'REPEATED_DIRECTIVE'),
        ('PT-C02-TEXT-009', STOP, b'\nSendSIGKILL=no\n',
         b'\nSendSIGKILL=no\nTimeoutStartSec=30s\n', 'STOP_ONLY'),
    )
    passed = []
    for ident, file, old, replacement, expected in checks:
        try:
            validate(mutate(value, file, old, replacement))
        except ValueError as result:
            assert str(result) == expected, (ident, str(result))
        else:
            raise AssertionError(ident + ' was not rejected')
        passed.append(dict(testId=ident, unit=file, expected=expected, actual=expected, passed=True))
    return passed


def main():
    start = read(next(D.glob('594_C02*.json')))
    v = start['values']
    assert git('rev-parse', 'HEAD').decode().strip() == v['source']
    pins = v['oracleReferences']
    assert all(ref(row['path']) == row for row in pins)
    handoff, historic, registry = (read(row['path']) for row in pins)
    assert handoff['c02']['currentTemplates'] == 14 and handoff['c02']['actualUnit'] is False
    assert historic['actualExit'] == 0 and historic['effectiveBaseUnitNotVerified']
    canonical = git('rev-parse', 'origin/main').decode().strip()
    design = git('show', f'{canonical}:{SS}')
    assert all(fragment.encode() in design for fragment in (
        'SSC107/BUG322', 'SSC127/BUG375', 'SSC178内部配備補足', 'RestartSec=5s',
        'Start limit | interval 600s, burst 5', 'TimeoutStartSec=30min/TimeoutStopSec=60s',
        '`schubert-nk-morning.target`は親MorningだけをRequires/After'))
    owned = sorted(row['path'] for row in registry['artifacts'] if row.get('owner') == 'WBS-C02')
    assert len(owned) == 14
    core = v['productionCoreMain']
    rows, data = [], {}
    for path in owned:
        rel = Path(path).relative_to(ROOT).as_posix()
        name = rel.removesuffix('.template')
        payload = git('show', f'{core}:{path}')
        assert payload == git('show', f"{v['source']}:{path}") == Path(path).read_bytes()
        data[name] = payload
        rows.append(dict(path=path, source=core, sha256=sha(payload)))
    edges, nodes = validate(data)
    fixtures = [dict(testId='PT-C02-TEXT-001', passed=True, configurations=14, orderEdges=edges, graphNodes=nodes)]
    fixtures.extend(exercise_negatives(data))
    summary = dict(actualExit=0, sourceCore=core, head=v['source'], currentFiles=rows, fixedOrderEdges=edges,
        graphNodes=nodes, canonical=dict(path=str(SS), source=canonical, sha256=sha(design)),
        tests=fixtures, sourceOnly=True, returnedUnitEvidence=False, currentHostObservation=False,
        caddyWebEffectiveAfterRequires='Unverified in base Unit; source drop-ins are Service-only',
        inspectorOwnerAndTerminalAccepted=False, systemdOrRuntimeInvocations=0, productTests=0,
        wholeC02Accepted=False, whole451Accepted=False, newAcceptance=0, references=pins,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    output = E / v['run']
    output.mkdir()
    file = output / 'manifest.json'
    file.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(ref(file), edges, len(fixtures))


if __name__ == '__main__':
    main()
