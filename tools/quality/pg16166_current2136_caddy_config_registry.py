"""Add three original cases, retaining all previous source qualifications without exec union."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16088-current2133-canonical-aad-registry-v1','b6e7dc918a723fd30965322bc8400e51a786872204ea72a99f3e9b18534e30b7')
PREV_POST=('PG16090-current2133-canonical-aad-registry-post-v1','f69775f5fdd046ed2850f400d9cdf40049fefb8905085e36a039cb402f520523')
POST=('PG16162-caddy-config-three-post-v1','241833934d3a7e7779b84a9515f1390799e348eb0a47eb002668245dea2f1bed')
INDEPENDENT=('PG16165-caddy-config-three-independent-v2','f797aaa8adcd6d8192a6d0a33b373b1387b6f5b3cc5ed4c709fb4c1e38612066')
OUT=data.BASE/'PG16166-current2136-caddy-config-registry-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q))
            and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34
            and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleNegativeVectors'],q['provenanceSchemaNegativeVectors'])==(25,5,2),'qualified original chain')
    require((p['tests'],p['suites'])==(3,1) and p['singleSession'] is True and p['crcMismatch']==0
            and p['strictFour100GateExit']==1 and p['normalOrdinaryTestSourceDomain'] is True,'exact original three/partial source')
    require(p['actualFilesOpenedByProduct'] is p['originalTestPublicTemplateRead'] is True
            and p['actualPrivateFilesOpened'] is p['rootMainInvoked'] is p['oldCoverageTransferred'] is False,'explicit original public template read only')
    for name,unit in q['previousSourceProofs'].items():
        require(old['fullSourceUnits'][name]==unit and name in p['fullSourceUnits'],'previous whole-source proof unchanged')
    before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==3 and not added&before and all(v['result']=='PASS' for v in p['cases']),'three new original references')
    result=copy.deepcopy(old);cases=before|added
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),
        cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),
        originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+3,
        uniqueProductMethodDelta=3,newTestIds=3,sourceProgramDelta=0,
        lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=3,suites=1,execSha256=p['execSha256'],
        sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PUBLIC_CONFIG3_SUPPLEMENTAL_MEASUREMENT_NO_SOURCE_REPLACEMENT'))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=3,newExecs=1,
        execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='SUPPLEMENTAL_PUBLIC_CONFIG_PARSER_AND_TEMPLATE_NOT_SOURCE_QUALIFICATION_REPLACEMENT',
        existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False))
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json'])
    normal={(v['className'],v['method']) for v in bindings}
    require(added<=normal and len(cases&normal)==2119 and len(cases-normal)==17,'ordinary declarations not extra fixture')
    decl.update(ordinaryCaseReferences=2119,ordinaryWithoutCurrentCaseReference=3667)
    result['currentOrdinaryTestDeclarationReference']=decl
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs',
        'totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','lastUpdateKind',
        'originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed),'all previous counters/roles/costs/corrections/qualification retained')
    require((result['tests'],result['suites'],result['totalProductExecs'],result['totalMethodExecutions'],result['totalRepeatedOriginalMethods'])
            ==(2136,286,129,2268,132),'new technical only, no repeated or phase acceptance')
    for v in (old,prior,p,q):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result)
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
