"""Original Maven Main-only Storage compile: no test/native/application operation."""
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
w = r.parent / 'pgpt-runs/PG379/pg36820-storage-main-compile-v1'
out = b / 'evidence/PG36820-storage-main-compile-v1'
core = '7123bb3bc8319cfadea41e5be38a75e825e5c14c'
group = 'PGPT-WBS66-F03-STORAGE-MAIN-20261117'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ref = lambda p: dict(path=str(p.relative_to(r)), sha256=sha(p))
assert not out.exists() and not w.exists()
previous = json.loads((d / '022_F03六module静的群開始.json').read_text())
q = json.loads(Path(sys.argv[1]).read_text())
scope = ('Existing unfinished F03/2-2 remaining2.4, not additional price. Storage all25 '
 'Main-only original Maven compile and full PMD/SpotBugs with original rules. No Test sources '
 'or Test execution, no app initialization/entrypoint/native/DB/VM/service/authority changes. '
 'Four QA056 held types are absent, not compiled/read. Existing closed PT runner untouched. '
 'Compiling FFM declarations is not invoking native bindings; no product class is initialized. '
 'Normal Maven compile is needed because four Storage Main inputs changed from old15276, '
 'and the current complete25 module has not been certified by recent closed component proofs.')
values = dict(build_context(group_id=group, category='CONTRACT_AUDIT',
    kind='SOURCE_REQUALIFICATION', scope=scope,
    oracle_refs=[ref(b / '4451_F03六module現在source静的ゲート仕様.md'),
                 ref(b / 'evidence/PG36814-six-main-maven-validate-independent-v1/manifest.json')]),
    source=core, wbsLeafIds=['WBS-F03'], managementWorkIds=['WBS-F03/2-2'],
    estimateAtGroupStartPp=previous['values']['estimateAtGroupStartPp'],
    groupCapPp=5, completedOriginalRowPricePp=0,
    sameExistingUnfinishedPriceNotAdditional=True, newAcceptance=0,
    nextCommand='Compile Storage25 Main only; collect terminal and full static scope, classify all raw findings before qualification.')
event = append_start(group, values, sys.argv[1], digest(q),
                     datetime.datetime.now(datetime.timezone.utc).isoformat())
start_record = d / '033_F03Storage全25Main群開始.json'
start_record.open('x').write(json.dumps(dict(actualExit=0, eventId=event,
    groupId=group, values=values, quota=q), ensure_ascii=False, indent=2) + '\n')
w.mkdir(); out.mkdir(); snapshot = w / 'snapshot'; snapshot.mkdir()
modules = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
paths = ['pom.xml', 'program/characterization/pom.xml']
paths.extend('src/schubert-nk-' + m + '/pom.xml' for m in modules)
main = sorted((r / 'src/schubert-nk-storage/src/main/java').rglob('*.java'))
assert len(main) == 25
paths.extend(str(p.relative_to(r)) for p in main)
assert not any(any(x in p for x in ['TemporaryInfrastructureException',
    'FingerprintKeyRing', 'ResponseSnapshotCodec', 'WebStartupException',
    'RootFailedStart', 'SnapshotKeyCloseWitness', 'pg9892_snapshot']) for p in paths)
pins = {}
for name in paths:
    raw = (r / name).read_bytes()
    assert subprocess.check_output(['git', 'show', core + ':' + name]) == raw
    target = snapshot / name; target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw); pins[name] = sha(r / name)
assert not list(snapshot.rglob('*.class'))
assert not any('/src/test/' in str(p) for p in snapshot.rglob('*'))
tc = r.parent / 'toolchain'
command = [str(tc / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
           '-o', '-B', '-ntp', '-Dmaven.repo.local=' + str(tc / 'm2/repository'),
           '-pl', 'src/schubert-nk-storage', '-am', 'compile']
env = {'PATH': str(tc / 'jdk-25.0.4/bin') + ':/usr/bin:/bin',
       'JAVA_HOME': str(tc / 'jdk-25.0.4'), 'HOME': os.environ['HOME'], 'LANG': 'C.UTF-8'}
begin = dict(sourceCore=core, groupId=group, eventId=event, inputHashes=pins,
    command=command, cwd=str(snapshot), mainCount=25,
    startAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    noTestSources=True, qa056HeldClassfilesAbsent=True)
(out / 'begin.safe.json').open('x').write(json.dumps(begin, indent=2) + '\n')
with (out / 'maven.stdout.log').open('xb') as stdout, (out / 'maven.stderr.log').open('xb') as stderr:
    try:
        result = subprocess.run(command, cwd=snapshot, env=env, stdout=stdout,
                                stderr=stderr, timeout=180)
        exit_code = result.returncode; timed_out = False
    except subprocess.TimeoutExpired:
        exit_code = 124; timed_out = True
assert all(sha(r / p) == h == sha(snapshot / p) for p, h in pins.items())
assert not list(snapshot.rglob('surefire-reports'))
classes = {str(p.relative_to(snapshot / 'src/schubert-nk-storage/target/classes')): sha(p)
    for p in sorted((snapshot / 'src/schubert-nk-storage/target/classes').rglob('*.class'))}
assert not any('/src/test/' in str(p) for p in snapshot.rglob('*'))
manifest = dict(begin, actualExit=exit_code, timedOut=timed_out,
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    physicalClassHashes=classes, productTestsExecuted=0,
    productClassesInitialized=0, actualNativeDbVmServiceActions=0,
    heldClassfileActions=0, formalUpdated=False, newAcceptance=0,
    logs=[ref(out / 'maven.stdout.log'), ref(out / 'maven.stderr.log')])
(out / 'manifest.json').open('x').write(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(dict(actualExit=exit_code, timedOut=timed_out,
    mainSources=25, physicalClasses=len(classes), event=event)))
sys.exit(exit_code)
