"""Static PG-only source domain; preserve old PT domains, ownership and all other rows."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced, SECTIONS, INV, SNAP
from pg9338_wbs_reference_metadata_post import validate
from pg13084_monitor_test_context import state_after as previous_state

SOURCE = '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3'
OUT = data.BASE/'PG13144-main-literal-trace-v1'
POST = data.BASE/'PG13145-main-literal-trace-post-v1'
PRIOR_SHA = '2fcf6b839ebf0cf918f81573491f82bd54a54b09184c2f685b28fee74343a83f'
PROOF_SHA = '72128b769a31f41388d6ac2c8f25e5976ac36b479c2de561d22e370d9581c608'
MARKER = 'previousMainLiteralSourceOnlyPG13144Reference'
REMOVED = {'PMD-02953','PMD-06175'}

def state_after():
    ids,refs,pending = previous_state();assert REMOVED <= ids-refs
    p = data.read_checked(data.BASE/'PG13132-main-literal-preflight-v1/manifest.json','4367bdd95cd9f8f503855250edb1b9104ad2bd2edf146018912596973ed8f9c0')
    original = json.loads((data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes())
    retained = {r['id'] for r in original if r['path'] in p['candidateSourceHashes'] and r['id'] in ids-REMOVED}
    assert len(retained) == 14 and len(retained&refs) == 2 and not retained&pending
    return ids-REMOVED,refs,pending|(retained&refs)

def inputs():
    prior = data.read_checked(data.BASE/'PG13118-snapshot-max-trace-v3/manifest.json',PRIOR_SHA)
    n = data.read_checked(data.BASE/'PG13134-main-literal-six-compile-v1/manifest.json','ef0c374ffb76d88402c3a19c70999c9f644bdbdecb0252c747b7f1544521d823')
    p = data.read_checked(data.BASE/'PG13140-main-literal-post-v2/manifest.json',PROOF_SHA)
    s = data.read_checked(data.BASE/'PG13136-main-literal-static-v1/manifest.json','363f2e0fbda83bd9fd37ce57236e4197f3205dfa4b59f98f9e4a2395f2a8f479')
    assert n['source'] == p['source'] == s['source'] == SOURCE and n['actualExit'] == p['actualExit'] == s['actualExit'] == 0
    assert n['testsExecuted'] == p['productTestsExecuted'] == 0 and p['dynamicPtStatus'] == 'NOT_EXECUTED_HOLD'
    assert p['allMainPhysical'] == 1843 and p['changedMainPhysical'] == 5 and p['allTestPhysicalUnchanged'] == 1973
    hashes = n['begin']['inputHashes'];changed = set(s['sourceHashes'])
    assert len(changed) == 2 and all(hashes[path] == sha for path,sha in s['sourceHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert len(prior['sourceRows']) == 993 and {r['path'] for r in prior['sourceRows'] if r['sha256'] != hashes[r['path']]} == changed&{r['path'] for r in prior['sourceRows']}
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,p,hashes,changed,raw,snap

def expected_rows(prior,hashes,changed,raw):
    rows = copy.deepcopy(prior['sourceRows'])
    prior_paths = {row['path'] for row in rows}
    missing = changed-prior_paths
    expected_missing = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/TransferCleanup.java'
    assert missing == {expected_missing}
    logical = {row['path']:row for row in json.loads(raw)['artifacts']}
    assert logical[expected_missing]['owner'] == logical[expected_missing]['costOwner'] == 'WBS-P017-09'
    for row in rows:row['sha256'] = hashes[row['path']]
    rows.append(dict(path=expected_missing,sha256=hashes[expected_missing],owner='WBS-P017-09',canonicalOwner='WBS-P017-09',canonicalCostOwner='WBS-P017-09',
        changeOwner='WBS-F03',basis='2418_EXISTING_LOGICAL_ARTIFACT_STATIC_SOURCE_OVERLAY_NOT_NEW_PATH',
        ownershipStatus='EXISTING_LOGICAL_ARTIFACT_STATIC_SOURCE_OVERLAY_NOT_NEW_ACCEPTANCE',legacyReportedOwner='WBS-P017-09',
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,independentSpec='evidence/01_PT/018_NK-OPS-001/2418_Main残literal二件_製造静的確認仕様.md'))
    return rows

def validate_registry(value,prior,proof,hashes,changed,raw):
    assert value['source'] == SOURCE and value['sourceRows'] == expected_rows(prior,hashes,changed,raw)
    assert value['priorRegistryReference'] == dict(path=str((data.BASE/'PG13118-snapshot-max-trace-v3/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceCount'] == len(value['sourceRows']) == len(prior['sourceRows'])+1 and value['newPathsAdded'] == 0 and value['incrementalOverlayRowsAdded'] == 1
    assert value['lastChangeOwnerByPath'] == {path:'WBS-F03' for path in changed}
    q = value['currentQualification']
    assert q == dict(source=SOURCE,status='PG_STATIC_ONLY_NOT_PT_QUALIFIED',proofManifestSha256=PROOF_SHA,
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',
        measuredProductCounters=None,allMainPhysical=proof['allMainPhysical'],changedMainPhysical=proof['changedMainPhysical'],
        otherMainUnchanged=proof['otherMainUnchanged'],allTestPhysicalUnchanged=proof['allTestPhysicalUnchanged'],
        oldPtQualificationTransferred=False,rawStaticScope=14,rawStaticGateExit=1,spotbugsSixExit=0)
    ids,refs,pending = state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8459,3259,963,5200]
    assert [value['sourceDerivedRaw'],value['mainRaw'],value['testRaw'],value['totalPriorCorrections']] == [8459,1502,6957,966]
    assert value['joinedContextWarnings'] == len(refs) and value['sourceReboundCurrentWholePending'] == len(pending)
    assert value['actualViolationCount'] is None and value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']

def main():
    invocation = capture(__file__);assert not OUT.exists()
    prior,proof,hashes,changed,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    rows = expected_rows(prior,hashes,changed,raw);universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    registered = universe&({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    assert len(universe) == 1820 and len(registered) == 1818 and sorted(universe-registered) == prior['unregisteredJavaPaths']
    owners = {r['path']:(r['canonicalOwner'],r['canonicalCostOwner']) for r in rows if r['path'] in changed}
    assert set(owners.values()) == {('WBS-P017-09','WBS-P017-09'),('WBS-P018-03','WBS-P018-03')}
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    q = dict(source=SOURCE,status='PG_STATIC_ONLY_NOT_PT_QUALIFIED',proofManifestSha256=PROOF_SHA,
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',measuredProductCounters=None,
        allMainPhysical=proof['allMainPhysical'],changedMainPhysical=proof['changedMainPhysical'],otherMainUnchanged=proof['otherMainUnchanged'],
        allTestPhysicalUnchanged=proof['allTestPhysicalUnchanged'],oldPtQualificationTransferred=False,rawStaticScope=14,rawStaticGateExit=1,spotbugsSixExit=0)
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str((data.BASE/'PG13118-snapshot-max-trace-v3/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=len(rows),registered=len(registered),javaPaths=len(universe),registeredMain=965,totalMain=965,registeredTest=853,totalTest=855,
        unregisteredJavaPaths=sorted(universe-registered),newPathsAdded=0,incrementalOverlayRowsAdded=1,newTestPaths=[],currentQualification=q,
        lastChangeOwnerByPath={path:'WBS-F03' for path in changed},sourceDerivedRaw=8459,mainRaw=1502,testRaw=6957,totalPriorCorrections=966,
        joinedContextWarnings=3259,sourceReboundCurrentWholePending=963,noCurrentReferenceInThisJoin=5200,
        rawDeltaBasis='Exactly two original Main inputs changed by constant extraction; original two removed, retained14 signatures unchanged; all other source inputs fixed',
        globalBaselineCorrectionsAdded=2,newContextClassifications=0,existingSourceContextRebindings=2,actualViolationCount=None,
        wholeWbsAuditBefore=observed,wholeCurrentGlobalAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0,
        newLogicalCandidates=prior['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=prior['legacyOwnerLabelsDifferingFromCanonical'])
    validate_registry(value,prior,proof,hashes,changed,raw);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',value)
    print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name];assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2419_Main残literal二件_製造静的確認結果.md',currentAddedTestPaths=[])
        if name == SECTIONS[0]:section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
            javaPaths=m['javaPaths'],registered=m['registered'],unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=855,registered=853,unregistered=2))
        else:section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
            sourceRows=m['sourceCount'],newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def emit():
    _,_,_,_,raw,snap = inputs();assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap = documents(raw,snap);patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,asnap)]:
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__);assert not POST.exists()
    prior,proof,hashes,changed,raw,snap = inputs();m = json.loads((OUT/'manifest.json').read_bytes())
    validate_registry(m,prior,proof,hashes,changed,raw)
    actualraw,actualsnap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actualraw,actualsnap,json.loads(raw),json.loads(snap));assert (actualraw,actualsnap) == documents(raw,snap)
    labels = []
    for label,change in [('owner',lambda v:next(r for r in v['sourceRows'] if r['path'].endswith('/LinuxSystemdSession.java')).update(canonicalOwner='WBS-F03')),('old-row',lambda v:v['sourceRows'][0].update(sha256='0'*64)),
        ('missing-existing-overlay',lambda v:v['sourceRows'].pop()),('false-physical-new-path',lambda v:v.update(newPathsAdded=1)),('source',lambda v:v.update(source='0'*40)),('acceptance',lambda v:v.update(newAccepted=1)),
        ('old-pt-transfer',lambda v:v['currentQualification'].update(oldPtQualificationTransferred=True)),
        ('invent-coverage',lambda v:v['currentQualification'].update(measuredProductCounters={})),
        ('invent-pt',lambda v:v['currentQualification'].update(productTestsExecuted=3)),
        ('raw',lambda v:v.update(sourceDerivedRaw=0)),('runtime-domain',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True))]:
        bad = copy.deepcopy(m);change(bad);assert bad != m
        try:validate_registry(bad,prior,proof,hashes,changed,raw)
        except AssertionError:labels.append(label)
        else:raise AssertionError('wrong static-only qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        sourceRows=994,existingOverlayHashChanges=1,existingLogicalOverlayAdded=1,physicalSourceChangesBound=2,allCanonicalOwnersCostsAndOldRuntimePreserved=True,
        sourceDerivedRaw=8459,totalPriorCorrections=966,wholeWbsAudit=observed,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,productTestsExecuted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
