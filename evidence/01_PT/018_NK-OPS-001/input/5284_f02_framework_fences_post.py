"""Bind both ArchUnit audits and physical fixture inventories to the frozen SS311 source."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TOOL = 'tools/quality/architecture/ModuleDependencyAudit.java'
EXPECTED = {
    '013': ('bootstrap.SpringMessaging', 'org.springframework.jms.core.JmsTemplate'),
    '014': ('bootstrap.SpringHttp', 'org.springframework.web.client.RestClient'),
    '015': ('bootstrap.JdkHttp', 'java.net.http.HttpClient'),
    '016': ('bootstrap.JmsApi', 'jakarta.jms.Connection'),
    '017': ('api.ControllerAnnotation', 'org.springframework.web.bind.annotation.RestController'),
    '018': ('batch.ControllerAnnotation', 'org.springframework.web.bind.annotation.RestController'),
    '019': ('api.BrowserResponse', 'org.springframework.http.server.ServerHttpResponse'),
}
POSITIVE = frozenset({'020', '021', '022'})
PREFIX = 'dev.codex.schubert.nk.'


def git(*args):
    return subprocess.check_output(['git', *args], timeout=35)


def hash_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=hash_bytes(Path(path).read_bytes()))


def read(path):
    return json.loads(Path(path).read_bytes())


def findings(path):
    return {tuple(row.split('\t')[1:]) for row in path.read_text().splitlines() if row.startswith('FINDING\t')}


def main():
    preparation = E / 'PG40114-f02-framework-fences-before-v1'
    before = E / 'PG40115-f02-framework-fences-before-v2'
    after = E / 'PG40116-f02-framework-fences-after-v1'
    original, corrected = (read(d / 'manifest.json') for d in (before, after))
    assert original['source'] != corrected['source']
    assert original['canonical'] == corrected['canonical'] and original['designSha256'] == corrected['designSha256']
    assert corrected['source'] == git('rev-parse', 'HEAD').decode().strip()
    assert original['productionCoreMain'] == corrected['productionCoreMain']
    assert not git('diff', '--name-only', original['source'], corrected['source'], '--', 'src')
    assert original['artifacts'] == corrected['artifacts']
    assert len(corrected['artifacts']) == 6
    assert sum(map(len, corrected['artifacts'].values())) == 16
    assert all(n.startswith(PREFIX + module + '.') for module, nodes in corrected['artifacts'].items() for n in nodes)
    for folder, evidence, detected in ((before, original, {'016'}), (after, corrected, set(EXPECTED))):
        assert evidence['actualExit'] == 0 and evidence['childAuditExit'] == 1
        assert evidence['toolSha256'] == hash_bytes(git('show', f"{evidence['source']}:{TOOL}"))
        for name, run in evidence['receipts'].items():
            assert run == read(folder / (name + '-exit.json'))
            assert run['stdout'] == ref(run['stdout']['path']) and run['stderr'] == ref(run['stderr']['path'])
            assert run['actualExit'] == (1 if name == 'audit' else 0)
        by_id = {r['testId'].rsplit('-', 1)[1]: r for r in evidence['cases']}
        assert len(evidence['cases']) == 10 and by_id.keys() == set(EXPECTED) | POSITIVE
        assert all((r['origin'], r['target']) == (PREFIX + origin, target)
                   and r['expected'] is True and r['observed'] == (number in detected)
                   for number, (origin, target) in EXPECTED.items() for r in [by_id[number]])
        assert all(by_id[number]['expected'] is False and by_id[number]['observed'] is False for number in POSITIVE)
        assert findings(folder / 'audit.stdout.txt') == {
            ('FRAMEWORK_FENCES', PREFIX + EXPECTED[number][0], EXPECTED[number][1]) for number in detected
        }
    invalid = findings(preparation / 'audit.stdout.txt')
    assert sum(row[0] == 'MODULE_EDGES' for row in invalid) == 8
    assert sum(row[0] == 'FRAMEWORK_FENCES' for row in invalid) == 1
    assert read(preparation / 'audit-exit.json')['actualExit'] == 1
    manifest = dict(actualExit=0, source=corrected['source'], productionCoreMain=corrected['productionCoreMain'],
                    prepareAudit=ref(preparation / 'audit-exit.json'), prepareOutput=ref(preparation / 'audit.stdout.txt'),
                    prepareVerifierExit=1, prepareReason='Compile-only external stubs erroneously placed in Web JAR',
                    before=ref(before / 'manifest.json'), after=ref(after / 'manifest.json'),
                    beforeCorrect=4, afterCorrect=10, deniedOwners=7, legitimateOwners=3, physicalCanaryClasses=16,
                    productTests=0, productClassesLoaded=0, productJarsScanned=0, coverageMeasured=False,
                    fullF02Accepted=False, full451Accepted=False, newFormalAcceptance=0,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    folder = E / 'PG40118-f02-framework-fences-independent-v1'
    folder.mkdir()
    path = folder / 'manifest.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(ref(path))


if __name__ == '__main__':
    main()
