"""Add two honest helper Source measurements from a registered exec; no new methods or Product run."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15748-current2023-mq-login-registry-v1','446c25131764958017d939cf9fabb6373a8b144822badccb388d839857ffb932')
PREV_POST=('PG15750-current2023-mq-login-registry-post-v1','24e87fc48eeeeff20e16afa8d791cd673e320b3a475c3cec404c2ec13e2c3fca')
POST=('PG15759-registered-mock-helper-measurement-post-v2','a11c2bc0601ce48308b82bd5573fa8c23183833923ec5308a7d551b4517f6d20')
INDEPENDENT=('PG15760-registered-mock-helper-independent-v1','546e31b389488b4ed3534db911d97466978a58d02e54c3e353b24b2e9cab622d')
OUT=data.BASE/'PG15762-current2023-mock-helper-registry-v1'
def require(ok,label):
    if not ok:raise ValueError(label)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old,prior,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'exact qualified predecessor')
    require(q['postSha256']==POST[1] and q['semanticNegativeVectors']==35 and (q['newTests'],q['newProductExecutions'],q['newUniqueMethods'],q['sourcePrograms'],q['physicalClasses'],q['incompleteSourcePrograms'])==(0,0,0,2,2,2),'independent same-exec measurement only')
    require(q['registeredOriginalMethodsReferencedOnly'] is p['originalRegisteredCasesNotRecounted'] is p['sameSourcePriorExecAdditionalMeasurement'] is True and q['cryptoOrKeyOperationsInvoked'] is p['cryptoOrKeyOperationsInvoked'] is q['publicSyntheticFixtureCredentialsUsed'] is p['publicSyntheticFixtureCredentialsUsed'] is True and q['cryptoOperationKind']==p['cryptoOperationKind']=='UUID_V4_PUBLIC_REQUEST_EVENT_IDENTIFIERS_ONLY','truthful effects and no recount')
    require(p['effectDisclosureCorrection']==q['effectDisclosureCorrection'] and all(q[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct']),'corrected metadata only, actual secrets/authority zero')
    require({(c['classname'],c['name']) for c in p['cases']}<={(c['classname'],c['name']) for c in old['cases']},'all original cases already counted')
    result=copy.deepcopy(old);units=result['fullSourceUnits']
    for name,u in p['fullSourceUnits'].items():
        require(name not in units and len(u['physical'])==1 and u['physical']==p['completeSourceUnitClosure'][name] and u['four100'] is u['branchNaturallyZero'] is False,'two new incomplete whole sources')
        units[name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(data.sha((data.ROOT/path).read_bytes())==row['sha256'] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual Source ownership')
        require(path not in result['owners'] or result['owners'][path]==row,'existing Test owners unchanged');result['owners'][path]=copy.deepcopy(row)
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=0,newExecs=0,newSourceMeasurements=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],originalQualifiedPostReference=p['originalQualifiedPostReference'],scope='NEW_SOURCE_MEASUREMENT_FROM_PREVIOUSLY_REGISTERED_SAME_SOURCE_EXEC_NO_PRODUCT_REPLAY',coverageExecUnion=False))
    physical={n for u in units.values() for n in u['physical']};meta=result['metadataClasses'];incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ADDITIONAL_MEASUREMENT_FROM_REGISTERED_EXEC_NO_NEW_PRODUCT_RUN')
    require((result['tests'],result['suites'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['measuredSourcePrograms'],result['measuredPhysical'],result['executablePhysical'],result['incompleteSourcePrograms'],len({n for name in incomplete for n in units[name]['physical']}))==(2023,266,112,113,2131,449,593,569,23,39),'only Source measurements grow, no PT/JVM count inflation')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=364,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=151),'two Main owners only')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','ownerStatusCounts','unknownOwnerPaths','measuredSourcePrograms','measuredPhysical','executablePhysical','incompleteSourcePrograms','lastUpdateKind','additionalScopeReferences'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old cases/JVM/proofs/cost/domain/corrections intact')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
