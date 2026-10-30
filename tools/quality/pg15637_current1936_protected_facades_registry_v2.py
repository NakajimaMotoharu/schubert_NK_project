"""Whole facades24 registry: retain finished independent actual OUT including historical duplicate suffix."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15620-current1912-dlq-web-health-registry-v1','60495269d8b2f1ef5e0096b18a30f22806dcd145c755624c27ad75455f4859ce')
PREV_POST=('PG15622-current1912-dlq-web-health-registry-post-v1','76912b44b42e6105494d3ffe19f8379ce52fefe06fd29fe790364126bf753836')
REFS=[['PG15632-protected-facades-twenty-four-post-v1','ae77f8127ca5d1afacdace5b986aef4f1519d7c33e83fecbae551c8109566b64','PG15634-protected-facades-twenty-four-independent-v1-independent-v1','2d2e1f2b4c800cb9f8083208c6a7c62a10d831622106e620f85eddb77344ce04',24,28]]
OUT=data.BASE/'PG15637-current1936-protected-facades-registry-v2'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    import pg15634_protected_facades_twenty_four_independent as independent
    require(independent.OUT.name==REFS[0][2] and independent.PIN==REFS[0][1] and independent.OUT.name!='PG15634-protected-facades-twenty-four-independent-v1','actual frozen independent OUT, no guessed path')
    require(data.sha((data.ROOT/'tools/quality/pg15634_protected_facades_twenty_four_independent.py').read_bytes())=='729d5f7321e7c354f765bd30cb8baf89dc1ec2717b0732de656b1c72354f5b14','original finished independent entry unchanged')
    require(data.sha((data.ROOT/'tools/quality/pg15636_current1936_protected_facades_registry.py').read_bytes())=='7dc91941b2d436d7dc93f80883b54589f513c56b7808e9c38cc393d1ef0c09ca','old failed entry frozen')
    require(data.sha((independent.OUT/'manifest.json').read_bytes())==REFS[0][3] and REFS[0][3]!='0'*64,'actual finished manifest hash and wrong hash separation')
    old,prior=read(PREV),read(PREV_POST)
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'exact independently qualified1760/owner11')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all current frozen inputs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,ind,indpin,count,negative in REFS:
        p,q=read((folder,pin)),read((ind,indpin));witnesses.extend([p,q])
        require(p['actualExit']==q['actualExit']==0 and p['source']==q['source']==SOURCE and q['postSha256']==pin and p['tests']==q['tests']==count and q['semanticNegativeVectors']==negative,'exact independent original proofs')
        require((q['sourcePrograms'],q['physicalClasses'],q['four100SourcePrograms'],q['naturallyBranchZeroSourcePrograms'],q['incompleteSourcePrograms'],q['baselineMainOwnerRows'],q['unknownTestOwnerRows'])==(3,4,0,3,0,3,3),'exact per-program categories')
        require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is True and p['publicSyntheticTestKeysUsed'] is q['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is q['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is q['ownFreshJvmProviderStateOnly'] is p['actualSecretKeysLoaded'] is q['actualSecretKeysLoaded'] is False,'truthful public SHA comparison/no key or JCA mutation')
        require(p['actualJmsConnectionsCreated']==q['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==q['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is q['actualBrokerOrListenerStarted'] is p['actualFilesOpenedByProduct'] is q['actualFilesOpenedByProduct'] is p['actualCredentialValuesUsed'] is q['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is q['actualAuthenticationOrSessionIssued'] is False and q['previousHelpersNotReaccepted'] is True and p['cryptoOperationKind']==q['cryptoOperationKind']=='MESSAGEDIGEST_ISEQUAL_PUBLIC_SYNTHETIC_CONTEXT_TEXT_ONLY','public fixture only/no real auth/keys/files and no previous helper reacceptance')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'new distinct current cases/full Code only');cases|=new
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name],'whole new Source closure')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,row in p['owners'].items():
            require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual new canonical rows, not change-owner inference')
            require(path not in result['owners'] or result['owners'][path]==row,'all shared owner rows preserved');result['owners'][path]=copy.deepcopy(row)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PROTECTED_FACADES24_FULL_THREE_SOURCE_FOUR_CODE_THREE_NATURAL'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(incomplete)==15 and len({p for n in incomplete for p in units[n]['physical']})==24,'disjoint whole Source closures and actual incomplete7/12')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+24,uniqueProductMethodDelta=24,newTestIds=24,sourceProgramDelta=3,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({p for u in units.values() if u['branchNaturallyZero'] for p in u['physical']}),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())),unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(1936,248,433,568,547,242,354,343,105,106,2044,170,184),'exact current17/9Source/10physical classification')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=348,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=132),'old215 candidates preserved/new9baseline5UNKNOWN')
    result['lastUpdateKind']='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED'
    require(result['postDisclosureCorrections']==old['postDisclosureCorrections'] and result['postDisclosureCorrections'],'all prior digest errata retained')
    changed={'lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and all(result['owners'][n]==v for n,v in old['owners'].items()),'all old history/candidate215/cost/domain/formal/metadata semantics unchanged')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
