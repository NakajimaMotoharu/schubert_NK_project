"""Verify current original-Maven validation and SS311 declared production module edges."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

EVIDENCE = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RUN = EVIDENCE / 'PG38184-wbs66-current-six-validate-v1'
OUT = EVIDENCE / 'PG38186-wbs66-current-six-validate-independent-v1'
NS = {'m':'http://maven.apache.org/POM/4.0.0'}
GROUP = 'dev.codex.schubert'
EXPECTED = {
    'protocol': set(), 'storage': set(), 'bootstrap': {'storage'},
    'api': {'protocol', 'storage', 'bootstrap'}, 'web': {'protocol', 'storage', 'bootstrap'},
    'batch': {'storage', 'bootstrap'},
}
EXPECTED_TEST = {
    'protocol': set(), 'storage': set(), 'bootstrap': set(),
    'api': {('bootstrap','test-jar')},
    'web': {('bootstrap','test-jar'),('api','jar')},
    'batch': {('bootstrap','test-jar')},
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_bytes())

m = load(RUN/'manifest.json')
end = load(RUN/'maven-process-exit.safe.json')
assert end['actualExit'] == m['actualExit'] == 0 and not end['timedOut'] and not m['timedOut']
assert m['terminalAtUTC'] == end['observedAtUTC']
snapshot = Path(m['cwd'])
assert sum(m['counts'].values()) == 1026
assert all(sha(name)==sha(snapshot/name)==pin for name,pin in m['inputHashes'].items())
assert all(sha(row['path'])==row['sha256'] for row in m['logs'])
assert not list(snapshot.rglob('*.class')) and not list(snapshot.rglob('surefire-reports'))
stdout = (RUN/'maven.stdout.log').read_text()
assert stdout.count('[INFO] BUILD SUCCESS') == 1
modules = {'schubert-nk'} | {f'schubert-nk-{k}' for k in EXPECTED}
gates = {}
for name, goal in [('enforcer','enforcer:3.6.3:enforce'),('spotless','spotless:3.10.2:check')]:
    found = re.findall(rf'^\[INFO\] --- {re.escape(goal)} .* @ (schubert-nk[a-z-]*) ---$',stdout,re.M)
    assert len(found) == len(modules) and set(found) == modules
    gates[name] = found
assert stdout.count('DependencyConvergence passed') == len(modules)
assert not re.search(r'^\[INFO\] --- (?:compiler|surefire|failsafe):',stdout,re.M)
root = ET.parse(snapshot/'pom.xml')
assert root.findtext('m:properties/m:maven.compiler.release',namespaces=NS) == '25'
children = [n.text for n in root.findall('m:modules/m:module',NS)]
assert set(children) == {'program/characterization'}|{f'src/schubert-nk-{n}' for n in EXPECTED}
assert not root.findall('m:dependencies/m:dependency',NS) and root.find('m:profiles',NS) is None
rows = {}
for module, expected in EXPECTED.items():
    name = f'src/schubert-nk-{module}/pom.xml'
    pom = ET.parse(snapshot/name)
    tag = lambda field: pom.findtext(f'm:{field}',namespaces=NS)
    assert tag('artifactId') == f'schubert-nk-{module}' and pom.findtext('m:parent/m:artifactId',namespaces=NS) == 'schubert-nk'
    assert pom.find('m:profiles',NS) is None
    prod, test = set(), set()
    for d in pom.findall('m:dependencies/m:dependency',NS):
        get = lambda field,default=None:d.findtext(f'm:{field}',default=default,namespaces=NS)
        if get('groupId') == GROUP:
            art = get('artifactId')
            assert art.startswith('schubert-nk-') and art.removeprefix('schubert-nk-') in EXPECTED
            assert get('version') == '${project.version}'
            target,scope,kind = art.removeprefix('schubert-nk-'),get('scope','compile'),get('type','jar')
            if scope == 'test':
                test.add((target,kind))
            else:
                assert scope == 'compile' and kind == 'jar'
                prod.add(target)
    assert prod == expected and test == EXPECTED_TEST[module], (module,prod,test)
    rows[module] = dict(pomSha256=m['inputHashes'][name],productionEdges=sorted(prod),testEdges=sorted(test))
out = dict(actualExit=0,run='PG38184-WBS66-CURRENT-SIX-VALIDATE',source=m['sourceCore'],
           terminalAtUTC=dt.datetime.now(dt.timezone.utc).isoformat(),mainSources=1026,productModules=6,
           mavenNumericExit=end['actualExit'],gates=gates,declaredProductionAndTestGraph=rows,
           requirements=['SYS-002','SYS-005'],projectDeclaredBoundaryVerified=True,
           dependencyConvergencePassed=7,productClassfilesGenerated=0,productTestsExecuted=0,
           fullArchUnitBytecodeBoundaryVerified=False,newAcceptance=0,
           producer={'path':str(RUN/'manifest.json'),'sha256':sha(RUN/'manifest.json')})
OUT.mkdir()
(OUT/'manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['actualExit','productModules','mainSources','dependencyConvergencePassed','productClassfilesGenerated','projectDeclaredBoundaryVerified']}))
