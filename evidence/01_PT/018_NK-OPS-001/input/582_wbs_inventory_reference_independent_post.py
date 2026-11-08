"""Narrow independent byte-reference check and tool-only malformed-metadata cases."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = B / 'evidence/PG23930-wbs-reference-repair-v1'
O = B / 'evidence/PG23932-wbs-reference-independent-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists()
    m = load(P / 'manifest.json')
    assert m['actualExit'] == 0 and m['changedAcceptanceFields'] == ['inventorySha256']
    before_ref = R / m['beforeManifest']['path']
    assert sha(before_ref) == m['beforeManifest']['sha256']
    before = load(before_ref)
    ipath = R / before['inventory']['path']
    apath = R / before['acceptance']['path']
    inventory = ipath.read_bytes()
    acceptance = apath.read_bytes()
    assert sha(ipath) == m['inventoryAfterSha256'] == before['inventory']['sha256']
    assert sha(apath) == m['acceptanceAfterSha256']
    old_acceptance = subprocess.check_output(['git', 'show', 'HEAD:' + before['acceptance']['path']], cwd=R)
    assert hashlib.sha256(old_acceptance).hexdigest() == before['acceptance']['sha256']
    old = json.loads(old_acceptance)
    new = json.loads(acceptance)
    assert old['inventorySha256'] != new['inventorySha256'] == hashlib.sha256(inventory).hexdigest()
    changed = dict(new)
    changed['inventorySha256'] = old['inventorySha256']
    assert changed == old
    expected = ('"inventorySha256": "' + new['inventorySha256'] + '"').encode()
    previous = ('"inventorySha256": "' + old['inventorySha256'] + '"').encode()
    assert acceptance.count(expected) == 1 and acceptance.replace(expected, previous, 1) == old_acceptance
    gp = R / m['guard']['path']
    assert sha(gp) == m['guard']['sha256']
    spec = importlib.util.spec_from_file_location('wbs_reference_guard_definition_only', gp)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    assert guard.verify_files(R)['bindingValid'] is True
    fixture = b'{"fixture":"tool-only-public-metadata"}\n'
    digest = hashlib.sha256(fixture).hexdigest()
    encoded = lambda value: json.dumps(value).encode()
    assert guard.validate_bytes(fixture, encoded(dict(inventorySha256=digest)))['bindingValid'] is True
    negatives = []
    bad = [None, False, 0, [], {}, digest.upper(), digest[:-1], 'g' * 64, '0' * 64]
    for i, value in enumerate(bad):
        try:
            guard.validate_bytes(fixture, encoded(dict(inventorySha256=value)))
        except ValueError:
            negatives.append('bad-pin-' + str(i))
        else:
            raise AssertionError('invalid pin accepted')
    vectors = [('missing-pin', fixture, b'{}'), ('nonobject-inventory', b'[]', encoded(dict(inventorySha256=hashlib.sha256(b'[]').hexdigest()))),
               ('nonobject-acceptance', fixture, b'[]'), ('malformed-json', b'{', b'{}'),
               ('duplicate-pin', fixture, ('{"inventorySha256":"' + digest + '","inventorySha256":"' + digest + '"}').encode()),
               ('duplicate-inventory-key', b'{"x":1,"x":1}', b'{}'),
               ('stale-original', inventory, old_acceptance),
               ('changed-inventory', inventory + b'\n', acceptance)]
    for name, inv, acc in vectors:
        try:
            guard.validate_bytes(inv, acc)
        except ValueError:
            negatives.append(name)
        else:
            raise AssertionError('invalid WBS reference accepted: ' + name)
    pub = R.parent / 'pgpt-runs/PG379/publish_characterization_delta.py'
    assert sha(pub) == m['privatePublisherAfterSha256']
    text = pub.read_text()
    patch = (P / 'publisher-attachment.patch.txt').read_text().rstrip('\n')
    assert patch in text
    guard_call = text.index("reference_guard['verify_files'](root)")
    assert guard_call < text.index('for name in names:') < text.index("['git','add'")
    assert guard.INVENTORY in patch and guard.ACCEPTANCE in patch
    assert sha(ipath) == m['inventoryAfterSha256'] and sha(apath) == m['acceptanceAfterSha256']
    O.mkdir()
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=m['source'],
                  producerManifest=dict(path=str((P / 'manifest.json').relative_to(R)), sha256=sha(P / 'manifest.json')),
                  changedAcceptanceFields=['inventorySha256'], inventoryBytesUnchanged=True,
                  otherAcceptanceValuesUnchanged=True, inverseAcceptanceBytesExact=True,
                  oldStalePairRejected=True, fixedCurrentPairAccepted=True,
                  metadataNegatives=negatives, publisherGuardBeforeFileScanAndStage=True,
                  productionSourceOrTestsChanged=False, productTestsExecuted=0, compilerOrJvmExecuted=False,
                  actualBackendActions=0, newAcceptance=0, formalUpdated=False, effortRate=None,
                  wholeTraceAccepted=False, fullWbsAuditRerun=False,
                  tool=dict(path=str(Path(__file__).relative_to(R)), sha256=sha(Path(__file__))))
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, metadataNegativeChecks=len(negatives), manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
