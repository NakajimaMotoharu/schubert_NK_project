"""Existing Test SHA overlay only, no PT qualification or reassignment of historical runtime."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced, SECTIONS, INV, SNAP
from pg9338_wbs_reference_metadata_post import validate as validate_docs
from pg13148_systemd_source_context import state_after as previous_state
from pg13190_systemd_test_literal_originals import PATH

SOURCE = '41359340de234b8bea7578d957bcbf4df6ab951f'
OUT = data.BASE/'PG13200-systemd-test-literal-trace-v1'
POST = data.BASE/'PG13201-systemd-test-literal-trace-post-v1'
PRIOR_SHA = '3335e707da5300809d267d79177a3969fe83043fdfa07f504c07f4c21e4ce4ee'
MARKER = 'previousSystemdTestLiteralPG13200Reference'

def state_after():
    ids,refs,pending = previous_state()
    original = json.loads((data.BASE/'PG13190-systemd-test-literal-originals-v1/original.json').read_bytes())
    removed = {r['id'] for r in original['findings'] if r['attributes']['rule'] == 'AvoidDuplicateLiterals'}
    retained = {r['id'] for r in original['findings']}-removed
    assert len(removed) == 21 and removed <= ids-refs
    result = ids-removed,refs,pending|(retained&refs)
    assert [len(x) for x in result] == [8438,3271,976]
    return result

def inputs():
    prior = data.read_checked(data.BASE/'PG13184-numeric-ceiling-trace-v1/manifest.json',PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG13194-systemd-test-literal-six-compile-v1/manifest.json','6c6809515a4ae056dad337e44b5ffd8e26b617e0292e88df7082b3ddcddea1b9')
    proof = data.read_checked(data.BASE/'PG13198-systemd-test-literal-post-v1/manifest.json','3f52f5b1beea8cac7407c7ed5a2fa58af0a9dba7d6225162ce8ab95499e9e35d')
    assert proof['source'] == normal['source'] == SOURCE and proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert proof['allMainPhysicalUnchanged'] == 1843 and proof['currentTestPhysical'] == 1974 and proof['newTestPhysical'] == 0
    assert proof['productTestsExecuted'] == 0 and proof['dynamicPtStatus'] == 'NOT_EXECUTED_HOLD' and proof['coverageStatus'] == 'NOT_MEASURED'
    assert proof['privateConstantsAdded'] == 21 and proof['rawStatic'] == 19 and proof['rawStaticGateExit'] == 1
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    assert len(prior['sourceRows']) == 995 and {r['path'] for r in prior['sourceRows'] if hashes[r['path']] != r['sha256']} == {PATH}
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,proof,hashes,raw,snap

def rows_after(prior,hashes):
    rows = copy.deepcopy(prior['sourceRows']);target = [r for r in rows if r['path'] == PATH];assert len(target) == 1
    assert target[0]['canonicalOwner'] == target[0]['canonicalCostOwner'] == 'WBS-P018-03'
    target[0]['sha256'] = hashes[PATH];return rows

def expected(prior,p,hashes):
    ids,refs,pending = state_after()
    value = copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore']:value.pop(key,None)
    value.update(source=SOURCE,sourceRows=rows_after(prior,hashes),modifiedTestPaths=[PATH],newTestPaths=[],newMethodIds=[],newTestIds=[],newPathsAdded=0,
        priorRegistryReference=dict(path=str((data.BASE/'PG13184-numeric-ceiling-trace-v1/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        currentQualification=dict(source=SOURCE,status='PG_STATIC_ONLY_NOT_PT_QUALIFIED',proofManifestSha256=data.sha((data.BASE/'PG13198-systemd-test-literal-post-v1/manifest.json').read_bytes()),
            productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',measuredProductCounters=None,
            allMainPhysicalUnchanged=p['allMainPhysicalUnchanged'],currentTestPhysical=p['currentTestPhysical'],changedTestPhysical=p['changedTestPhysical'],newTestPhysical=0,
            rawStaticScope=19,rawStaticGateExit=1,spotbugsSixExit=0,oldPtQualificationTransferred=False),
        sourceDerivedRaw=len(ids),mainRaw=1502,testRaw=6936,totalPriorCorrections=987,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        contextReference=copy.deepcopy(prior['contextReference']),contextStateTransition='pg13200_systemd_test_literal_trace.state_after',
        rawDeltaBasis='Exact21 original Test duplicates removed; other19 retained; global analyzer not replayed',actualViolationCount=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    return value

def validate(value,prior,p,hashes):
    reference = expected(prior,p,hashes)
    actual = copy.deepcopy(value)
    for key in ['invocation','wholeWbsAuditBefore']:actual.pop(key,None)
    assert actual == reference

def main():
    invocation = capture(__file__);assert not OUT.exists();prior,p,h,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    value = expected(prior,p,h);observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    value.update(invocation=invocation,wholeWbsAuditBefore=observed);validate(value,prior,p,h);verify(invocation)
    OUT.mkdir();data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name];assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2428_SystemdTest重複literal21件_製造静的確認結果.md',currentAddedTestPaths=[])
        if name == SECTIONS[0]:section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,javaPaths=value['javaPaths'],registered=value['registered'],unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=value['totalTest'],registered=value['registeredTest'],unregistered=2))
        else:section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,sourceRows=value['sourceCount'],newLogicalCandidates=value['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=value['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw));return raw,snap

def emit():
    _,_,_,raw,snap = inputs();assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,after_snap = documents(raw,snap);patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,after_snap)]:patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__);assert not POST.exists();prior,p,h,raw,snap = inputs();value = json.loads((OUT/'manifest.json').read_bytes());validate(value,prior,p,h)
    actual_raw,actual_snap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes();validate_docs(actual_raw,actual_snap,json.loads(raw),json.loads(snap));assert (actual_raw,actual_snap) == documents(raw,snap)
    negatives = []
    for label,change in [('source',lambda v:v.update(source='0'*40)),('owner',lambda v:next(r for r in v['sourceRows'] if r['path'] == PATH).update(canonicalOwner='WBS-F03')),
        ('neighbour',lambda v:v['sourceRows'][0].update(sha256='0'*64)),('raw',lambda v:v.update(sourceDerivedRaw=8459)),('accepted',lambda v:v.update(newAccepted=1)),
        ('PT',lambda v:v['currentQualification'].update(productTestsExecuted=20)),('coverage',lambda v:v['currentQualification'].update(measuredProductCounters={})),
        ('old-domain',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True))]:
        bad = copy.deepcopy(value);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(value,sort_keys=True)
        try:validate(bad,prior,p,h)
        except AssertionError:negatives.append(label)
        else:raise AssertionError('incorrect static qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed'];verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(negatives),nonVacuousLabels=negatives,
        prior995OnlyOneSourceHashChanged=True,allOwnersCostsAndOldRuntimePreserved=True,sourceRows=995,unknownPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
