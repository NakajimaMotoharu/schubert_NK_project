"""New codec Test registry row: dynamic dimensions from verified plan/host/proof, old domains kept."""
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

SOURCE = 'b11fe71bd20e244dd10c83bd339f8345a0c1f085'
OUT = data.BASE/'PG13166-nfc-golden-trace-v1'
POST = data.BASE/'PG13167-nfc-golden-trace-post-v1'
PRIOR_SHA = '0fb281be83adb94b0ead9ee71731ab6fe03cebbc3a9e9b64f1fdd530424f3124'
PROOF_SHA = 'cdec2827b883dd6e6d75a9aecbe1fbc11f3d42ab36f7bccbfb6a6e9479d275ad'
NEWS = ['src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/FieldCodecNfcGoldenTest.java']
MARKER = 'previousNfcGoldenPG13166Reference'

def inputs():
    prior = data.read_checked(data.BASE/'PG13144-main-literal-trace-v1/manifest.json',PRIOR_SHA)
    n = data.read_checked(data.BASE/'PG13156-nfc-golden-six-compile-v1/manifest.json','4c1f5352b5d048cda761851d3482fd74983b3ec885ed839d91f987bca60be0d9')
    p = data.read_checked(data.BASE/'PG13164-nfc-golden-post-v2/manifest.json',PROOF_SHA)
    plan = data.read_checked(data.BASE/'PG13154-nfc-golden-plan-v1/manifest.json','7695d1297c842faf24096b623194ff74903b849d58f2b4355f002ae9b5a5748f')
    host = data.read_checked(data.BASE/'PG13158-nfc-golden-host-v1/manifest.json','90af523f25fd27284d2fc5de6e2205ab1bfe0fcb4f77db7ae94f0d7e142fcabd')
    assert n['source'] == p['source'] == plan['source'] == host['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    dimensions = bind(plan,host,p);assert dimensions.public() == p['dimensions'] and dimensions.observed_cases == 8 and dimensions.suites == 2 and dimensions.new_test_ids == 3
    assert dimensions.main_physical_unchanged == 1843 and dimensions.old_test_physical_unchanged == 1973 and dimensions.new_test_physical == 1
    assert p['rawStatic'] == p['staticGateExit'] == p['spotbugsSixExit'] == 0 and not p['selectedMainCoverage100']
    hashes = n['begin']['inputHashes'];assert len(prior['sourceRows']) == 994 and all(hashes[r['path']] == r['sha256'] for r in prior['sourceRows'])
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,p,plan,dimensions,hashes,raw,snap

def new_rows(plan,hashes,raw):
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    subject = next(path for path in plan['eligibilityClosureSourceHashes'] if path.endswith('/codec/FieldCodec.java'))
    owner = 'WBS-P002-01';assert logical[subject]['owner'] == logical[subject]['costOwner'] == owner
    assert NEWS[0] in plan['wholeTestSourceHashes'] and NEWS[0] not in logical
    return [dict(path=NEWS[0],sha256=hashes[NEWS[0]],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,changeOwner=owner,
        basis='2422_NFC_HANGUL_ANGSTROM_COMBINING_ORDER_FIXED_SCALAR_HEX_ORACLES',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
        legacyReportedOwner=None,actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,independentSpec='evidence/01_PT/018_NK-OPS-001/2422_FieldCodec_NFC固定scalar・wire_単体テスト仕様.md',
        methodTestIds=['PT-CODEC-NFCGOLD001','PT-CODEC-NFCGOLD002','PT-CODEC-NFCGOLD003'],mainSourceSubjects=[subject],
        ownerProofManifest=str((data.BASE/'PG13164-nfc-golden-post-v2/manifest.json').relative_to(data.ROOT)),ownerProofSha256=PROOF_SHA)]

def validate_registry(value,prior,p,plan,dimensions,hashes,raw):
    assert value['source'] == SOURCE and value['sourceRows'] == prior['sourceRows']+new_rows(plan,hashes,raw)
    assert value['sourceCount'] == len(value['sourceRows']) == len({r['path'] for r in value['sourceRows']}) == len(prior['sourceRows'])+1
    assert value['priorRegistryReference'] == dict(path=str((data.BASE/'PG13144-main-literal-trace-v1/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False)
    verify_qualification(dimensions,value['currentQualification'])
    assert value['currentQualification']['proofManifestSha256'] == PROOF_SHA and value['currentQualification']['selectedMain'] == p['selectedMain']
    assert value['currentQualification']['selectedMainCoverage100'] is False and value['currentQualification']['fullArtifactCoverage100'] is False
    assert value['sourceDerivedRaw'] == 8459 and value['totalPriorCorrections'] == 966 and value['joinedContextWarnings'] == 3271 and value['sourceReboundCurrentWholePending'] == 975
    assert value['newAccepted'] == 0 and value['actualViolationCount'] is None and not value['whole451Accepted'] and not value['wholeF03Accepted']

def main():
    invocation = capture(__file__);assert not OUT.exists();prior,p,plan,d,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    context = data.read_checked(data.BASE/'PG13149-systemd-source-context-post-v1/manifest.json','b2d7947bd08f97f58b0872261d429793afaad836b21d188ef6af2dd607e7b25c')
    assert context['source'] == prior['source'] and context['actualExit'] == 0 and context['productTestsExecuted'] == 0
    rows = prior['sourceRows']+new_rows(plan,hashes,raw);universe = {path for path in hashes if '/java/' in path and path.endswith('.java')}
    registered = universe&({r['path'] for r in json.loads(raw)['artifacts']}|{r['path'] for r in rows})
    assert len(universe) == prior['javaPaths']+1 and len(registered) == prior['registered']+1 and sorted(universe-registered) == prior['unregisteredJavaPaths']
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    q = dict(source=SOURCE,proofManifestSha256=PROOF_SHA,observedTestExecutions=d.observed_cases,newTestIds=d.new_test_ids,suites=d.suites,
        wholeTestSources=d.whole_test_sources,allMainClassesUnchanged=d.main_physical_unchanged,oldTestPhysicalUnchanged=d.old_test_physical_unchanged,
        newTestPhysical=d.new_test_physical,selectedMain=p['selectedMain'],selectedMainCoverage100=False,fullArtifactCoverage100=False,rawStaticScope=0,spotbugsSixExit=0)
    value = dict(actualExit=0,schemaVersion='PGPT_JAVA_PATH_REGISTRY_SOURCE_DOMAIN_V2',source=SOURCE,invocation=invocation,
        priorRegistryReference=dict(path=str((data.BASE/'PG13144-main-literal-trace-v1/manifest.json').relative_to(data.ROOT)),sha256=PRIOR_SHA,source=prior['source'],oldRuntimeDomainsReassigned=False),
        sourceRows=rows,sourceCount=len(rows),registered=len(registered),javaPaths=len(universe),registeredMain=965,totalMain=965,registeredTest=len(registered)-965,totalTest=len(universe)-965,
        unregisteredJavaPaths=sorted(universe-registered),newPathsAdded=1,newTestPaths=NEWS,currentQualification=q,
        newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        sourceDerivedRaw=8459,mainRaw=1502,testRaw=6957,totalPriorCorrections=966,joinedContextWarnings=3271,sourceReboundCurrentWholePending=975,noCurrentReferenceInThisJoin=5188,
        actualViolationCount=None,rawDeltaBasis='All prior source inputs/1843Main/1973Test physical bytes unchanged; one new Test static0; raw8459/corr966 retained, no global replay',
        contextReference=dict(path=str((data.BASE/'PG13149-systemd-source-context-post-v1/manifest.json').relative_to(data.ROOT)),sha256='b2d7947bd08f97f58b0872261d429793afaad836b21d188ef6af2dd607e7b25c',oldDynamicQualificationTransferred=False),
        wholeWbsAuditBefore=observed,wholeCurrentGlobalAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    validate_registry(value,prior,p,plan,d,hashes,raw);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))

def documents(raw,snap):
    m = json.loads((OUT/'manifest.json').read_bytes())
    for name in SECTIONS:
        section = json.loads(raw)[name];assert MARKER not in section
        section[MARKER] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2423_FieldCodec_NFC固定scalar・wire_実行結果.md',currentAddedTestPaths=NEWS)
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
    invocation = capture(__file__);assert not POST.exists();prior,p,plan,d,hashes,raw,snap = inputs();m = json.loads((OUT/'manifest.json').read_bytes())
    validate_registry(m,prior,p,plan,d,hashes,raw);actualraw,actualsnap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    validate(actualraw,actualsnap,json.loads(raw),json.loads(snap));assert (actualraw,actualsnap) == documents(raw,snap);labels = []
    for label,change in [('owner',lambda v:v['sourceRows'][-1].update(canonicalOwner='WBS-F03')),('old-row',lambda v:v['sourceRows'][0].update(sha256='0'*64)),
        ('source',lambda v:v.update(source='0'*40)),('acceptance',lambda v:v.update(newAccepted=1)),('legacy-runtime',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True)),
        ('case-count',lambda v:v['currentQualification'].update(observedTestExecutions=3)),('suite-count',lambda v:v['currentQualification'].update(suites=1)),
        ('old-physical',lambda v:v['currentQualification'].update(oldTestPhysicalUnchanged=1972)),('new-physical',lambda v:v['currentQualification'].update(newTestPhysical=2)),
        ('coverage',lambda v:v['currentQualification'].update(selectedMainCoverage100=True))]:
        bad = copy.deepcopy(m);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(m,sort_keys=True)
        try:validate_registry(bad,prior,p,plan,d,hashes,raw)
        except (AssertionError,ValueError):labels.append(label)
        else:raise AssertionError('incorrect dynamic dimensions/owner accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed'];verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,prior994AllFieldsPreserved=True,sourceRows=len(m['sourceRows']),registered=m['registered'],javaPaths=m['javaPaths'],unknownPathsUnchanged=2,
        wholeWbsAudit=observed,inventorySha256=data.sha(actualraw),snapshotSha256=data.sha(actualsnap),newAccepted=0,whole451Accepted=False));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
