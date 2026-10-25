"""Two current WBS references only, exact raw hash, original semantics and actual audit HOLD."""
import copy
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import pg9338_wbs_reference_metadata_post as metadata
from pg9880_snapshot_nonce_trace import audit
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
PMO = ROOT/'documents/400_PGPT/470_PMO'
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
BEFORE = 'aba4a202b267a1dc7c84393b0fd4a0b37073dab8'
OUT = BASE/'PG9884-snapshot-nonce-metadata-post-v1'
REGISTRY = 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9880-snapshot-nonce-trace-v1/manifest.json'
REGISTRY_SHA = 'dd8c2590f9962bdcaa9f37c4f3ebf67c2940af14829b2b365ca8073b2ae15012'
PROOF = 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9882-snapshot-nonce-trace-post-v1/manifest.json'
PROOF_SHA = 'a04b5de32e9606bcfb9ddb2cfbd234d1f13301cd9d5982092079861f721b251f'
INVENTORY_SHA = 'bfb50af60960526ac7d74518837a3d687a91fe4869e79ce85c97c3363dd0aac5'


def contract(inv,snap,old_inv,expected_bindings,expected_raw_sha):
    for key in ('currentIncrementalHostOwnership','currentJavaPathExplicitRegistryMeasurement'):
        current,old = inv[key],old_inv[key]
        incremental = key == 'currentIncrementalHostOwnership'
        refkeys = ['source','manifest','sha256','record']+(['guardManifest','guardSha256','sourceRows','newLogicalCandidates']
            if incremental else ['independentPostManifest','independentPostSha256','javaPaths','registered','unregistered','main','test'])
        allowed = set(refkeys)|{'currentModifiedLogicalBindings','previousSnapshotNonceSourceOverlay'}
        if incremental:
            allowed |= {'legacyOwnerLabelsDifferingFromCanonical','guardReuseScope'}
        if set(current) != set(old)|{'previousSnapshotNonceSourceOverlay'}:
            raise ValueError('exact fields, only one explicit prior-reference note added')
        if any(current[k] != v for k,v in old.items() if k not in allowed):
            raise ValueError('all prior historical/cost/support fields unchanged')
        if current['previousSnapshotNonceSourceOverlay'] != {k:old[k] for k in refkeys}:
            raise ValueError('original references and prior counts retained')
        if current['source'] != SOURCE or current['manifest'] != REGISTRY or current['sha256'] != REGISTRY_SHA:
            raise ValueError('exact current completed source/registry/hash')
        if current['currentModifiedLogicalBindings'] != expected_bindings:
            raise ValueError('Outbox preserved and Codec current binding appended')
        if incremental:
            if current['guardManifest'] != PROOF or current['guardSha256'] != PROOF_SHA or current['sourceRows'] != 969 or current['newLogicalCandidates'] != 961:
                raise ValueError('current bounded969/961 and independent guard')
            if current['formalAccepted'] or current['newAccepted']:
                raise ValueError('no acceptance promotion')
        else:
            if current['independentPostManifest'] != PROOF or current['independentPostSha256'] != PROOF_SHA:
                raise ValueError('independent exact guard')
            if (current['javaPaths'],current['registered'],current['unregistered']) != (1796,1794,2):
                raise ValueError('exact source denominator with two unknown')
            if current['main'] != dict(total=965,registered=965,unregistered=0) or current['test'] != dict(total=831,registered=829,unregistered=2):
                raise ValueError('Main/Test dimensions separate')
            if current['wholeG13Accepted'] or current['effortPercent'] is not None:
                raise ValueError('no whole gate or effort invention')
    if snap['inventorySha256'] != expected_raw_sha:
        raise ValueError('exact original raw-byte hash, no semantic reserialization fallback')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    invpath,snappath = PMO/'485_WBS網羅性・受入対応.json',PMO/'486_WBS現行実績.json'
    old_inv_raw = subprocess.check_output(['git','show',BEFORE+':'+str(invpath.relative_to(ROOT))],cwd=ROOT)
    old_snap_raw = subprocess.check_output(['git','show',BEFORE+':'+str(snappath.relative_to(ROOT))],cwd=ROOT)
    old_inv,old_snap = json.loads(old_inv_raw),json.loads(old_snap_raw)
    raw,sraw = invpath.read_bytes(),snappath.read_bytes()
    assert data.sha(raw) == INVENTORY_SHA
    metadata.validate(raw,sraw,old_inv,old_snap)
    inv,snap = json.loads(raw),json.loads(sraw)
    joined,proof = data.read_checked(ROOT/REGISTRY,REGISTRY_SHA),data.read_checked(ROOT/PROOF,PROOF_SHA)
    assert joined['actualExit'] == proof['actualExit'] == 0 and joined['source'] == proof['source'] == SOURCE
    bindings = joined['currentModifiedLogicalBindings']
    contract(inv,snap,old_inv,bindings,data.sha(raw))
    assert inv['currentIncrementalHostOwnership']['legacyOwnerLabelsDifferingFromCanonical'] == sum(
        r.get('legacyReportedOwner') != r['canonicalOwner'] for r in joined['sourceRows'])
    assert proof['wholeWbsAuditBefore'] == joined['wholeWbsAuditBefore']
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        path = PMO/name
        assert path.read_bytes() == subprocess.check_output(['git','show',BEFORE+':'+str(path.relative_to(ROOT))],cwd=ROOT)
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in proof['auditSourceHashes'].items())
    negatives = []
    for label,edit in (
        ('wrong-source',lambda a,b:a['currentIncrementalHostOwnership'].update(source='0'*40)),
        ('wrong-proof',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement'].update(independentPostSha256='0'*64)),
        ('unknown-erased',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement'].update(registered=1796,unregistered=0)),
        ('old-binding-lost',lambda a,b:a['currentIncrementalHostOwnership']['currentModifiedLogicalBindings'].pop(0)),
        ('support-cost-reassigned',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement']['sharedOracleSupportDecision'].update(canonicalCostOwner='WBS-G13.07')),
        ('old-history-lost',lambda a,b:a['currentIncrementalHostOwnership'].pop('additionalCrossMethod23Observation')),
        ('prior-source-modified',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement']['previousSnapshotNonceSourceOverlay'].update(source=SOURCE)),
        ('raw-hash-wrong',lambda a,b:b.update(inventorySha256='0'*64)),
        ('canonical-json-fallback',lambda a,b:b.update(inventorySha256=data.sha(json.dumps(a).encode()))),
        ('accepted',lambda a,b:a['currentIncrementalHostOwnership'].update(formalAccepted=True)),
        ('unknown-field',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement'].update(unreviewed_field=True))):
        a,b = copy.deepcopy(inv),copy.deepcopy(snap)
        edit(a,b)
        try:
            contract(a,b,old_inv,bindings,data.sha(raw))
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid metadata accepted: '+label)
    assert len(negatives) == 11
    after = audit()
    assert after['actualExit'] == 1 and not after['passed'] and after['lastError'] == 'ValueError: current physical candidate exact Git/worktree scope'
    assert data.sha(invpath.read_bytes()) == data.sha(raw) and data.sha(snappath.read_bytes()) == data.sha(sraw)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=REGISTRY_SHA,independentOwnerPostSha256=PROOF_SHA,
        inventorySha256=data.sha(raw),snapshotSha256=data.sha(sraw),registered=1794,javaPaths=1796,unregistered=2,
        original941LogicalDatasetUnchanged=True,historical943PhysicalDatasetUnchanged=True,
        originalBudgetAndAcceptanceSemanticsUnchanged=True,onlyTwoCurrentInventorySectionsChanged=True,
        snapshotOnlyChangedField='inventorySha256',rawHashFallbackAllowed=False,metadataNegativeVectors=negatives,
        originalActualAuditBeforeReusedNoReplay=True,wholeWbsAuditBefore=proof['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,
        productTestsExecuted=0,actualExternalOperations=0,newAccepted=0,formalUpdated=False,wholeG13Accepted=False,
        whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1794,unknown=2,metadataNegatives=11,wholeAuditBefore=1,wholeAuditAfter=1,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
