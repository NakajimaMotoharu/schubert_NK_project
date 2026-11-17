"""Recover PG38180 from original Maven outputs and the exact frozen snapshot."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import subprocess

EVIDENCE = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RUN = EVIDENCE / 'PG38180-wbs66-current-four-main-v1'
OUT = EVIDENCE / 'PG38182-wbs66-current-four-main-independent-v1'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_bytes())

begin = load(RUN / 'begin.safe.json')
failure = load(RUN / 'wrapper-failure.safe.json')
prior_path = EVIDENCE / 'PG37656-ssc452-grammar-callers-v2/manifest.json'
assert sha(prior_path) == begin['baselineManifestSha256']
prior = load(prior_path)
snapshot = Path(begin['cwd'])
expected = begin['mainCounts']
for name, pin in begin['sourceInputs'].items():
    raw = subprocess.check_output(['git', 'show', f"{begin['sourceCore']}:{name}"])
    assert hashlib.sha256(raw).hexdigest() == sha(name) == sha(snapshot / name) == pin, name
maven = (RUN / 'maven.stdout.log').read_text()
assert maven.count('[INFO] BUILD SUCCESS') == 1 and '[ERROR]' not in maven
assert len(re.findall(r'^\[INFO\] .* SUCCESS \[', maven, re.M)) == 5
goals = {}
prefixes = {
    'enforcer': 'enforcer:3.6.3:enforce',
    'spotless': 'spotless:3.10.2:check',
}
for gate, prefix in prefixes.items():
    goals[gate] = re.findall(rf'^\[INFO\] --- {re.escape(prefix)} .* @ (schubert-nk[a-z-]*) ---$', maven, re.M)
    assert len(set(goals[gate])) == 5, (gate, goals[gate])
assert maven.count('DependencyConvergence passed') == 5
assert [int(v) for v in re.findall(r'Compiling (\d+) source files with javac', maven)] == list(expected.values())
assert not list(snapshot.glob('src/*/target/test-classes'))
assert not list(snapshot.glob('src/*/target/surefire-reports'))
for module in ('api','web'):
    assert not (snapshot / f'src/schubert-nk-{module}/target').exists()

scoped = {'bootstrap': 'PG38076-jdbc-pure-admission-v1', 'batch': 'PG38056-unit-state-pure-admission-v1'}
rows = {}
for module, old in prior['physicalClassHashes'].items():
    base = snapshot / f'src/schubert-nk-{module}/target/classes'
    current = {p.relative_to(base).as_posix(): sha(p) for p in sorted(base.rglob('*.class'))}
    assert current.keys() == old.keys()
    changes = [k for k,h in current.items() if h != old[k]]
    scope_ref = None
    if module in scoped:
        scope_ref = EVIDENCE / scoped[module] / 'normalized-prepare.json'
        scope = load(scope_ref)
        assert len(changes) == 1 and scope['physicalClassHashes'][changes[0]] == current[changes[0]]
        assert len([n for n in begin['changedSources'] if '/schubert-nk-'+module+'/' in n]) == 1
    else:
        assert changes == []
    rows[module] = dict(mainSources=expected[module], classCount=len(current), deltas=changes, classHashes=current,
                        scopedPriorProof=dict(path=str(scope_ref), sha256=sha(scope_ref)) if scope_ref else None)
value = dict(
    actualExit=0, run=begin['run'], source=begin['sourceCore'], groupStart=begin['startEvent'],
    terminalAtUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
    buildObservedState='MAVEN_BUILD_SUCCESS_LOG_AND_ALL_FOUR_CLASS_INVENTORIES_VERIFIED',
    mavenNumericExit=None, initialWrapperExit=failure['wrapperExit'], repeatBuilds=0,
    independentChecks={'inputHashes':len(begin['sourceInputs']), 'reactorSuccesses':5, 'modules':4},
    gateExecutions=goals, dependencyConvergencePassLines=5, rows=rows,
    actualProductTests=0, heldClassfilesGenerated=0, formalAcceptanceDelta=0,
    evidence={str(p):sha(p) for p in RUN.iterdir() if p.is_file()}
)
OUT.mkdir()
(OUT / 'manifest.json').write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, classes={k:v['classCount'] for k,v in rows.items()},
                      changed={k:v['deltas'] for k,v in rows.items()})))
