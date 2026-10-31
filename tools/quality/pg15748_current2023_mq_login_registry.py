"""Add original memory Login14 and four fully covered whole sources without real authority."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15732-current2009-recovery-values-registry-v1','66b317c50586b44e39d8a7b7e0f175184d151554c7e7d2c9bfb0d3650e6c7bfa')
PREV_POST=('PG15734-current2009-recovery-values-registry-post-v1','a718f73c9b82331f988f145479fc2073f4c0c84bfdd00d26d84d8270cb9bac32')
REFS=[["PG15744-mq-login-memory-fourteen-post-v1","8778a987b1616cd6ab2b6d998202e0ebefb54762f62a32a13b5c9785a2aa77d9","PG15746-mq-login-memory-fourteen-independent-v1","de73a35736d836aaf9d9a492117d9c2693ee6cc381197d642dccfa92b2ab0752",14,38]]
OUT=data.BASE/'PG15748-current2023-mq-login-registry-v1'
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
        require((q['sourcePrograms'],q['physicalClasses'],q['four100SourcePrograms'],q['naturallyBranchZeroSourcePrograms'],q['incompleteSourcePrograms'],q['baselineMainOwnerRows'],q['unknownTestOwnerRows'])==(4,5,4,0,0,9,3),'exact per-program categories')
        require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is p['actualSecretKeysLoaded'] is q['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is q['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is q['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is q['actualFilesOpenedByProduct'] is False,'memory callbacks/exception values, not crypto or live IO')
        require(p['previousHelpersNotReaccepted'] is q['previousHelpersNotReaccepted'] is True and wire(p['helperPreviousSourceProofs'])==wire(q['previousHelperProofs']) and len(q['previousHelperProofs'])==5 and all(old['fullSourceUnits'][n]==u for n,u in q['previousHelperProofs'].items()),'all three old helper proofs unchanged')
        require(p['publicSyntheticFixtureCredentialsUsed'] is q['publicSyntheticFixtureCredentialsUsed'] is p['syntheticLocalSpringAuthenticationObjectsCreated'] is q['syntheticLocalSpringAuthenticationObjectsCreated'] is True and p['valueBearingWireSaved'] is q['valueBearingWireSaved'] is False and q['actualHttpSessionsIssued']==q['actualApiAuthenticationGrantsIssued']==0 and q['specNegativeVectors']==1,'synthetic local objects explicit, real authority zero and spec correction qualified')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'new distinct current cases/full Code only');cases|=new
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name],'whole new Source closure')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,row in p['owners'].items():
            require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual new canonical rows, not change-owner inference')
            require(path not in result['owners'] or result['owners'][path]==row,'all shared owner rows preserved');result['owners'][path]=copy.deepcopy(row)
        for n in p['metadataClasses']:
            require(n not in result['metadataClasses'] and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new exact NoCode mapper')
            result['metadataClasses'][n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_MQ_LOGIN_MEMORY14_FOUR_WHOLE_SOURCE_FIVE_CODE_FOUR100'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(incomplete)==21 and len({p for n in incomplete for p in units[n]['physical']})==37,'disjoint whole Source closures and actual incomplete7/12')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+14,uniqueProductMethodDelta=14,newTestIds=14,sourceProgramDelta=4,measuredSourcePrograms=len(units),measuredPhysical=len(physical),metadataPhysical=len(meta),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({p for u in units.values() if u['branchNaturallyZero'] for p in u['physical']}),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())),unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(2023,266,447,591,567,247,360,349,112,113,2131,173,188),'exact current17/9Source/10physical classification')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=362,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=151),'old215 candidates preserved/new9baseline5UNKNOWN')
    result['lastUpdateKind']='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED'
    require(result['postDisclosureCorrections']==old['postDisclosureCorrections'] and result['postDisclosureCorrections'],'all prior digest errata retained')
    changed={'lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','metadataClasses','metadataPhysical'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and all(result['owners'][n]==v for n,v in old['owners'].items()),'all old history/candidate215/cost/domain/formal/metadata semantics unchanged')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
