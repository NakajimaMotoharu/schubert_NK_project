"""Original synthetic JMS guard six current-source addition; preserve all previous proof/history/effects."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15508-current1844-credentialfree-factory-values-registry-v1','394b7af6c45830184e1c8d84f33f4fde096041eede2862b485dc280f380d6842')
PREV_POST=('PG15510-current1844-credentialfree-factory-values-registry-post-v1','9a607f04642cc778ac19ba66070711261286ae4e6f75aae1057806477b981681')
REFS=[['PG15520-synthetic-jms-guard-six-post-v1','77b9c0aa0bec563c180c66f3de6e81fc108e9b604c068bbc77f4e49242f2bdcb','PG15522-synthetic-jms-guard-six-independent-v1','037c35e1f7e15efb0d8823ea39c2dd1b10cc5a1ac829ab82170a657732a8f4fd',6,24]]
OUT=data.BASE/'PG15524-current1850-synthetic-jms-guard-registry-v1'
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
        require((q['sourcePrograms'],q['physicalClasses'],q['four100SourcePrograms'],q['naturallyBranchZeroSourcePrograms'],q['incompleteSourcePrograms'],q['baselineMainOwnerRows'],q['unknownTestOwnerRows'])==(2,2,1,1,0,2,1),'exact per-program categories')
        require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is p['actualSecretKeysLoaded'] is q['actualSecretKeysLoaded'] is False and p['ownFreshJvmProviderStateOnly'] is q['ownFreshJvmProviderStateOnly'] is True,'no crypto/actual keys/own child only')
        require(p['onlySyntheticJmsProxyMessages'] is q['onlySyntheticJmsProxyMessages'] is p['jmsDestinationValueObjectsConstructed'] is q['jmsDestinationValueObjectsConstructed'] is True and p['actualJmsConnectionsCreated']==q['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==q['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is q['actualBrokerOrListenerStarted'] is p['actualFilesOpenedByProduct'] is q['actualFilesOpenedByProduct'] is p['actualCredentialValuesUsed'] is q['actualCredentialValuesUsed'] is p['jmsFactoryObjectsConstructed'] is q['jmsFactoryObjectsConstructed'] is False,'only synthetic proxies/destinations, no broker/files/credentials/factory')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'new distinct current cases/full Code only');cases|=new
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name],'whole new Source closure')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,row in p['owners'].items():
            require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual new canonical rows, not change-owner inference')
            require(path not in result['owners'] or result['owners'][path]==row,'all shared owner rows preserved');result['owners'][path]=copy.deepcopy(row)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_SYNTHETIC_JMS_GUARD6_FULL_TWO_SOURCE_ONE_FOUR100_ONE_NATURAL'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(incomplete)==10 and len({p for n in incomplete for p in units[n]['physical']})==17,'disjoint whole Source closures and actual incomplete7/12')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+6,uniqueProductMethodDelta=6,newTestIds=6,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({p for u in units.values() if u['branchNaturallyZero'] for p in u['physical']}),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())),unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(1850,232,397,523,502,219,325,314,98,99,1958,162,175),'exact current17/9Source/10physical classification')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=312,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=116),'old215 candidates preserved/new9baseline5UNKNOWN')
    result['lastUpdateKind']='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED'
    require(result['postDisclosureCorrections']==old['postDisclosureCorrections'] and result['postDisclosureCorrections'],'all prior digest errata retained')
    changed={'lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and all(result['owners'][n]==v for n,v in old['owners'].items()),'all old history/candidate215/cost/domain/formal/metadata semantics unchanged')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
