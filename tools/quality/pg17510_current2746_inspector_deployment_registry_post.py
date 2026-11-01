"""Independent resource-only addition; all Main units, four counters and prior histories identical."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg17508_current2746_inspector_deployment_registry import SOURCE,PREV,PREV_POST,REF,DOMAIN,read,require
PIN='eb7902fee60aaf3966019a81ce70ffde89e1d070181fa83264508fc381f6de6a'
OUT=data.BASE/'PG17510-current2746-inspector-deployment-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,m=[read(v) for v in [PREV,PREV_POST,REF,('PG17508-current2746-inspector-deployment-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and (p['tests'],p['suites'],p['javaSourceProgramsQualified'],p['parentProductionMainTrueProbeHits'])==(8,1,0,0),'genuine resource-only and prior independent chain')
    require(p['parentCoverageScopeOnly'] is True and p['childJavaCoverageClaimed'] is False and p['ownJavaChildCount']==1 and p['publicToolReceiptCount']==50 and p['methodCatalogNegativeVectors']==3,'explicit child/parent measurement separation')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/REF[0]/name).read_bytes();require(data.sha(blob)==pin,'exact copied XML');xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for c in xml.findall('testcase'):require(not list(c),'no nonpass');actual.append((c.get('classname'),c.get('name')))
    added=set(actual);before={(v['classname'],v['name']) for v in old['cases']};names=before|added
    require(len(actual)==len(added)==8 and not added&before,'four new original methods')
    expected=copy.deepcopy(old);expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=8,newTestIds=0,sourceProgramDelta=0,lastUpdateKind='CURRENT_SOURCE_RESOURCE_ONLY_ORIGINAL_METHODS_NO_MAIN_COUNTER_CREDIT')
    for key,delta in [('tests',8),('suites',1),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',8),('resourceOnlyJavaMethods',8)]:expected[key]=old[key]+delta
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical/candidate owners')
        require(path not in old['owners'] or old['owners'][path]==row,'all previous owners same');expected['owners'][path]=copy.deepcopy(row)
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()));expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    require(expected['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=496,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=234,UNKNOWN=285),'actual owner categories')
    expected['resourceOnlyReferences'].append(dict(name=REF[0],sha256=REF[1],tests=8,suites=1,domain=DOMAIN,javaSourceProgramsQualified=0,actualBrowser=False,ownUnadmittedCliChild=1,childJavaCoverageQualified=False,originalPublicToolReceipts=50))
    decl=expected['currentOrdinaryTestDeclarationReference'];inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2727 and len(names-ordinary)==19,'new original resource cases in ordinary declarations, quality19 unchanged')
    decl.update(ordinaryCaseReferences=2727,ordinaryWithoutCurrentCaseReference=3059,existingQualityFixtureCases=19)
    require((expected['tests'],expected['suites'],expected['resourceOnlyJavaMethods'],expected['measuredSourcePrograms'],expected['measuredPhysical'],expected['four100SourcePrograms'],expected['totalProductExecs'],expected['totalMethodExecutions'])==(2746,404,79,559,982,289,200,2878),'actual mixed method counts versus unchanged Main')
    def contract(v):require(wire(v)==wire(expected),'exact old/new whole object, no Main/counter/cost/formal credit')
    contract(m);negative=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('uniqueProductMethodDelta',0),('newTestIds',True),('sourceProgramDelta',1),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',{}),('metadataClasses',{}),('owners',old['owners']),('resourceOnlyJavaMethods',0),('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('originalPostReferences',[])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false resource registry '+key)
    for key,value in [('ordinaryCaseReferences',2620),('ordinaryWithoutCurrentCaseReference',3166),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:negative.append('ordinary-'+key)
        else:raise ValueError('false ordinary resource domain')
    require(len(negative)==34,'finite34 negatives')
    summary={key:m[key] for key in prior['summary']}
    for v in [old,prior,p,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=34,negativeLabels=negative,newUniqueMethods=8,newSourcePrograms=0,newPhysicalClasses=0,newMetadataPhysical=0,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,resourceOnlyOriginalMethods=79,publicDeclarationInputs=5,ownUnadmittedCliChild=1,childJavaCoverageQualified=False,originalPublicToolReceipts=50,javaMainCoverageCreditAdded=0,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
