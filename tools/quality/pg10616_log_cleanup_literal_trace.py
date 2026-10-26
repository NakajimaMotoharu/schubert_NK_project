"""Two source SHA changes only; keep original owners, costs and historical runtimes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV, SNAP, SECTIONS

ROOT = data.ROOT
BASE = 'bfd74f2e6'
SOURCE = '95894757e2bd7f392262497ea620873430ccc5f1'
PRIOR = 'df46372e702b3b0b28c9609250f002b3d7308cd825b8b0298fbe2a1867f99172'
PROOF = 'd52b92859b889cbae3d5cfaeafb3933d194cb4a4d74ae2f7443c156c3a0b8075'
OUT = data.BASE/'PG10616-log-cleanup-literal-trace-v1'
POST = data.BASE/'PG10618-log-cleanup-literal-trace-post-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2091_LogCleanup十一定数・静的指摘減少結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10602-fixed-error-oracle-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10614-log-cleanup-literal-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10612-log-cleanup-literal-compile-v1/manifest.json',
        '7e484e3e66d5f8b678c933a8628d40e4ecb7d145d1f426d8372c9e22d411fcf1')
    assert proof['source'] == normal['source'] == SOURCE
    assert proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    changes = {r['path']:r for r in proof['sourceChanges']}
    assert len(changes) == 2
    bindings = []
    for old,new in zip(prior['sourceRows'],value['sourceRows']):
        if old['path'] in changes:
            item = changes[old['path']]
            assert old['sha256'] == item['beforeSha256'] != item['sha256'] == hashes[old['path']]
            assert old['canonicalOwner'] == old['canonicalCostOwner'] == old['owner'] != 'UNKNOWN'
            new['sha256'] = item['sha256']
            bindings.append(dict(path=old['path'],beforeSha256=old['sha256'],sha256=new['sha256'],
                canonicalOwner=old['canonicalOwner'],canonicalCostOwner=old['canonicalCostOwner']))
        restored = copy.deepcopy(new)
        restored['sha256'] = old['sha256']
        assert restored == old
    assert len(bindings) == 2 and len(value['sourceRows']) == 983
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentLogCleanupLiteralBinding=dict(source=SOURCE,sourceChanges=bindings,proofManifestSha256=PROOF,
            sameValueConstants=11,references=64,mainClassesUnchanged=1843,otherTestClassesUnchanged=proof['otherTestClassesUnchanged'],
            productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,
            staticRawFindings=39,staticApplicability='PENDING',whole451Accepted=False,
            additionalSharedCostPp=0,oldRuntimeReassigned=False))
    for key in ('currentTraceContextRuntimeQualification','currentPublicTemplateRuntimeQualification',
                'currentPureViewRuntimeQualification','currentAnmNameMetadataBinding'):
        assert value[key] == prior[key]
    assert value['currentFixedErrorOracleBinding'] == prior['currentFixedErrorOracleBinding']
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousLogCleanupLiteralRegistryReference' not in section
        section['previousLogCleanupLiteralRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentLogCleanupLiteralBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentLogCleanupLiteralBinding',
            qualification='SAME_VALUE_CONSTANT_PG_SOURCE_COMPILE_METADATA_NOT_DYNAMIC_PT')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def contract(value,reference):
    if any(value.get(k) != v for k,v in reference.items()):
        raise ValueError('exact source-only bindings; all original runtime and owner/cost fields immutable')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,hashes,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    reference = expected(prior,proof,hashes)
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,priorRegistrySha256=PRIOR,
        proofManifestSha256=PROOF,wholeWbsAuditBefore=observed,**reference))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    _,_,pairs,spairs = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines:
            patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,proof,hashes,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,hashes)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    rejected = []
    mutations = [
        ('owner',lambda v:v['currentLogCleanupLiteralBinding']['sourceChanges'][0].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['currentLogCleanupLiteralBinding'].update(additionalSharedCostPp=1)),
        ('runtime-transfer',lambda v:v['currentTraceContextRuntimeQualification'].update(source=SOURCE)),
        ('invented-pt',lambda v:v['currentLogCleanupLiteralBinding'].update(productTestsExecuted=4)),
        ('invented-coverage',lambda v:v['currentLogCleanupLiteralBinding'].update(coverage=100)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('sha',lambda v:v['sourceRows'][0].update(sha256='0'*64)),
        ('source',lambda v:v.update(source=prior['source']))]
    for label,edit in mutations:
        damaged = copy.deepcopy(reference)
        edit(damaged)
        assert damaged != reference
        try:
            contract(damaged,reference)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('invalid source-only qualification accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=rejected,registered=1808,total=1810,unknown=2,
        oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()

