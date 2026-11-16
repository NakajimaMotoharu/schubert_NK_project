"""Actual original-POM validate on frozen Main only; never compile, Test, app or native."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys

r = Path.cwd()
sys.path[:0] = [str(r / 'tools/quality'), str(r / 'tools/quality/vm/050_s1')]
from pmo_group_context import build_context
from pmo_quota_binding import append_start, digest

b = r / 'evidence/01_PT/018_NK-OPS-001'
d = r / 'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
w = r.parent / 'pgpt-runs/PG379/pg36812-six-main-maven-validate-v1'
out = b / 'evidence/PG36812-six-main-maven-validate-v1'
core = '7123bb3bc8319cfadea41e5be38a75e825e5c14c'
group = 'PGPT-WBS66-F03-MAIN-MAVEN-VALIDATE-20261117'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ref = lambda p: dict(path=str(p.relative_to(r)), sha256=sha(p))
assert not out.exists() and not w.exists(), 'immutable new run only'
previous = json.loads((d / '022_F03六module静的群開始.json').read_text())
q = json.loads(Path(sys.argv[1]).read_text())
scope = ('Resume existing F03/2-2 remaining2.4, no new price. Original Maven validate '
         'for all1022 Main in six modules in a fresh snapshot with no Test sources, '
         'no classfiles/application initialization/entrypoint/DB/native. Root enforcer '
         'and normal Spotless only, no skips or alternate format policy. QA056 remains '
         'pending for four-classfile operations. Failure is a failure, never PT PASS.')
values = dict(build_context(group_id=group, category='CONTRACT_AUDIT',
    kind='SOURCE_REQUALIFICATION', scope=scope,
    oracle_refs=[ref(b / '4451_F03六module現在source静的ゲート仕様.md')]),
    source=core, wbsLeafIds=['WBS-F03'], managementWorkIds=['WBS-F03/2-2'],
    estimateAtGroupStartPp=previous['values']['estimateAtGroupStartPp'],
    groupCapPp=5, completedOriginalRowPricePp=0,
    sameExistingUnfinishedPriceNotAdditional=True, newAcceptance=0,
    nextCommand='Original Maven validate only, collect actual terminal and independently verify no classes/tests.')
event = append_start(group, values, sys.argv[1], digest(q),
                     datetime.datetime.now(datetime.timezone.utc).isoformat())
(d / '031_F03正式MavenMainvalidate開始.json').open('x').write(json.dumps(
    dict(actualExit=0, eventId=event, groupId=group, values=values, quota=q),
    ensure_ascii=False, indent=2) + '\n')
w.mkdir(); out.mkdir()
snapshot = w / 'snapshot'; snapshot.mkdir()
modules = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
expected = dict(zip(modules, [165, 25, 87, 283, 262, 200]))
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
    modules=6, mainSources=1022, classfilesGenerated=0, event=event)))
sys.exit(exit_code)
