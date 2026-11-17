"""Actual original-POM validate on frozen Main only; never compile, Test, app or native."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys
import shutil

r = Path.cwd()
b = r / 'evidence/01_PT/018_NK-OPS-001'
d = r / 'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
w = r.parent / 'pgpt-runs/PG379/pg38184-wbs66-current-six-validate-v1'
out = b / 'evidence/PG38184-wbs66-current-six-validate-v1'
start_record = json.loads((d / '176_WBS66六module現行validate着手.json').read_text())
core = start_record['productionCore']
group = start_record['groupId']
event = start_record['eventId']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ref = lambda p: dict(path=str(p.relative_to(r)), sha256=sha(p))
assert not out.exists() and not w.exists(), 'immutable new run only'
assert shutil.disk_usage(r).free >= 1024**3
w.mkdir(); out.mkdir()
snapshot = w / 'snapshot'; snapshot.mkdir()
modules = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
expected = dict(zip(modules, [169, 25, 87, 283, 262, 200]))
pins = {}; counts = {}
paths = ['pom.xml', 'program/characterization/pom.xml']
for module in modules:
    base = 'src/schubert-nk-' + module
    sources = sorted((r / base / 'src/main/java').rglob('*.java'))
    counts[module] = len(sources)
    paths.append(base + '/pom.xml')
    paths.extend(str(p.relative_to(r)) for p in sources)
assert counts == expected
for name in paths:
    p = r / name
    raw = p.read_bytes()
    assert subprocess.check_output(['git', 'show', core + ':' + name]) == raw
    target = snapshot / name; target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw); pins[name] = sha(p)
assert not list(snapshot.rglob('*.class'))
assert not any('/src/test/' in str(p) for p in snapshot.rglob('*'))
tc = r.parent / 'toolchain'
command = [str(tc / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
           '-o', '-B', '-ntp', '-Dmaven.repo.local=' + str(tc / 'm2/repository'),
           '-pl', ','.join('src/schubert-nk-' + m for m in modules), '-am', 'validate']
env = {'PATH': str(tc / 'jdk-25.0.4/bin') + ':/usr/bin:/bin',
       'JAVA_HOME': str(tc / 'jdk-25.0.4'), 'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8'}
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
begin = dict(sourceCore=core, groupId=group, eventId=event, counts=counts,
    inputHashes=pins, command=command, cwd=str(snapshot), startAtUTC=start,
    noTestSources=True, noClassfilesBefore=True, qa056Unchanged=True)
(out / 'begin.safe.json').open('x').write(json.dumps(begin, indent=2) + '\n')
with (out / 'maven.stdout.log').open('xb') as stdout, (out / 'maven.stderr.log').open('xb') as stderr:
    try:
        result = subprocess.run(command, cwd=snapshot, env=env, stdout=stdout,
                                stderr=stderr, timeout=180)
        exit_code = result.returncode; timed_out = False
    except subprocess.TimeoutExpired:
        exit_code = 124; timed_out = True
terminal = datetime.datetime.now(datetime.timezone.utc).isoformat()
(out / 'maven-process-exit.safe.json').open('x').write(json.dumps(
    dict(actualExit=exit_code, timedOut=timed_out, observedAtUTC=terminal), indent=2) + '\n')

assert all(sha(r / p) == h == sha(snapshot / p) for p, h in pins.items())
classes = list(snapshot.rglob('*.class')); assert not classes
assert not list(snapshot.rglob('surefire-reports'))
manifest = dict(begin, actualExit=exit_code, timedOut=timed_out, terminalAtUTC=terminal,
    classfilesGenerated=0, productTestsExecuted=0, actualDbNativeVmServiceActions=0,
    formalUpdated=False, newAcceptance=0, completedOriginalRowPricePp=0,
    logs=[ref(out / 'maven.stdout.log'), ref(out / 'maven.stderr.log')],
    heldClassfileActions=0, wholeF03Accepted=False)
(out / 'manifest.json').open('x').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=exit_code, timedOut=timed_out, sourceCore=core,
    modules=6, mainSources=1026, classfilesGenerated=0, event=event)))
sys.exit(exit_code)
