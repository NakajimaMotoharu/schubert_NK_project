"""Independent disclosure-only registry join; old proofs immutable, effective public-ID flag corrected."""
import copy
import json
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16625_current2315_morning_disclosure_registry_v2 import SOURCE,PREV,PREV_POST,ERR,KEY,read,require
PIN='02fad496c50898ffec03a3489b705a60277b87c7d939fbfd73d992939bca455d'
OUT=data.BASE/'PG16629-current2315-morning-disclosure-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,e,m=[read(v) for v in [PREV,PREV_POST,ERR,('PG16625-current2315-morning-disclosure-registry-v2',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,e,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and e['originalPost'][1]==KEY and e['metadataNegativeVectors']==8,'actual independent chain')
    effect=dict(effectivePublicSyntheticUuidFixture=True,effectiveSyntheticIdentifiersFromFixedPublicFixtures=True,effectiveLiveIdentifierUsedAsTestInput=False,actualAuthenticationOrSessionIssued=False,actualSecretKeysLoaded=False,interpretation='FIXED_PUBLIC_PROOF_IDS_NOT_LIVE_BOOT_SESSION_PERMIT_OR_AUTHORITY')
    require(wire(e['effectiveDisclosure'])==wire(effect),'independent explicit effective disclosure')
    fields={'boot_id','epoch_id','run_id','activation_id','morning_invocation_id','broker_invocation_id'}
    require(len(e['independentGoldenFileHashes'])==3,'three original fixed golden inputs')
    for path,pin in e['independentGoldenFileHashes'].items():
        blob=(data.ROOT/path).read_bytes();require(data.sha(blob)==pin,'independent fixed input hash');observed=set()
        for line in blob.decode('ascii').splitlines():
            key,sep,value=line.partition('=')
            if key in fields:require(sep and key not in observed,'one typed field');uuid.UUID(value);observed.add(key)
        require(observed==fields and e['observedSyntheticUuidFieldNames'][path]==sorted(fields),'original synthetic identity fields, not live values')
    expected=copy.deepcopy(old)
    expected['postDisclosureCorrections'][KEY]=dict(bug='BUG2184',horizontal='YKT1931',manifest=str((data.BASE/ERR[0]/'manifest.json').relative_to(data.ROOT)),sha256=ERR[1],originalPostSha256=KEY,effectiveDisclosure=effect,originalQualificationAndCountersUnchanged=True)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),sourceProgramDelta=0,uniqueProductMethodDelta=0,lastUpdateKind='POST_DISCLOSURE_ERRATUM_ONLY_NO_CASE_OR_COUNTER_ADDITION')
    def contract(v):require(wire(v)==wire(expected),'exact old/new metadata object, only qualified erratum added')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('uniqueProductMethodDelta',1),('newTestIds',True),('sourceProgramDelta',1),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',[]),('fullSourceUnits',{}),('metadataClasses',{}),('owners',{}),('resourceOnlyJavaMethods',0),('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('originalPostReferences',[])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false registry '+key)
    for key,value in [('ordinaryCaseReferences',0),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary domain')
    extra=[]
    for key,value in [('effectivePublicSyntheticUuidFixture',False),('effectiveLiveIdentifierUsedAsTestInput',True),('actualSecretKeysLoaded',True)]:
        bad=copy.deepcopy(m);bad['postDisclosureCorrections'][KEY]['effectiveDisclosure'][key]=value
        try:contract(bad)
        except ValueError:extra.append(key)
        else:raise ValueError('false effective disclosure')
    require(len(labels)==34 and len(extra)==3,'finite independent metadata/effect negatives')
    for v in [old,prior,e,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,disclosureNegativeVectors=len(extra),disclosureNegativeLabels=extra,newUniqueMethods=0,newSourcePrograms=0,newPhysicalClasses=0,newMetadataPhysical=0,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=m['currentOrdinaryTestDeclarationReference'],newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
