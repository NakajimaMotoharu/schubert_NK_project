"""Independent addition of generated values12; all Source qualifications, costs and roles preserved."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15826_current2043_generated_values_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,read,require

PIN='dc8e5ea4115e406ef4951c060586261fce5e189fb92a65c694b2daca56199f85'
OUT=data.BASE/'PG15828-current2043-generated-values-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(isinstance(PIN,str) and len(PIN)==64 and all(c in '0123456789abcdef' for c in PIN),'bound literal digest');require(not OUT.exists(),'new-only1711 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15826-current2043-generated-values-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[];metadata=copy.deepcopy(old['metadataClasses'])
    p,proof=read(POST),read(INDEPENDENT);witnesses.extend([p,proof])
    require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==POST[1] and proof['semanticNegativeVectors']==47 and proof['tests']==12 and proof['newSourcePrograms']==0,'genuine independent original12')
    require(p['sameExecMeasurementSupplementalOnly'] is proof['sameExecMeasurementSupplementalOnly'] is p['previousSourceProofsNotReplaced'] is proof['previousSourceProofsNotReplaced'] is p['onlyGeneratedMetricValueContracts'] is proof['onlyGeneratedMetricValueContracts'] is True,'pure generated semantics separate from Source qualifications')
    require(p['meterRegistryOrRecorderConstructed'] is proof['meterRegistryOrRecorderConstructed'] is p['actualCollectorOrExporterStarted'] is proof['actualCollectorOrExporterStarted'] is p['cryptoOrKeyOperationsInvoked'] is proof['cryptoOrKeyOperationsInvoked'] is p['currentSourceQualificationProofsReplaced'] is False and p['noOuterRecorderMethodInvocations'] is proof['noOuterRecorderMethodInvocations'] is True,'no live operations/crypto/qualification rewrite')
    require(p['singleSession'] is True and p['crcMismatch']==0 and p['strictFour100GateExit']==1 and p['newAccepted']==proof['newAccepted']==0,'not all-source pass')
    require(set(proof['previousSourceProofs'])==set(p['fullSourceUnits']) and wire(proof['previousSourceProofs'])==wire(p['currentTargetPriorSourceProofs']) and all(units[n]==u and u['four100'] is True for n,u in proof['previousSourceProofs'].items()),'all five prior qualified Source proofs unchanged')
    require(p['metadataClasses']==[] and proof['metadataPhysicalClasses']==0 and proof['independentHashVectors']==dict(pool=94248,outbox=3040,max4=0,max3=-2147483648,zero=0),'no NoCode conversion/independent hash overflow vectors')
    new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==12 and not new&methods and all(c['result']=='PASS' for c in p['cases']),'new disjoint thirteen');methods|=new
    for path,row in p['owners'].items():
        require(path not in owners or owners[path]==row,'existing roles unchanged');owners[path]=copy.deepcopy(row)
    refs.append(dict(name=POST[0],sha256=POST[1],tests=12,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_GENERATED_VALUE12_SUPPLEMENTAL_MEASUREMENT_NO_SOURCE_REPLACEMENT'))
    scope_refs=copy.deepcopy(old['additionalScopeReferences'])
    scope_refs.append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=12,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='SUPPLEMENTAL_GENERATED_VALUE_CONTRACTS_NOT_SOURCE_QUALIFICATION_REPLACEMENT',existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False))
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=metadata
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']==31 and len({n for name in incomplete for n in units[name]['physical']})==60,'new measured incomplete partition explicit, no gate relaxation')
    summary=copy.deepcopy(prior['summary']);summary.update(metadataPhysical=len(metadata),incompleteSourcePrograms=len(incomplete),tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+12,uniqueProductMethodDelta=12,newTestIds=12,sourceProgramDelta=0,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(2043,271,458,615,584,247,360,349,117,2151,174,189,6,31),'exact independent category/method/JVM counts')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':373,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':229,'UNKNOWN':154},'actual owners distinct from change group; UNKNOWN retained')
    changed={'lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','additionalScopeReferences','metadataClasses',*summary}
    def contract(v):
        require(v['lastUpdateKind']=='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED' and v['postDisclosureCorrections']==old['postDisclosureCorrections'],'new PT marker and all previous digest errata retained')
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and wire(v['originalPostReferences'])==wire(refs),'all actual old/new cases/whole proof/owner roles')
        require(wire(v['additionalScopeReferences'])==wire(scope_refs),'separate supplemental refs without replacement');require(wire(v['metadataClasses'])==wire(metadata) and v['metadataPhysical']==31,'new explicit NoCode interface and all old metadata retained')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact immutable predecessor')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'old Catalog/SQLjoint/JS/metadata/cost/formal untouched')
    contract(m);negative=[]
    for key,value in [('tests',914),('suites',132),('totalProductExecs',61),('totalMethodExecutions',994),('totalRepeatedOriginalMethods',92),('uniqueProductMethodDelta',0),('sourceProgramDelta',1),('four100SourcePrograms',131),('four100Physical',196),('incompleteSourcePrograms',4),('naturalZeroBranchSourcePrograms',145),('measuredSourcePrograms',287),('measuredPhysical',365),('executablePhysical',347),('metadataPhysical',0),('metadataSourcePrograms',0),('fullSourceUnits',{}),('metadataClasses',{}),('cases',old['cases']),('originalPostReferences',old['originalPostReferences']),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('javascriptResourceDomain',{}),('unknownOwnerPaths',99),('ownerStatusCounts',{'BASELINE_LOGICAL_REFERENCE':283,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':103}),('priorSource0061TestsTransferred',True),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',75),('uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false1697 registry accepted '+key)
    for label in ['typed-counter-bool','typed-four100-int','typed-suite-bool']:
        bad=copy.deepcopy(m)
        if label=='typed-counter-bool':
            next(iter(bad['fullSourceUnits'].values()))['counters']['LINE']['missed']=False
        elif label=='typed-four100-int':
            unit=next(u for u in bad['fullSourceUnits'].values() if u['four100'] is True);unit['four100']=1
        else:
            reference=next(r for r in bad['originalPostReferences'] if r['suites']==1);reference['suites']=True
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('numeric and boolean roles must not alias '+label)
    for v in [old,prior,m,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=0,newUniqueMethods=12,newIncompleteSources=0,newIncompletePhysical=0,incompletePhysicalClasses=60,newProductExecutions=1,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
