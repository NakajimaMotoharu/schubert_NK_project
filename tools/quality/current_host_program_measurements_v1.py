"""Immutable scoped host registry; all measurements remain in separate original executions."""
import copy
import json
import subprocess
from pathlib import Path
import g07_host_class_provenance_inputs as data
import snapshot_program_qualified_v2 as cfg
from trace_owner_join import canonical
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE=cfg.SOURCE
BASE='55d0758b1ab88da5e0a10c3a7d75fd3a93b36015'
PRIOR=('PG14086-main-monitor-eighty-one-trace-v1','7ae5c6848478b409aa366c974e777aa25d0a7abac23fbe1b328e82d68d01580c')
BASE_AUDIT=('PG13956-used35-periodic-original-manifest-audit-v1','86593de60fa46eb34b7d2f85f587c3baa04d20aed1d84c3f88d5cdddb087761e')
ADDED=[
 ('PG14014-maintenance-parent-guard-whole-six-post-v1','ec2910e33c11f274908de9b2c47dde6e2e55d7df0925d6ea6d3fb25b4cb840f9',6,1),
 ('PG14094-context-hash-whole-three-post-v1','fce0833bbe6aa9026995f27d2ac264bdc70fd28099cc30e380a42cbce4f0b28e',3,1),
 ('PG14101-api-stop-budget-whole-eighteen-post-v2','3fc4a6469d7ff348981bfed1a53f42be7e102064f953d403bf00a69a9da3946c',18,1),
 ('PG14112-batch-timed-state-whole-twenty-four-post-v1','1284185d6b10454f6254ce8b7369f87056446a36b09ecb6a754f105bd207f986',24,3),
 ('PG14118-batch-metric-whole-thirteen-post-v1','6666f7428340fb37f641bd4a63ec393d72a024bba53047999b9d99068ba431d1',13,2)]
OUT=data.BASE/'PG14122-current-host-program-measurements-v1'
RECORD='evidence/01_PT/018_NK-OPS-001/2583_現source完全Program測定_WBS参照結果.md'
MODULES=('api','batch','bootstrap','protocol','storage','web')

def unit_path(unit):
    matched=[m for m in MODULES if unit.startswith('dev/codex/schubert/nk/'+m+'/')]
    if len(matched)!=1:raise ValueError('literal known module prefix, never positional guess')
    return 'src/schubert-nk-'+matched[0]+'/src/main/java/'+unit+'.java'

def inputs():
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw)=='299ac769a257478ec82c5ffb880f33709efbb6e02ec80524bb4de9790ae075f6'
    assert data.sha(snap)=='39356f11cc3a7f466059bcf4041d18260f7d4b26ebb1f225bba629efe4aa7c26'
    prior=data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    base=data.read_checked(data.BASE/BASE_AUDIT[0]/'manifest.json',BASE_AUDIT[1])
    assert prior['source']==base['source']==SOURCE and base['actualExit']==0
    normal,pin=cfg.normal();assert pin=='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
    assert normal['actualExit']==normal['testsExecuted']==0 and normal['source']==SOURCE
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    assert all(data.sha(Path(v['path']).read_bytes())==v['sha256'] for v in normal['jars'].values())
    posts={};refs=copy.deepcopy(base['postReferences'])
    refs.extend(dict(path=str((data.BASE/n/'manifest.json').relative_to(data.ROOT)),sha256=h,source=SOURCE,methods=t,suites=s) for n,h,t,s in ADDED)
    cases=[]
    for ref in refs:
        post=data.read_checked(data.ROOT/ref['path'],ref['sha256'])
        assert post['source']==SOURCE and post['actualExit']==0 and len(post['cases'])==ref['methods']
        cases.extend((r['classname'],r['name']) for r in post['cases']);posts[ref['sha256']]=post
    assert len(refs)==len(posts)==16 and len(cases)==len(set(cases))==183 and sum(r['suites'] for r in refs)==31
    programs=copy.deepcopy(base['fullSourceProgramMeasurements'])
    for index in [2,3,4]:
        n,h,t,s=ADDED[index];post=posts[h];ref=next(r for r in refs if r['sha256']==h)
        if index==2:
            unit='dev/codex/schubert/nk/api/bootstrap/ApiStopBudget'
            programs.append(dict(source=SOURCE,sourceUnit=unit,completeSourceClosure=post['completeSourceUnitClosure'],executablePhysical=1,postManifest=ref,totalsFromOneOriginalExecOnly=post['totals']))
        else:
            for unit,value in sorted(post['fullSourceUnits'].items()):
                assert value['four100'] is True
                programs.append(dict(source=SOURCE,sourceUnit=unit,completeSourceClosure=value['physical'],executablePhysical=len(value['physical']),postManifest=ref,totalsFromOneOriginalExecOnly=value['totals']))
    assert len(programs)==len({p['sourceUnit'] for p in programs})==15 and sum(p['executablePhysical'] for p in programs)==23
    logical={r['path']:r for r in json.loads(raw)['artifacts']}
    for program in programs:
        totals=program['totalsFromOneOriginalExecOnly']
        assert set(totals)=={'LINE','METHOD','CLASS','BRANCH'} and all(type(v['covered']) is int and v['covered']>0 and type(v['missed']) is int and v['missed']==0 for v in totals.values())
        path=unit_path(program['sourceUnit'])
        program.update(path=path,sourceSha256=hashes[path],canonicalOwnership=canonical(path,logical),runtimeDomain='ONE_ORIGINAL_SCOPED_EXECUTION_NOT_GLOBAL_UNION',formalAccepted=False)
    checks='dev/codex/schubert/nk/batch/file/MorningCompletionChecks'
    hash_reference=next(r for r in refs if r['sha256']==ADDED[1][1])
    natural=[
      dict(sourceUnit=checks,path=unit_path(checks),totals=base['additionalCompleteChecksSourceNaturalZeroBranch'],qualification='FULL_SOURCE_COUNTERS_WITH_NATURAL_ZERO_BRANCH_NOT_FOUR100',postManifest=next(r for r in refs if r['path'].endswith('PG13914-morning-completion-boundaries-whole-thirteen-post-v1/manifest.json'))),
      dict(sourceUnit='dev/codex/schubert/nk/api/security/ContextHash',path=unit_path('dev/codex/schubert/nk/api/security/ContextHash'),totals=posts[ADDED[1][1]]['totals'],qualification='FULL_SOURCE_COUNTERS_WITH_NATURAL_ZERO_BRANCH_NOT_FOUR100',postManifest=hash_reference)]
    for item in natural:
        assert item['totals']['BRANCH']==dict(missed=0,covered=0)
        item.update(source=SOURCE,sourceSha256=hashes[item['path']],branchPercent=None,canonicalOwnership=canonical(item['path'],logical),formalAccepted=False)
    assert len(prior['sourceRows'])==995
    module_hashes={'tools/quality/pmd_context_disposition.py':'ca7dd1a05c261e06368413368be38d1f5de3ca714f636b881cf0e87e4c0035bc','tools/quality/pmd_contract_disposition.py':'36d3462499c7637bf880a8a935d38af4ab4db73f4b7848d1f161a02f092d2705'}
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in module_hashes.items())
    return prior,refs,programs,natural,raw,snap,pin,module_hashes

def expected(prior,refs,programs,natural,pin,module_hashes):
    return dict(actualExit=0,source=SOURCE,record=RECORD,normalManifestSha256=pin,originalPostReferences=refs,originalExecutions=16,uniqueMethods=183,suiteReferences=31,fullSourceProgramMeasurements=programs,fullSourceProgramsFour100=15,fullSourceExecutablePhysicalFour100=23,naturalZeroBranchSources=natural,naturalZeroBranchSourceCount=2,retainedPartialAndUnmeasured=['MaintenanceOwnerFrame Guard default Code methods unmeasured','WebRuntimeExecution partial','StartClient remaining physical closures','StartupLaunchOwner parent/factories','RootScope native overload and BootstrapAdmin actual behavior','All original whole/native/CHR/quality held dependencies remain'],
      previousRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1]),previous995RowsAndHistoricalRuntimeUnchanged=True,previousSnapshotCurrentQualificationUnchanged=True,previous995SourceRowsSha256=data.sha(json.dumps(prior['sourceRows'],sort_keys=True).encode()),previousCurrentQualificationSha256=data.sha(json.dumps(prior['currentQualification'],sort_keys=True).encode()),applicabilityModuleHashes=module_hashes,applicabilityAssessmentCanPassWholeQuality=False,ruleConfigurationChanged=False,rawWarningsRemoved=0,productTestsExecuted=0,coverageExecReanalyzed=False,globalExecUnion=False,oldSourceSuccessTransferred=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False,qualification='CURRENT_SCOPED_HOST_MEASUREMENT_REFERENCES_NOT_FORMAL')

def documents(value,raw,snap):
    original=json.loads(raw);result=raw
    overlay=dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,qualification=value['qualification'],fullSourceProgramsFour100=15,fullSourceExecutablePhysicalFour100=23,naturalZeroBranchSourceCount=2,originalExecutions=16,uniqueMethods=183,suiteReferences=31,previous995RowsAndHistoricalRuntimeUnchanged=True,previousSnapshotCurrentQualificationUnchanged=True,globalExecUnion=False,newAccepted=0,formalUpdated=False,whole451Accepted=False)
    for name in SECTIONS:
        section=copy.deepcopy(original[name]);assert 'currentScopedHostMeasurementsPG14122' not in section
        section['currentScopedHostMeasurementsPG14122']=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    result_snap,_,_=replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,original,json.loads(snap))
    return result,result_snap
