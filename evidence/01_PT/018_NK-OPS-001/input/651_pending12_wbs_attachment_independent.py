"""Verify the exact WBS metadata save; do not reinterpret the unchanged full audit HOLD."""
from pathlib import Path
import copy
import datetime
import hashlib
import json

B = Path('evidence/01_PT/018_NK-OPS-001')
BEFORE = B / 'evidence/PG24138-pending12-oracle-wbs-before-v1'
P = B / 'evidence/PG24150-pending12-oracle-wbs-attachment-v1'
O = B / 'evidence/PG24152-pending12-wbs-attachment-independent-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def validate(inventory, snapshot, old_i, old_s, key, reference):
    stripped = copy.deepcopy(inventory)
    overlay = stripped.pop(key)
    assert stripped == old_i
    restored = copy.deepcopy(snapshot)
    restored['inventorySha256'] = old_s['inventorySha256']
    assert restored == old_s
    assert overlay['independentManifest'] == reference
    for name, number in [('sourcePrograms', 12), ('physicalClasses', 17), ('knownMethodMetadata', 87),
                         ('measuredMethodRelations', 67), ('originalCompilerFilteredMethods', 8),
                         ('abstractNoCodeMethods', 12), ('originalUniqueCaseRefs', 96),
                         ('originalIndependentProofGroups', 10), ('reviewGroups', 7), ('assertionSnippetChecks', 254)]:
        assert type(overlay[name]) is int and overlay[name] == number
    for name in ['fullOracleOrScopeAcceptance', 'caseSpecificCoverageMeasured', 'originalExecOrCounterUnion',
                 'currentWholeSourceOrDependencyAcceptance', 'formalUpdated', 'wholeG13Accepted', 'whole451Accepted']:
        assert overlay[name] is False
    assert overlay['registeredComponentDelta'] is None and overlay['effortRate'] is None
    for name in ['productTestsExecuted', 'newTests', 'newAcceptance']:
        assert type(overlay[name]) is int and overlay[name] == 0


def main():
    assert not O.exists()
    manifest = load(P / 'manifest.json')
    assert manifest['actualExit'] == 0 and manifest['wbsPreAuditExit'] == manifest['wbsPostAuditExit'] == 1
    for name, pin in manifest['files'].items():
        assert sha(P / name) == pin
    c = load(B / 'input/645_pending12_method_oracle_seal_scope.json')
    ip, sp = Path(c['wbsInventory']), Path(c['wbsSnapshot'])
    assert ip.read_bytes() == (P / ip.name).read_bytes()
    assert sp.read_bytes() == (P / sp.name).read_bytes()
    assert load(sp)['inventorySha256'] == sha(ip) == manifest['inventoryAfterSha256']
    assert sha(sp) == manifest['snapshotAfterSha256']
    assert sha(BEFORE / ip.name) == manifest['inventoryBeforeSha256']
    assert sha(BEFORE / sp.name) == manifest['snapshotBeforeSha256']
    old_i, old_s = load(BEFORE / ip.name), load(BEFORE / sp.name)
    inventory, snapshot = load(ip), load(sp)
    reference = manifest['independentManifest']
    assert sha(Path(reference['path'])) == reference['sha256']
    validate(inventory, snapshot, old_i, old_s, c['overlayKey'], reference)
    negative = []
    for label, change in [
        ('old-source-change', lambda i, s: i.update(source='0' * 40)),
        ('old-snapshot-change', lambda i, s: s.update(source='0' * 40)),
        ('new-test-credit', lambda i, s: i[c['overlayKey']].update(newTests=96)),
        ('full-oracle-claim', lambda i, s: i[c['overlayKey']].update(fullOracleOrScopeAcceptance=True)),
        ('NoCode-measured', lambda i, s: i[c['overlayKey']].update(measuredMethodRelations=79)),
        ('case-doublecount', lambda i, s: i[c['overlayKey']].update(originalUniqueCaseRefs=98)),
        ('formal-claim', lambda i, s: i[c['overlayKey']].update(formalUpdated=True)),
        ('registry-credit', lambda i, s: i[c['overlayKey']].update(registeredComponentDelta=12)),
    ]:
        a, b = copy.deepcopy(inventory), copy.deepcopy(snapshot)
        change(a, b)
        try:
            validate(a, b, old_i, old_s, c['overlayKey'], reference)
        except AssertionError:
            negative.append(label)
        else:
            raise AssertionError(label)
    O.mkdir()
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  attachmentManifest={'path': str(P / 'manifest.json'), 'sha256': sha(P / 'manifest.json')},
                  inventoryBeforeSha256=sha(BEFORE / ip.name), inventoryAfterSha256=sha(ip),
                  snapshotBeforeSha256=sha(BEFORE / sp.name), snapshotAfterSha256=sha(sp),
                  addedOverlayOnly=True, snapshotChangedOnlyInventorySha256=True, referencePairCoherent=True,
                  metadataNegativeChecks=negative, wbsPreAuditExit=1, wbsPostAuditExit=1,
                  wholeWbsAccepted=False, boundedRelationCompletenessVerified=True, fullOracleOrScopeAcceptance=False,
                  productTestsExecuted=0, newAcceptance=0, formalUpdated=False, effortRate=None,
                  verifier={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, referencePairCoherent=True, overlayOnly=True,
                         metadataNegatives=len(negative), manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
