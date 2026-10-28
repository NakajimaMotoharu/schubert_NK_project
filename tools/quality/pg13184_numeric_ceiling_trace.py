"""Existing Test source hash update only; preserve canonical owners/cost and previous runtime domains."""
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
from quality_scope_dimensions import bind, verify_qualification

SOURCE = '80ba5f783432c84b6facd83bcd3a80774f4e4665'
OUT = data.BASE/'PG13184-numeric-ceiling-trace-v1'
POST = data.BASE/'PG13185-numeric-ceiling-trace-post-v1'
PRIOR_SHA = '3f8769ae62a70375d0d0a1b7e6085110d0dd9a08ec711be368b024f0392230e8'
PROOF_SHA = 'c62b307ca85ddf0b5a7e505817115eb41b4a3ce04bff9e9272aee1f3bdc0b4a5'
MODIFIED = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/FieldCodecTest.java'
MARKER = 'previousNumericCeilingPG13184Reference'

def inputs():
    prior = data.read_checked(data.BASE/'PG13166-nfc-golden-trace-v1/manifest.json',PRIOR_SHA)
    n = data.read_checked(data.BASE/'PG13176-numeric-ceiling-six-compile-v1/manifest.json','ba6cbaa31b2d244115de5665d30142d3b067da21625a01af415b1f002fbe940f')
    proof = data.read_checked(data.BASE/'PG13182-numeric-ceiling-post-v1/manifest.json',PROOF_SHA)
    plan = data.read_checked(data.BASE/'PG13174-numeric-ceiling-plan-v1/manifest.json','7cb6dbf4fb9b2532cd9e170dc18a71fcb6732a04314c693dc812ffea66c2a40d')
    host = data.read_checked(data.BASE/'PG13178-numeric-ceiling-host-v1/manifest.json','b1d058359df9b2d989b30a66b07f19a0125a2e2cbc6ae1dc6ae0e955030a56a1')
    assert n['source'] == proof['source'] == plan['source'] == host['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == proof['actualExit'] == 0
    dimensions = bind(plan,host,proof);assert dimensions.public() == proof['dimensions']
    assert dimensions.observed_cases == 9 and dimensions.new_test_ids == 1 and dimensions.suites == 2
    assert dimensions.old_test_physical_unchanged == 1973 and dimensions.new_test_physical == 0 and proof['changedTestPhysical'] == 1 and proof['previousTotalTestPhysical'] == 1974
    assert proof['selectedMainCoverage100'] is True and proof['rawStatic'] == proof['spotbugsSixExit'] == 0
    hashes = n['begin']['inputHashes'];assert len(prior['sourceRows']) == 995
    assert {r['path'] for r in prior['sourceRows'] if hashes[r['path']] != r['sha256']} == {MODIFIED}
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,proof,plan,dimensions,hashes,raw,snap

def rows_after(prior,hashes):
    rows = copy.deepcopy(prior['sourceRows']);selected = [r for r in rows if r['path'] == MODIFIED];assert len(selected) == 1
    row = selected[0];assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P002-01';row['sha256'] = hashes[MODIFIED]
    return rows

def validate_registry(value,prior,proof,d,hashes):
    assert value['source'] == SOURCE and value['sourceRows'] == rows_after(prior,hashes)
    assert value['sourceCount'] == len(value['sourceRows']) == 995 and value['newPathsAdded'] == 0 and value['modifiedTestPaths'] == [MODIFIED]
    assert value['priorRegistryReference'] == dict(path=str((data.BASE/'PG13166-nfc-golden-trace-v1/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    q = value['currentQualification'];verify_qualification(d,q)
    assert q['proofManifestSha256'] == PROOF_SHA and q['selectedMain'] == proof['selectedMain'] and q['selectedMainCoverage100'] is True
    assert q['changedTestPhysical'] == 1 and q['previousTotalTestPhysical'] == 1974 and q['fullArtifactCoverage100'] is False
    assert value['contextReference'] == prior['contextReference']
    assert [value[k] for k in ['sourceDerivedRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending']] == [8459,966,3271,975]
    assert value['newAccepted'] == 0 and value['actualViolationCount'] is None and not value['whole451Accepted'] and not value['wholeF03Accepted']

def main():
    invocation = capture(__file__);assert not OUT.exists();prior,p,plan,d,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    rows = rows_after(prior,hashes);universe = {path for path in hashes if '/java/' in path and path.endswith('.java')}
    registered = universe&({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    assert len(universe) == prior['javaPaths'] and len(registered) == prior['registered'] and sorted(universe-registered) == prior['unregisteredJavaPaths']
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    q = dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=d.observed_cases,newTestIds=d.new_test_ids,suites=d.suites,
        wholeTestSources=d.whole_test_sources,allMainClassesUnchanged=d.main_physical_unchanged,oldTestPhysicalUnchanged=d.old_test_physical_unchanged,newTestPhysical=d.new_test_physical,
        changedTestPhysical=p['changedTestPhysical'],previousTotalTestPhysical=p['previousTotalTestPhysical'],selectedMain=p['selectedMain'],selectedMainCoverage100=True,fullArtifactCoverage100=False,rawStaticScope=0,spotbugsSixExit=0)
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str((data.BASE/'PG13166-nfc-golden-trace-v1/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=len(rows),registered=len(registered),javaPaths=len(universe),registeredMain=965,totalMain=965,registeredTest=prior['registeredTest'],totalTest=prior['totalTest'],
        unregisteredJavaPaths=prior['unregisteredJavaPaths'],newPathsAdded=0,newTestPaths=[],modifiedTestPaths=[MODIFIED],currentQualification=q,
        newMethodIds=plan['newMethodIds'],newTestIds=['PT-CODEC-NUMMAX001'],contextReference=copy.deepcopy(prior['contextReference']),
        sourceDerivedRaw=8459,mainRaw=1502,testRaw=6957,totalPriorCorrections=966,joinedContextWarnings=3271,sourceReboundCurrentWholePending=975,noCurrentReferenceInThisJoin=5188,
        actualViolationCount=None,rawDeltaBasis='One existing Test appends one method; old/new five-source static0, original tokens recovered; all1843Main/1973 otherTest bytes fixed; global raw retained without replay',
        newLogicalCandidates=prior['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=prior['legacyOwnerLabelsDifferingFromCanonical'],
        wholeWbsAuditBefore=observed,wholeCurrentGlobalAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    validate_registry(value,prior,p,d,hashes);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name];assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2425_FieldCodec数値semantic上限_実行結果.md',currentAddedTestPaths=[])
        if name == SECTIONS[0]:section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,
            javaPaths=m['javaPaths'],registered=m['registered'],unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=m['totalTest'],registered=m['registeredTest'],unregistered=2))
        else:section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None,sourceRows=m['sourceCount'],newLogicalCandidates=m['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=m['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw));return raw,snap

def emit():
    _,_,_,_,_,raw,snap = inputs();assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap = documents(raw,snap);patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,asnap)]:patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__);assert not POST.exists();prior,p,_,d,hashes,raw,snap = inputs();m = json.loads((OUT/'manifest.json').read_bytes());validate_registry(m,prior,p,d,hashes)
    actualraw,actualsnap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes();validate(actualraw,actualsnap,json.loads(raw),json.loads(snap));assert (actualraw,actualsnap) == documents(raw,snap);labels = []
    for label,change in [('owner',lambda v:next(r for r in v['sourceRows'] if r['path'] == MODIFIED).update(canonicalOwner='WBS-F03')),
        ('old-row',lambda v:v['sourceRows'][0].update(sha256='0'*64)),('source',lambda v:v.update(source='0'*40)),('acceptance',lambda v:v.update(newAccepted=1)),
        ('legacy-runtime',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True)),('case-count',lambda v:v['currentQualification'].update(observedTestExecutions=8)),
        ('new-physical',lambda v:v['currentQualification'].update(newTestPhysical=1)),('changed-physical',lambda v:v['currentQualification'].update(changedTestPhysical=0)),
        ('coverage',lambda v:v['currentQualification'].update(selectedMainCoverage100=False)),('full-artifact',lambda v:v['currentQualification'].update(fullArtifactCoverage100=True))]:
        bad = copy.deepcopy(m);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(m,sort_keys=True)
        try:validate_registry(bad,prior,p,d,hashes)
        except (AssertionError,ValueError):labels.append(label)
        else:raise AssertionError('incorrect existing-source qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed'];verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,prior995OnlyOneSourceHashChanged=True,allOwnersCostsAndOldRuntimePreserved=True,
        sourceRows=len(m['sourceRows']),javaPaths=m['javaPaths'],registered=m['registered'],unknownPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,whole451Accepted=False));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
