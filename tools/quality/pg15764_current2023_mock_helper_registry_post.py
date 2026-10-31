"""Independent no-recount registry derivation for two additional helper Source measurements."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15762_current2023_mock_helper_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,read,require
PIN='8c2d3069736a32b9154f030a14f6ca8274e2f4059a3f5507f67f778cbd277bb8'
OUT=data.BASE/'PG15764-current2023-mock-helper-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old,prior,p,q,m=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT,('PG15762-current2023-mock-helper-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and q['semanticNegativeVectors']==35,'genuine predecessor/current independent proof')
    require(q['registeredOriginalMethodsReferencedOnly'] is True and q['newTests']==q['newProductExecutions']==q['newUniqueMethods']==0 and {(c['classname'],c['name']) for c in p['cases']}<={(c['classname'],c['name']) for c in old['cases']},'twelve registered cases referenced, zero new execution')
    require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticFixtureCredentialsUsed'] is q['publicSyntheticFixtureCredentialsUsed'] is True and p['cryptoOperationKind']==q['cryptoOperationKind']=='UUID_V4_PUBLIC_REQUEST_EVENT_IDENTIFIERS_ONLY' and p['effectDisclosureCorrection']==q['effectDisclosureCorrection'],'effective original runtime disclosure, no secret operations')
    units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners'])
    for name,u in p['fullSourceUnits'].items():
        require(name not in units and u['physical']==[name] and u['four100'] is u['branchNaturallyZero'] is False,'new two incomplete closures')
        units[name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    for path,row in p['owners'].items():
        require(path not in owners or owners[path]==row,'old owners unchanged');owners[path]=copy.deepcopy(row)
    scope=copy.deepcopy(old['additionalScopeReferences'])
    scope.append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=0,newExecs=0,newSourceMeasurements=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],originalQualifiedPostReference=p['originalQualifiedPostReference'],scope='NEW_SOURCE_MEASUREMENT_FROM_PREVIOUSLY_REGISTERED_SAME_SOURCE_EXEC_NO_PRODUCT_REPLAY',coverageExecUnion=False))
    physical={n for u in units.values() for n in u['physical']};incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    summary=copy.deepcopy(prior['summary']);summary.update(uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-old['metadataClasses'].keys()),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['originalExecs'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['naturalZeroBranchSourcePrograms'],summary['metadataPhysical'],summary['incompleteSourcePrograms'],len({n for name in incomplete for n in units[name]['physical']}))==(2023,266,112,113,2131,449,593,569,247,360,173,24,23,39),'exact typed measurement versus runtime separation')
    require(summary['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=364,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=151),'two new Main only')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','lastUpdateKind','fullSourceUnits','owners','additionalScopeReferences',*summary}
    def contract(v):
        require(v['lastUpdateKind']=='CURRENT_SOURCE_ADDITIONAL_MEASUREMENT_FROM_REGISTERED_EXEC_NO_NEW_PRODUCT_RUN','only measurement marker')
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived counters')
        require(wire(v['fullSourceUnits'])==wire(units) and wire(v['owners'])==wire(owners) and wire(v['additionalScopeReferences'])==wire(scope),'complete old/new sources/owners and no-count reference')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'immutable predecessor')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'old cases/JVM/JS/history/cost/corrections untouched')
    contract(m);negative=[]
    for key,value in [('tests',2024),('suites',0),('originalExecs',0),('totalProductExecs',114),('totalMethodExecutions',2143),('uniqueProductMethodDelta',1),('newTestIds',12),('sourceProgramDelta',0),('measuredSourcePrograms',447),('measuredPhysical',591),('executablePhysical',567),('metadataPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('naturalZeroBranchSourcePrograms',0),('metadataSourcePrograms',0),('fullSourceUnits',{}),('metadataClasses',{}),('cases',[]),('originalPostReferences',[]),('additionalScopeReferences',[]),('owners',{}),('unknownOwnerPaths',0),('ownerStatusCounts',{}),('priorSource0061TestsTransferred',True),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',75),('uniqueProductMethodDelta',True)]:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false no-recount registry accepted '+key)
    for label in ['typed-counter-bool','typed-four100-int','typed-suite-bool']:
        bad=copy.deepcopy(m)
        if label=='typed-counter-bool':next(iter(bad['fullSourceUnits'].values()))['counters']['LINE']['missed']=False
        elif label=='typed-four100-int':next(u for u in bad['fullSourceUnits'].values() if u['four100'] is True)['four100']=1
        else:next(r for r in bad['originalPostReferences'] if r['suites']==1)['suites']=True
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('typed role alias '+label)
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=2,newUniqueMethods=0,newIncompleteSources=2,newIncompletePhysical=2,incompletePhysicalClasses=39,newProductExecutions=0,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
