"""Attach a bounded relation-only observation and rebind the two-file WBS reference together."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/645_pending12_method_oracle_seal_scope.json'
O = B / 'evidence/PG24150-pending12-oracle-wbs-attachment-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def main():
    assert not O.exists()
    c = load(C)
    ip, sp = Path(c['wbsInventory']), Path(c['wbsSnapshot'])
    before_i, before_s = ip.read_bytes(), sp.read_bytes()
    assert sha(ip) == c['inputPins'][str(ip)] and sha(sp) == c['inputPins'][str(sp)]
    inventory, snapshot = load(ip), load(sp)
    assert snapshot['inventorySha256'] == sha(ip)
    post = B / 'evidence/PG24144-pending12-method-oracle-independent-v1/manifest.json'
    m = load(post)
    assert m['actualExit'] == 0 and m['boundedRelationCompletenessVerified'] is True
    assert m['newAcceptance'] == 0 and m['formalUpdated'] is False and m['effortRate'] is None
    assert m['fullOracleOrScopeAcceptance'] is False
    key = c['overlayKey']
    assert key not in inventory
    after_i = copy.deepcopy(inventory)
    after_i[key] = dict(source=c['source'], scopeStatus='LIMITED_METHOD_TEST_ORACLE_RELATION_SET_COMPLETE_WITH_LIMITS',
                        sourcePrograms=12, physicalClasses=17, knownMethodMetadata=87, measuredMethodRelations=67,
                        originalCompilerFilteredMethods=8, abstractNoCodeMethods=12,
                        originalUniqueCaseRefs=96, originalIndependentProofGroups=10,
                        reviewGroups=7, assertionSnippetChecks=254,
                        independentManifest={'path': str(post), 'sha256': sha(post)},
                        relationManifest=m['producerManifest'], fullOracleOrScopeAcceptance=False,
                        caseSpecificCoverageMeasured=False, originalExecOrCounterUnion=False,
                        currentWholeSourceOrDependencyAcceptance=False, registeredComponentDelta=None,
                        productTestsExecuted=0, newTests=0, newAcceptance=0, formalUpdated=False,
                        wholeG13Accepted=False, whole451Accepted=False, effortRate=None)
    after_s = copy.deepcopy(snapshot)
    after_i_bytes = encoded(after_i)
    after_s['inventorySha256'] = hashlib.sha256(after_i_bytes).hexdigest()
    after_s_bytes = encoded(after_s)
    reverse_i = copy.deepcopy(after_i)
    del reverse_i[key]
    assert reverse_i == inventory
    reverse_s = copy.deepcopy(after_s)
    reverse_s['inventorySha256'] = snapshot['inventorySha256']
    assert reverse_s == snapshot
    O.mkdir()
    # Preserve both proposed bytes before the small two-file save, allowing guarded recovery.
    (O / ip.name).write_bytes(after_i_bytes)
    (O / sp.name).write_bytes(after_s_bytes)
    ip.write_bytes(after_i_bytes)
    sp.write_bytes(after_s_bytes)
    assert load(sp)['inventorySha256'] == sha(ip)
    audit = subprocess.run(['python3', '-B', 'tools/quality/wbs_progress_audit.py'],
                           capture_output=True, text=True, timeout=60)
    (O / 'wbs-audit.stdout').write_text(audit.stdout)
    (O / 'wbs-audit.stderr').write_text(audit.stderr)
    before = load(B / 'evidence/PG24138-pending12-oracle-wbs-before-v1/manifest.json')
    last = audit.stderr.strip().splitlines()[-1] if audit.stderr.strip() else ''
    original_last = (B / 'evidence/PG24138-pending12-oracle-wbs-before-v1/wbs-audit.stderr').read_text().strip().splitlines()[-1]
    assert audit.returncode == before['actualExit'] == 1 and last == original_last
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  independentManifest={'path': str(post), 'sha256': sha(post)}, overlayKey=key,
                  inventoryBeforeSha256=hashlib.sha256(before_i).hexdigest(), inventoryAfterSha256=sha(ip),
                  snapshotBeforeSha256=hashlib.sha256(before_s).hexdigest(), snapshotAfterSha256=sha(sp),
                  addedOverlayOnly=True, snapshotChangedOnlyInventorySha256=True,
                  oldArtifactsAcceptanceAndBudgetUnchanged=True, referencePairCoherent=True,
                  wbsPreAuditExit=1, wbsPostAuditExit=audit.returncode, originalAuditHoldUnchanged=True,
                  boundedRelationCompletenessVerified=True, fullOracleOrScopeAcceptance=False,
                  productTestsExecuted=0, newAcceptance=0, formalUpdated=False, effortRate=None,
                  files={p.name: sha(p) for p in O.iterdir()},
                  tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_bytes(encoded(result))
    print(json.dumps(dict(actualExit=0, referencePairCoherent=True, oldValuesUnchanged=True,
                         preAuditExit=1, postAuditExit=1, manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
