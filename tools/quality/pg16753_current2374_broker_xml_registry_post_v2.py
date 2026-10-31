"""Independent resource-only addition; all Main units, four counters and prior histories identical."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16734-current2370-schema-history-registry-v1','7abb04160133704f8dbd39e97938e3de2a21ef266adbc1651e167cc742ce6629')
PREV_POST=('PG16736-current2370-schema-history-registry-post-v1','9a0de2c13a3806d11e97b5eeca2754e2a533aeece025f5a464ab9c8298ce2357')
REF=('PG16746-broker-public-xml-original-four-post-v1','5c37aba56045083bd233f903ce9c71da54881ddd369dd2751cc7d6c4ef15daa5')
DOMAIN='RESOURCE_PUBLIC_BROKER_XML_PARSER_CONTRACTS'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
PIN='afa9060c34781dc13ea5bc9ad56554b00bc0df56f906c6bb877e97b043aa1399'
OUT=data.BASE/'PG16753-current2374-broker-xml-registry-post-v2'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,m=[read(v) for v in [PREV,PREV_POST,REF,('PG16750-current2374-broker-xml-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and (p['tests'],p['suites'],p['javaSourceProgramsQualified'],p['productionMainTrueProbeHits'])==(4,1,0,0),'genuine resource-only and prior independent chain')
    q=read(('PG16748-broker-public-xml-original-four-independent-v1','b8718bf5cbaf8e391f043880944a1160d5fda7bf91f40e45abb1dde069965a9d'))
    require(q['actualExit']==0 and q['source']==SOURCE and q['postSha256']==REF[1] and q['semanticNegativeVectors']==47 and q['independentOracleGroups']==4 and q['originalMutationCanaries']==0 and p['productionMainRecordsObserved']==[] and p['ownSyntaxParserInvocationsDeclared']==1,'independent closed resource text-only proof')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/REF[0]/name).read_bytes();require(data.sha(blob)==pin,'exact copied XML');xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for c in xml.findall('testcase'):require(not list(c),'no nonpass');actual.append((c.get('classname'),c.get('name')))
    added=set(actual);before={(v['classname'],v['name']) for v in old['cases']};names=before|added
    require(len(actual)==len(added)==4 and not added&before,'four new original methods')
    expected=copy.deepcopy(old);expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=4,newTestIds=0,sourceProgramDelta=0,lastUpdateKind='CURRENT_SOURCE_RESOURCE_ONLY_ORIGINAL_METHODS_NO_MAIN_COUNTER_CREDIT')
    for key,delta in [('tests',4),('suites',1),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',4),('resourceOnlyJavaMethods',4)]:expected[key]=old[key]+delta
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical/candidate owners')
        require(path not in old['owners'] or old['owners'][path]==row,'all previous owners same');expected['owners'][path]=copy.deepcopy(row)
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()));expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())

    expected['resourceOnlyReferences'].append(dict(name=REF[0],sha256=REF[1],tests=4,suites=1,domain=DOMAIN,javaSourceProgramsQualified=0,actualBrowser=False))
    decl=expected['currentOrdinaryTestDeclarationReference'];inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2355 and len(names-ordinary)==19,'new original resource cases in ordinary declarations, quality19 unchanged')
    decl.update(ordinaryCaseReferences=2355,ordinaryWithoutCurrentCaseReference=3431,existingQualityFixtureCases=19)
    require((expected['tests'],expected['suites'],expected['resourceOnlyJavaMethods'],expected['measuredSourcePrograms'],expected['measuredPhysical'],expected['four100SourcePrograms'],expected['totalProductExecs'],expected['totalMethodExecutions'])==(2374,333,53,521,812,281,158,2506),'actual mixed method counts versus unchanged Main')
    def contract(v):require(wire(v)==wire(expected),'exact old/new whole object, no Main/counter/cost/formal credit')
    contract(m);negative=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('uniqueProductMethodDelta',0),('newTestIds',True),('sourceProgramDelta',1),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',{}),('metadataClasses',{}),('owners',old['owners']),('resourceOnlyJavaMethods',0),('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('originalPostReferences',[])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false resource registry '+key)
    for key,value in [('ordinaryCaseReferences',2178),('ordinaryWithoutCurrentCaseReference',3608),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:negative.append('ordinary-'+key)
        else:raise ValueError('false ordinary resource domain')
    require(len(negative)==34,'finite34 negatives')
    def chain_contract(a,b,c):
        require(m['previousUniqueRegistryReference']==list(a) and m['previousRegistryPostReference']==list(b) and m['resourceOnlyReferences'][-1]['name']==c[0] and m['resourceOnlyReferences'][-1]['sha256']==c[1],'exact current predecessor and resource binding')
    chain_contract(PREV,PREV_POST,REF);chain_labels=[]
    for label,a,b,c in [('previous',('WRONG',PREV[1]),PREV_POST,REF),('post',PREV,('WRONG',PREV_POST[1]),REF),('resource',PREV,PREV_POST,('WRONG',REF[1]))]:
        try:chain_contract(a,b,c)
        except ValueError:chain_labels.append(label)
        else:raise ValueError('wrong chain accepted '+label)
    summary={key:m[key] for key in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=34,negativeLabels=negative,chainBindingNegativeVectors=len(chain_labels),chainBindingNegativeLabels=chain_labels,newUniqueMethods=4,newSourcePrograms=0,newPhysicalClasses=0,newMetadataPhysical=0,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,resourceOnlyOriginalMethods=m['resourceOnlyJavaMethods'],publicConfigurationTemplates=1,javaMainCoverageCreditAdded=0,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
