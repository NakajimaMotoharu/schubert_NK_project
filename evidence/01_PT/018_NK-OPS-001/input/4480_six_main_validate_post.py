"""Independent read-only actual-terminal check, never invoke the Maven producer again."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

r = Path.cwd()
b = r / 'evidence/01_PT/018_NK-OPS-001/evidence'
p = b / 'PG36812-six-main-maven-validate-v1'
o = b / 'PG36814-six-main-maven-validate-independent-v1'
assert not o.exists()
m = json.loads((p / 'manifest.json').read_text())
assert m['actualExit'] == 0 and not m['timedOut']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for row in m['logs']:
    assert sha(r / row['path']) == row['sha256']
log = (p / 'maven.stdout.log').read_text()
assert '[INFO] BUILD SUCCESS' in log
assert log.count('--- spotless:3.10.2:check (java-format-contract)') == 7
assert log.count('DependencyConvergence passed') == 7
assert not any(x in log for x in ['--- compiler:', '--- surefire:', '[ERROR]'])
assert m['command'][-1] == 'validate'
assert not any('skip' in x for x in m['command'])
snapshot = Path(m['cwd'])
assert not list(snapshot.rglob('*.class'))
assert not list(snapshot.rglob('surefire-reports'))
actual = {str(p.relative_to(snapshot)) for p in snapshot.rglob('*.java')}
declared = {p for p in m['inputHashes'] if p.endswith('.java')}
assert actual == declared and len(actual) == 1022
for name, h in m['inputHashes'].items():
    assert sha(r / name) == h == sha(snapshot / name)
    assert hashlib.sha256(subprocess.check_output(
        ['git', 'show', m['sourceCore'] + ':' + name])).hexdigest() == h
o.mkdir()
result = dict(actualExit=0, source=m['sourceCore'],
    sourceDomain='CURRENT_MAIN_SOURCE_ONLY_MAVEN_VALIDATE_NOT_COMPILE_OR_PT',
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    producer=dict(path=str((p / 'manifest.json').relative_to(r)), sha256=sha(p / 'manifest.json')),
    mainSources=1022, modules=6, rootAndModuleSpotlessGates=7,
    dependencyConvergenceGates=7, sourceChanged=0, classfilesGenerated=0,
    productTestsExecuted=0, mainClassfilePhases='WAIT_QA056',
    wholeF03Accepted=False, formalUpdated=False, newAcceptance=0)
(o / 'manifest.json').open('x').write(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
