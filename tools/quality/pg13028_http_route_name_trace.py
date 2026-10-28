"""Registry v2: two existing SHA edits only, no paths/owners/costs/runtime reassignment."""
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

SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
OUT = data.BASE/'PG13028-http-route-name-trace-v1'
POST = data.BASE/'PG13029-http-route-name-trace-post-v1'
PRIOR = data.BASE/'PG13006-value-binding-trace-v1/manifest.json'
PRIOR_SHA = 'f78a2bcc2f7285d3aacc87248ea21cb1ecc8ebafe34aaeec998fabaf218f972d'
PROOF_SHA = '6d4088dfc5b7b254ef4aaa652c41a3dd0e49d0106a0cfdc7759c5d1cffe19a1c'
MARKER = 'previousHttpRouteNamePG13028Reference'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricContract.java'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/HttpMetricContractTest.java'

def inputs():
    prior = data.read_checked(PRIOR,PRIOR_SHA)
    before = data.read_checked(data.BASE/'PG12998-value-binding-six-compile-v1/manifest.json','f391201e726c7e4ad28b86b4e8d5ef332e2c06cfdca02d4df05529f332f8e730')
    n = data.read_checked(data.BASE/'PG13018-http-route-name-six-compile-v1/manifest.json','66360a6446a271767118ed3ff4d734701f55a010638dc7676490409a0c488351')
    p = data.read_checked(data.BASE/'PG13024-http-route-name-post-v1/manifest.json',PROOF_SHA)
    c = data.read_checked(data.BASE/'PG13026-http-route-name-context-v1/manifest.json','e9a90bad3af371bf236ab3a54a29a5d6ea852038514195177a939dc93c4c46b1')
    assert prior['source'] == before['source'] == '94eeea264b449e5826f292c746a9cd4655b3122a'
    assert n['source'] == p['source'] == c['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == c['actualExit'] == 0
    assert p['selectedMainCoverage100'] and len(p['selectedMain']) == 6 and p['rawStatic'] == 4 and p['staticGateExit'] == 1 and p['spotbugsSixExit'] == 0
    assert p['observedTestExecutions'] == 6 and p['mainChangedPhysical'] == 5 and p['allOtherMainClassesUnchanged'] == 1838 and p['oldTestPhysicalUnchanged'] == 1969 and p['changedTestPhysical'] == 1 and p['newTestPhysical'] == 0
    assert c['sourceDerivedRaw'] == 8472 and c['totalPriorCorrections'] == 953
    hashes = n['begin']['inputHashes']; old = before['begin']['inputHashes']
    assert set(hashes) == set(old) and {path for path in hashes if hashes[path] != old[path]} == {MAIN,TEST}
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert len(prior['sourceRows']) == 990 and all(old[row['path']] == row['sha256'] for row in prior['sourceRows'])
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,p,hashes,raw,snap

def edited_rows(prior,hashes):
    rows = copy.deepcopy(prior['sourceRows']); seen = []
    for row in rows:
        if row['path'] in {MAIN,TEST}:
            assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P018-09'
            assert row['sha256'] != hashes[row['path']]
            row['sha256'] = hashes[row['path']]; seen.append(row['path'])
    assert set(seen) == {MAIN,TEST} and len(seen) == 2
    return rows

def require(value,prior,proof,hashes):
    assert value['schemaVersion'] == 'PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2' and value['source'] == SOURCE
    assert value['priorRegistryReference'] == dict(path=str(PRIOR.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    assert value['sourceRows'] == edited_rows(prior,hashes) and len(value['sourceRows']) == value['sourceCount'] == 990
    assert value['newAccepted'] == 0 and not value['whole451Accepted'] and not value['wholeF03Accepted']
    assert value['sourceDerivedRaw'] == 8472 and value['totalPriorCorrections'] == 953 and value['actualViolationCount'] is None
    assert value['currentQualification']['source'] == SOURCE and value['currentQualification']['proofManifestSha256'] == PROOF_SHA
    assert value['currentQualification']['selectedMain'] == proof['selectedMain'] and value['currentQualification']['selectedMainCoverage100']
    assert value['currentQualification']['observedTestExecutions'] == 6 and value['currentQualification']['rawStaticScope'] == 4
    assert value['registered'] == 1815 and value['javaPaths'] == 1817 and value['newPathsAdded'] == 0

def main():
    invocation = capture(__file__); assert not OUT.exists(); prior,proof,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    rows = edited_rows(prior,hashes)
    registered = universe & ({row['path'] for row in json.loads(raw)['artifacts']} | {row['path'] for row in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1817 and len(registered) == 1815 and unknown == prior['unregisteredJavaPaths']
    observed = audit(); assert observed['actualExit'] == 1
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str(PRIOR.relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=990,registered=1815,javaPaths=1817,registeredMain=965,totalMain=965,registeredTest=850,totalTest=852,
        unregisteredJavaPaths=unknown,newPathsAdded=0,newTestPaths=[],editedSourcePaths=[MAIN,TEST],existingShaOnlyEdits=2,
        original988OtherRowsAllFieldsPreserved=True,ownersCostsAndHistoricalFieldsUnchanged=True,
        newLogicalCandidates=sum(row.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for row in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(row.get('legacyReportedOwner') != row['canonicalOwner'] for row in rows),
        currentQualification=dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=6,newTestIds=0,suites=1,
            selectedMain=proof['selectedMain'],selectedMainCoverage100=True,rawStaticScope=4,staticGateExit=1,spotbugsSixExit=0,
            allMainPhysicalClasses=1843,mainChangedPhysical=5,allOtherMainClassesUnchanged=1838,oldTestPhysicalUnchanged=1969,changedTestPhysical=1,newTestPhysical=0,fullArtifactCoverage100=False),
        sourceDerivedRaw=8472,mainRaw=1504,testRaw=6968,totalPriorCorrections=953,actualViolationCount=None,
        removedFindingIds=['PMD-07371','PMD-08207'],inheritedFlatScopeCountersCopied=False,oldRuntimeDomainsReachableViaImmutablePriorReference=True,
        wholeWbsAuditBefore=observed,wholeCurrentGlobalAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    require(value,prior,proof,hashes); verify(invocation); OUT.mkdir(); data.write(OUT/'manifest.json',value)
    print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name]; assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2405_HTTP私有index命名_実行結果.md',currentAddedTestPaths=[],currentEditedSourcePaths=[MAIN,TEST])
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
                javaPaths=1817,registered=1815,unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=852,registered=850,unregistered=2))
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,
                sourceRows=990,newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def emit():
    _,_,_,raw,snap = inputs(); assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,after_snap = documents(raw,snap); patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,after_snap)]:
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__); assert not POST.exists(); prior,proof,hashes,raw,snap = inputs()
    m = json.loads((OUT/'manifest.json').read_bytes()); require(m,prior,proof,hashes)
    actual_raw,actual_snap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actual_raw,actual_snap,json.loads(raw),json.loads(snap)); assert (actual_raw,actual_snap) == documents(raw,snap)
    labels = []
    for label,change in [('owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-F03')),
        ('old-row-sha',lambda v:v['sourceRows'][0].update(sha256='0'*64)),('source',lambda v:v.update(source='0'*40)),
        ('acceptance',lambda v:v.update(newAccepted=1)),('legacy-runtime',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True)),
        ('raw',lambda v:v.update(sourceDerivedRaw=8474)),('corrections',lambda v:v.update(totalPriorCorrections=951)),
        ('fake-new-path',lambda v:v.update(newPathsAdded=1))]:
        bad = copy.deepcopy(m); change(bad); assert bad != m
        try: require(bad,prior,proof,hashes)
        except AssertionError: labels.append(label)
        else: raise AssertionError('wrong current source/owner/row accepted')
    observed = audit(); assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,existingShaOnlyEdits=2,original988OtherRowsAllFieldsPreserved=True,
        registered=1815,javaPaths=1817,unregisteredPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else: assert not sys.argv[1:]; main()
