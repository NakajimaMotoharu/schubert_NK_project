"""Validate only two current registry references and inventory hash; keep original WBS semantics/HOLD."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
import pg9338_wbs_reference_metadata_post as metadata
from host_tool_invocation import capture, verify

ROOT = data.ROOT
PMO = ROOT / 'documents/400_PGPT/470_PMO'
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
BEFORE = '223bbcef6'
OUT = data.BASE / 'PG9838-shared-probe-snapshot-post-v1'
REGISTRY = 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9834-shared-probe-owner-v1/manifest.json'
REGISTRY_SHA = '0d361ca974427a14e3feab9ae8be3c55b704268da3576bd70cdfa52bd4bcf200'
PROOF = 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9836-shared-probe-owner-post-v1/manifest.json'
PROOF_SHA = '5fc8b6f8e3ce36b01c935ab557c70437674739c617d642d074393448c41f3011'


def current_contract(inv,snap):
    def require(condition,message):
        if not condition:
            raise ValueError(message)
    a,b = inv['currentIncrementalHostOwnership'],inv['currentJavaPathExplicitRegistryMeasurement']
    require(all(v['source'] == SOURCE and v['manifest'] == REGISTRY and v['sha256'] == REGISTRY_SHA for v in (a,b)),'exact current registry reference')
    require(a['sourceRows'] == 968 and a['newLogicalCandidates'] == 960 and a['unknownWithinBoundedRows'] == 0,'bounded registry count')
    require(a['guardManifest'] == b['independentPostManifest'] == PROOF and a['guardSha256'] == b['independentPostSha256'] == PROOF_SHA,'independent proof reference')
    require(b['javaPaths'] == 1795 and b['registered'] == 1793 and b['unregistered'] == 2,'current exact denominator, no unknown erasure')
    require(b['main'] == dict(total=965,registered=965,unregistered=0) and b['test'] == dict(total=830,registered=828,unregistered=2),'separate Main/Test measurement')
    for v in (a,b):
        rule = v['sharedOracleSupportDecision']
        require(rule == dict(id='PG-D673',canonicalOwner='WBS-G03',canonicalCostOwner='WBS-G03',exactSourcePaths=6,consumerReferences=25,
            businessConsumerOwnersChanged=False,historicalCostReallocated=False,executionPermissionInferred=False,accepted=False),'bounded support rule, no authority or business reassignment')
        require(v['previousSharedProbeSourceOverlay']['source'] == '58913ab374ef54d138fa3fad8c80cccd03d87c10','actual prior metadata source retained')
        require(v['intermediateCleanupValueRegistry']['sha256'] == 'ac07bdb3152cb171996e913c48d01b63cf1ea75583a5a7584008b646756d456c','intermediate registry not omitted')
    require(not a['formalAccepted'] and not a['newAccepted'] and not b['wholeG13Accepted'] and b['effortPercent'] is None,'no acceptance or effort promotion')
    require(snap['inventorySha256'] == data.sha(json.dumps(inv,ensure_ascii=False).encode()) or snap['inventorySha256'] == data.sha((PMO / '485_WBS網羅性・受入対応.json').read_bytes()),'current original byte hash only')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    invpath,snappath = PMO / '485_WBS網羅性・受入対応.json',PMO / '486_WBS現行実績.json'
    old_inv = json.loads(subprocess.check_output(['git','show',BEFORE + ':' + str(invpath.relative_to(ROOT))],cwd=ROOT))
    old_snap = json.loads(subprocess.check_output(['git','show',BEFORE + ':' + str(snappath.relative_to(ROOT))],cwd=ROOT))
    raw,sraw = invpath.read_bytes(),snappath.read_bytes()
    metadata.validate(raw,sraw,old_inv,old_snap)
    inv,snap = json.loads(raw),json.loads(sraw)
    assert snap['inventorySha256'] == data.sha(raw)
    current_contract(inv,snap)
    proof = data.read_checked(ROOT / PROOF,PROOF_SHA)
    joined = data.read_checked(ROOT / REGISTRY,REGISTRY_SHA)
    assert proof['actualExit'] == joined['actualExit'] == 0 and proof['source'] == joined['source'] == SOURCE
    assert proof['registered'] == joined['registered'] == 1793 and proof['newCandidates'] == joined['sourceOwnerCandidatesAdded'] == 6
    for v in (inv['currentIncrementalHostOwnership'],inv['currentJavaPathExplicitRegistryMeasurement']):
        assert v['currentModifiedLogicalBindings'] == joined['currentModifiedLogicalBindings']
    assert inv['currentIncrementalHostOwnership']['legacyOwnerLabelsDifferingFromCanonical'] == sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in joined['sourceRows'])
    negative = []
    for label,edit in (
        ('unknown-erased',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement'].update(registered=1795,unregistered=0)),
        ('owner-changed-to-working-group',lambda a,b:a['currentIncrementalHostOwnership']['sharedOracleSupportDecision'].update(canonicalOwner='WBS-G13.07')),
        ('cost-reallocated',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement']['sharedOracleSupportDecision'].update(historicalCostReallocated=True)),
        ('execution-permitted',lambda a,b:a['currentIncrementalHostOwnership']['sharedOracleSupportDecision'].update(executionPermissionInferred=True)),
        ('accepted-invented',lambda a,b:a['currentIncrementalHostOwnership']['sharedOracleSupportDecision'].update(accepted=True)),
        ('bad-proof',lambda a,b:a['currentJavaPathExplicitRegistryMeasurement'].update(independentPostSha256='0'*64))):
        a,b = copy.deepcopy(inv),copy.deepcopy(snap)
        edit(a,b)
        try:
            current_contract(a,b)
        except ValueError:
            negative.append(label)
        else:
            raise AssertionError('metadata counterexample accepted: ' + label)
    assert len(negative) == 6
    command = [sys.executable,'-B',str(ROOT / 'tools/quality/wbs_progress_audit.py')]
    run = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
    last = run.stderr.decode().splitlines()[-1]
    assert run.returncode == 1 and not run.stdout and last == proof['wholeWbsAuditBefore']['lastError']
    assert data.sha(invpath.read_bytes()) == data.sha(raw) and data.sha(snappath.read_bytes()) == data.sha(sraw)
    verify(invocation)
    OUT.mkdir()
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=REGISTRY_SHA,independentOwnerPostSha256=PROOF_SHA,
        inventorySha256=data.sha(raw),snapshotSha256=data.sha(sraw),original941LogicalDatasetUnchanged=True,
        historical943PhysicalDatasetUnchanged=True,originalBudgetAndAcceptanceSemanticsUnchanged=True,
        metadataNegativeVectors=negative,registered=1793,javaPaths=1795,unregistered=2,
        wholeWbsAuditBefore=proof['wholeWbsAuditBefore'],wholeWbsAuditAfter=dict(command=command,actualExit=1,lastError=last,passed=False),
        productTestsExecuted=0,actualExternalOperations=0,newAccepted=0,formalUpdated=False,wholeG03Accepted=False,
        wholeG13Accepted=False,wholeWbsAuditHoldNotLifted=True,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,registered=1793,unregistered=2,wholeWbsAudit='BEFORE_AFTER_ACTUAL1_HOLD',
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
