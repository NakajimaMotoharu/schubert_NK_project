"""Add original stream5 and a typed disclosure addendum; all original runtime proofs/counters unchanged."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15876-current2055-maintenance-records-registry-v1','e297179a1c121c3842432940be4f8a85d35de820c379fef7cf3661af79aa4389')
PREV_POST=('PG15878-current2055-maintenance-records-registry-post-v1','449e0bdee0bd324fe673f3b6d9ea13ed7b2f58abffb596279b68a778a89c9efe')
REFS=[['PG15888-scenario-record-stream-five-post-v1','221c4b68ed3f128cf26e43510f9d73c96bf4e031f9844b953a24b0b332aa6477','PG15890-scenario-record-stream-five-independent-v1','7aee60001f2663b25555ded009bc03b5d8628307009cf1fdf6e2f6c4cac2ea34',5,38]]
OUT=data.BASE/'PG15892-current2060-scenario-stream-registry-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior=read(PREV),read(PREV_POST)
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'exact independently qualified1760/owner11')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all current frozen inputs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,ind,indpin,count,negative in REFS:
        p,q=read((folder,pin)),read((ind,indpin));witnesses.extend([p,q])
        require(p['actualExit']==q['actualExit']==0 and p['source']==q['source']==SOURCE and q['postSha256']==pin and p['tests']==q['tests']==count and q['semanticNegativeVectors']==negative,'exact independent original proofs')
        require((q['sourcePrograms'],q['physicalClasses'],q['four100SourcePrograms'],q['naturallyBranchZeroSourcePrograms'],q['incompleteSourcePrograms'])==(1,1,1,0,0),'one strict whole source, not a prior helper reacceptance')
        require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is p['testOwnedTemporaryFixtureWrites'] is q['testOwnedTemporaryFixtureWrites'] is p['actualJdkFileForceOnOwnTemporaryFiles'] is q['actualJdkFileForceOnOwnTemporaryFiles'] is True,'actual own temporary file/force/public digest effects')
        require(p['testOwnNewSlotPublicEvidenceWrites'] is q['testOwnNewSlotPublicEvidenceWrites'] is p['actualSecretKeysLoaded'] is q['actualSecretKeysLoaded'] is p['actualPrivateFilesOpened'] is q['actualPrivateFilesOpened'] is False,'temporary fixtures are not explicit slot evidence or secrets')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and len(p['metadataClasses'])==0,'new distinct current cases/full Code only');cases|=new
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name],'whole new Source closure')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,row in p['owners'].items():
            require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual new canonical rows, not change-owner inference')
            require(path not in result['owners'] or result['owners'][path]==row,'all shared owner rows preserved');result['owners'][path]=copy.deepcopy(row)
        for n in p['metadataClasses']:
            require(n not in result['metadataClasses'] and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new exact NoCode mapper')
            result['metadataClasses'][n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_SCENARIO_RECORD_STREAM5_ONE_WHOLE_SOURCE_ONE_CODE_FOUR100'))
    correction_name='PG15889-reader-temporary-fixture-disclosure-erratum-v1';correction_sha='4f9439fb32a5f5876e07bbe731a4864e3c9b46da3e946b18428b46df2f54773f'
    correction=read((correction_name,correction_sha));require(correction['actualExit']==0 and correction['source']==SOURCE and correction['originalManifestAndToolUnchanged'] is True and correction['originalCountersSourceRunCasesAndCryptoUnchanged'] is True,'exact narrow erratum only')
    require(witnesses[-1]['disclosureErratumSha256']==correction_sha and witnesses[-1]['disclosureCorrectionNegativeVectors']==5,'independent erratum qualified without runtime replay')
    corrected_post=correction['originalPostSha256'];require(corrected_post not in old['postDisclosureCorrections'],'new correction append only')
    correction_ref=dict(manifest=str((data.BASE/correction_name/'manifest.json').relative_to(data.ROOT)),sha256=correction_sha,bug='BUG2151',horizontal='YKT1898',originalPostSha256=corrected_post,effectiveDisclosure=copy.deepcopy(correction['effectiveDisclosure']),originalQualificationAndCountersUnchanged=True)
    result['postDisclosureCorrections'][corrected_post]=copy.deepcopy(correction_ref)
    corrected_names=['dev/codex/schubert/nk/web/storage/ScenarioRecordReader','dev/codex/schubert/nk/web/storage/FileIntegrityException']
    for name in corrected_names:
        require(old['fullSourceUnits'][name]['postSha256']==corrected_post and 'effectDisclosureCorrection' not in old['fullSourceUnits'][name],'same original reader execution scope, no old unit substitution')
        units[name]['effectDisclosureCorrection']=copy.deepcopy(correction_ref)
    verify(correction['invocation'])
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(incomplete)==32 and len({p for n in incomplete for p in units[n]['physical']})==61,'disjoint whole Source closures and actual incomplete7/12')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+5,uniqueProductMethodDelta=5,newTestIds=5,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),metadataPhysical=len(meta),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({p for u in units.values() if u['branchNaturallyZero'] for p in u['physical']}),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())),unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(2060,274,463,621,590,250,364,353,119,120,2168,175,190),'exact current17/9Source/10physical classification')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=378,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229,UNKNOWN=158),'old215 candidates preserved/new9baseline5UNKNOWN')
    result['lastUpdateKind']='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED'
    require(all(result['postDisclosureCorrections'][k]==v for k,v in old['postDisclosureCorrections'].items()) and set(result['postDisclosureCorrections'])==set(old['postDisclosureCorrections'])|{corrected_post},'all prior errata retained, only narrow new erratum appended')
    changed={'postDisclosureCorrections','lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','metadataClasses','metadataPhysical'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all({k:value for k,value in result['fullSourceUnits'][n].items() if not(n in corrected_names and k=='effectDisclosureCorrection')}==v for n,v in old['fullSourceUnits'].items()) and all(result['owners'][n]==v for n,v in old['owners'].items()),'all old history/candidate215/cost/domain/formal/metadata semantics unchanged')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
