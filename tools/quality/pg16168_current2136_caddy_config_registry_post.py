"""Independent original XML delta and preserved source/history reconstruction."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg16166_current2136_caddy_config_registry import SOURCE, PREV, PREV_POST, POST, INDEPENDENT, read, require

PIN='8f4646787f63d7060a25143c36c8250ffc650086d591ce413f5a477f7d8a3842'
OUT=data.BASE/'PG16168-current2136-caddy-config-registry-post-v1'

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT,('PG16166-current2136-caddy-config-registry-v1',PIN))]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q,m))
            and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1]
            and (q['semanticNegativeVectors'],q['independentOracleNegativeVectors'],q['provenanceSchemaNegativeVectors'])==(25,5,2),'qualified chain')
    actual=[]
    for filename,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(blob)==pin,'exact copied originalXML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no failure/skip')
        for node in xml.findall('testcase'):
            require(not list(node),'actual case no nonpass');actual.append((node.get('classname'),node.get('name')))
    old_cases={(v['classname'],v['name']) for v in old['cases']};added=set(actual)
    require(len(actual)==len(added)==3 and not added&old_cases,'three unique new original methods')
    names=old_cases|added;expected=copy.deepcopy(old)
    expected['invocation']=m['invocation'];expected['previousUniqueRegistryReference']=list(PREV);expected['previousRegistryPostReference']=list(PREV_POST)
    expected['cases']=[dict(classname=c,name=n) for c,n in sorted(names)];expected['suiteNames']=sorted({c for c,n in names})
    for key,delta in [('tests',3),('suites',1),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',3)]:expected[key]=old[key]+delta
    expected.update(uniqueProductMethodDelta=3,newTestIds=3,sourceProgramDelta=0,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=3,suites=1,execSha256=p['execSha256'],
        sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PUBLIC_CONFIG3_SUPPLEMENTAL_MEASUREMENT_NO_SOURCE_REPLACEMENT'))
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=3,newExecs=1,
        execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='SUPPLEMENTAL_PUBLIC_CONFIG_PARSER_AND_TEMPLATE_NOT_SOURCE_QUALIFICATION_REPLACEMENT',
        existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False))
    decl=expected['currentOrdinaryTestDeclarationReference'];inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    declarations=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in declarations}
    require(added<=ordinary and len(names&ordinary)==2119 and len(names-ordinary)==17,'new original declarations, no fixture mixing')
    decl.update(ordinaryCaseReferences=len(names&ordinary),ordinaryWithoutCurrentCaseReference=len(ordinary-names))
    require((expected['tests'],expected['suites'],expected['totalProductExecs'],expected['totalMethodExecutions'],
             decl['ordinaryCaseReferences'],decl['ordinaryWithoutCurrentCaseReference'])==(2136,286,129,2268,2119,3667),'independently derived counts')
    require(all(old['fullSourceUnits'][name]==row for name,row in q['previousSourceProofs'].items())
            and p['strictFour100GateExit']==1 and p['originalTestPublicTemplateRead'] is True
            and p['actualPrivateFilesOpened'] is False,'whole-source old qualification kept, new publicfile read explicit')
    def contract(value):
        require(wire(value)==wire(expected),'exact old/new independent whole object; no silent domain/history changes')
    contract(m);negative=[]
    vectors=[('tests',2133),('suites',285),('originalExecs',127),('totalProductExecs',128),('totalMethodExecutions',2265),
        ('totalRepeatedOriginalMethods',135),('uniqueProductMethodDelta',0),('newTestIds',True),('sourceProgramDelta',1),
        ('measuredSourcePrograms',478),('measuredPhysical',663),('four100SourcePrograms',259),('four100Physical',377),
        ('incompleteSourcePrograms',36),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),
        ('cases',old['cases']),('fullSourceUnits',{}),('metadataClasses',{}),('owners',{}),('ownerStatusCounts',{}),
        ('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),
        ('additionalScopeReferences',old['additionalScopeReferences']),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),
        ('originalPostReferences',old['originalPostReferences'])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false registry accepted '+key)
    for key,value in [('ordinaryCaseReferences',2116),('ordinaryWithoutCurrentCaseReference',3670),('existingQualityFixtureCases',20),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:negative.append('ordinary-'+key)
        else:raise ValueError('false ordinary count')
    require(len(negative)==34,'finite34 negative vectors')
    summary=copy.deepcopy(prior['summary'])
    for key in summary:summary[key]=m[key]
    for v in (old,prior,p,q,m):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,
        summary=summary,metadataNegativeVectors=34,negativeLabels=negative,newUniqueMethods=3,newSourcePrograms=0,
        previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,
        currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,
        whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
