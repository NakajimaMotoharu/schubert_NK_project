"""Current-source original Hasher3 plus public value18; preserve exact old proof/cost/owners."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15442-current1810-auth-context-codec-registry-v1','e94941427a78ea47d0b82eabbcffd19400909efb16b939c3216a30cc6aed897c')
PREV_POST=('PG15444-current1810-auth-context-codec-registry-post-v1','c886784d0fbfe94c9e2bd7a29a10fcbab04d901960aa7125f5ea7fd997caec32')
REFS=[['PG15454-password-hasher-three-post-v1','20b1787d8803c86bb0f3c65de60bbe74e063ad60156e860ae230ad86ba4fba91','PG15456-password-hasher-three-independent-v1','8a66fcf52b2a47ab4c07d79f20fde3c830f582cddd76449e22d1719b71d43bd1',3,35],['PG15460-public-value-eighteen-post-v1','b316e19d53bb71007e4442a6d835feedfae2a55201197fe89e4478796427e5b8','PG15462-public-value-eighteen-independent-v1','c5277dc239be507ed1562d039e9ae3c94fd880a10e133566d33033c18a69cc9d',18,36]]
OUT=data.BASE/'PG15464-current1831-hasher-public-value-registry-v1'
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
        require((q['sourcePrograms'],q['physicalClasses'],q['four100SourcePrograms'],q['naturallyBranchZeroSourcePrograms'],q['incompleteSourcePrograms'],q['baselineMainOwnerRows'],q['unknownTestOwnerRows'])==((1,1,1,0,0,1,1) if count==3 else (6,6,4,2,0,6,4)),'exact per-program categories')
        require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is True and p['actualSecretKeysLoaded'] is q['actualSecretKeysLoaded'] is False and p['ownFreshJvmProviderStateOnly'] is q['ownFreshJvmProviderStateOnly'] is True,'dedicated truthful synthetic AES/child-only JCA, no actual secrets')
        if count==3:
            require(p['publicSyntheticTestPasswordsUsed'] is q['publicSyntheticTestPasswordsUsed'] is True and p['cryptoOperationKind']=='PBKDF2_HMACSHA256_PUBLIC_SYNTHETIC_PASSWORD_AND_SALT','public synthetic password profile')
        else:
            require(count==18 and p['publicReceiptIdentifierRandomnessOnly'] is q['publicReceiptIdentifierRandomnessOnly'] is p['testOwnNewSlotPublicEvidenceWrites'] is q['testOwnNewSlotPublicEvidenceWrites'] is True and p['forbiddenProductProbeHits']==q['forbiddenProductProbeHits']==0 and p['cryptoOperationKind']=='CSPRNG_PUBLIC_RECEIPT_IDENTIFIER_ONLY_NO_KEYS','own public receipt entropy/output profile')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'new distinct current cases/full Code only');cases|=new
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name],'whole new Source closure')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,row in p['owners'].items():
            require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual new canonical rows, not change-owner inference')
            require(path not in result['owners'] or result['owners'][path]==row,'all shared owner rows preserved');result['owners'][path]=copy.deepcopy(row)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PASSWORD_HASHER3_FULL_ONE_SOURCE_PUBLIC_SYNTHETIC_PASSWORD' if count==3 else 'ORIGINAL_PUBLIC_VALUES18_FULL_SIX_SOURCE_PUBLIC_IDENTIFIER_ENTROPY_OWN_PUBLIC_TEST_OUTPUTS'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(incomplete)==8 and len({p for n in incomplete for p in units[n]['physical']})==13,'disjoint whole Source closures and actual incomplete7/12')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+2,totalProductExecs=old['totalProductExecs']+2,totalMethodExecutions=old['totalMethodExecutions']+21,uniqueProductMethodDelta=21,newTestIds=21,sourceProgramDelta=7,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({p for u in units.values() if u['branchNaturallyZero'] for p in u['physical']}),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())),unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(1831,226,392,516,495,218,324,313,95,96,1939,160,173),'exact current17/9Source/10physical classification')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=307,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=110),'old215 candidates preserved/new9baseline5UNKNOWN')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and all(result['owners'][n]==v for n,v in old['owners'].items()),'all old history/candidate215/cost/domain/formal/metadata semantics unchanged')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
