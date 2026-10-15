"""Read-only extraction of already completed PG3274 protocol test witnesses.

No Maven, VM, business operation, or new test credit. XML properties/stdout are
not exported. Current tests must equal the fixed actually executed snapshot.
"""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

import lan_server
from pg3274_header_group_full_six import ROOT, SOURCE, W

PUBLIC = Path('evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG3284-canonical-acceptance')
FULL = W / 'pg3276-header-group-full-qualified-v1/manifest.safe.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def project_suite(root, sha):
    require(root.tag == 'testsuite', 'one real JUnit suite required')
    counts = {k: int(root.get(k, '0')) for k in ('tests', 'failures', 'errors', 'skipped')}
    cases = root.findall('testcase')
    require(counts['tests'] == len(cases) > 0 and all(counts[k] == 0 for k in ('failures', 'errors', 'skipped')),
            'complete successful suite required')
    require(not root.findall('.//failure') and not root.findall('.//error')
            and not root.findall('.//skipped') and not root.findall('.//flakyFailure')
            and not root.findall('.//rerunFailure'), 'no failed/skipped/flaky test credit')
    names = [case.attrib['name'] for case in cases]
    require(len(names) == len(set(names)) and all(case.get('classname') == root.get('name') for case in cases),
            'unique named cases of exact suite required')
    return {'class': root.attrib['name'], 'tests': names, 'counts': counts, 'xmlSha256': sha}


def server_source(full):
    # Execute this exact independent parser remotely without transporting secrets.
    import inspect
    parser = inspect.getsource(require) + '\n' + inspect.getsource(project_suite)
    return '''import hashlib,json,pathlib,xml.etree.ElementTree as ET
''' + parser + '''
B=pathlib.Path('/home/mini/schubert-nk-pgpt')
M=B/'runs/PG3274-six-v1/manifest.safe.json'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
require(sha(M)==EXPECTED_MANIFEST, 'fixed successful original whole run manifest required')
v=json.loads(M.read_bytes())
require(v['actualExit']==v['mavenExit']==0 and v['issues']==[] and v['sourceInputsUnchanged'] is True and v['productionSource']==SOURCE and v['sourceSnapshotHead']==SNAPSHOT, 'original whole exit/source required')
S=B/'source-full-PG3274'
T=S/'src/schubert-nk-protocol/target'
static=T/'spotbugsXml.xml'
require(sha(static)==EXPECTED_STATIC and not ET.parse(static).getroot().findall('.//BugInstance'), 'original static XML hash and zero issues required')
suites=[project_suite(ET.parse(p).getroot(),sha(p)) for p in sorted((T/'surefire-reports').glob('TEST-*.xml'))]
require(len(suites)==17 and sum(s['counts']['tests'] for s in suites)==84, 'actual protocol84/17 required')
sources={str(p.relative_to(S)):sha(p) for p in sorted((S/'src/schubert-nk-protocol/src/test').rglob('*')) if p.is_file()}
print(json.dumps({'actualExit':0,'productionSource':SOURCE,'run':'PG3274-six-v1','sourceSnapshot':SNAPSHOT,'originalWholeManifestSha256':sha(M),'staticXmlSha256':sha(static),'staticIssues':0,'suites':suites,'testSourceHashes':sources,'propertiesExported':False,'testsReissued':0,'vmActions':0}))
'''.replace('EXPECTED_MANIFEST', repr(full['serverManifestSha256'])).replace('EXPECTED_STATIC', repr(full['qualificationInputs']['protocol']['static'])).replace('SOURCE', repr(SOURCE)).replace('SNAPSHOT', repr(full['sourceSnapshot']))


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean witness tool required')
    receipt = json.loads(FULL.read_bytes()); full = receipt['result']
    require(receipt['actualExit'] == full['actualExit'] == full['FESFlakyNotRun'] == 0
            and full['productionSource'] == SOURCE and full['tests'] == 3701, 'qualified completed whole3701 required')
    code = server_source(full)
    rc, output = lan_server.run('python3 -c ' + shlex.quote(code), timeout=120)
    require(rc == 0, 'read-only original XML witness extraction must succeed')
    value = json.loads(output)
    require(value['productionSource'] == SOURCE and value['sourceSnapshot'] == full['sourceSnapshot'], 'exact actual test snapshot required')
    for name, digest in value['testSourceHashes'].items():
        current = (ROOT / name).read_bytes()
        fixed = subprocess.check_output(['git', 'show', full['sourceSnapshot'] + ':' + name], cwd=ROOT)
        require(hashlib.sha256(current).hexdigest() == digest == hashlib.sha256(fixed).hexdigest(), 'current/fixed/actually executed Test byte must match')
    value.update(fullPrivateReceiptSha256=hashlib.sha256(FULL.read_bytes()).hexdigest(),
                 toolSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), formalAccepted=False,
                 acceptedLeafDelta=0, independentCanonicalManifestSha256=hashlib.sha256((W / 'pg3284-protocol-canonical-fixtures-v2/manifest.safe.json').read_bytes()).hexdigest())
    target = ROOT / PUBLIC
    target.mkdir(parents=True, exist_ok=False)
    # Both reports contain only explicit source IDs, hashes, test names/counters.
    with (target / 'test-witness.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    canonical = json.loads((W / 'pg3284-protocol-canonical-fixtures-v2/manifest.safe.json').read_bytes())
    with (target / 'canonical-fixtures.json').open('x') as stream:
        json.dump(canonical, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'actualExit': 0, 'suites': len(value['suites']), 'tests': sum(len(s['tests']) for s in value['suites']), 'public': str(PUBLIC), 'newPtCredit': 0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
