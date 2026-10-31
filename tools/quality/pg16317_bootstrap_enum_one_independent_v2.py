"""Independent public enum catalogs/schema and honest whole-Source incomplete denominator."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16314-bootstrap-enum-one-post-v1','5352afbe2d27ab0e54e1c3a50cced48fde15950a58994290e215547493a6d87e')
RAW=('PG16312-bootstrap-enum-one-pt-v1','4873fb1aaec0b2a2c53fefee8664d29721d2a88760ccae21a9589d3b3f8c423f')
PREV=('PG16302-current2172-inspection-registry-v1','000254c960de391f58918a11980b7cc1c62f3fa1cfdabb95188f3ada22d95254')
AES='dev/codex/schubert/nk/api/file/AesCredentialFile'
MANAGER='dev/codex/schubert/nk/bootstrap/SystemManagerObservation'
OUT=data.BASE/'PG16317-bootstrap-enum-one-independent-v2'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,old)),'genuine source chain')
    path=data.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/EnumValueCatalogCompatibilityTest.java';body=path.read_bytes();text=body.decode()
    require(data.sha(body)==raw['begin']['testSourceHashes'][str(path)]=='da1b6cfec2530e07f7d083906901d80d69279ac926642356d14afa31fb0c57fc','whole original fixed Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(methods==['bst001CredentialAndServiceIdentifiersRetainTheirLiteralCatalogs'],'one original method')
    expected={('dev.codex.schubert.nk.api.file.EnumValueCatalogCompatibilityTest',methods[0])};actual=[]
    for filename,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(blob)==pin,'copied originalXML');xml=ET.fromstring(blob)
        require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'no nonpass')
        for case in xml.findall('testcase'):require(not list(case),'no hidden skip');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==1 and set(actual)==expected and not expected&{(v['classname'],v['name']) for v in old['cases']}
            and not {AES,MANAGER}&old['fullSourceUnits'].keys(),'new current scope, not old API package case')
    credentials=[('CONTEXT_CURRENT','api-context-aes-current',False),('CONTEXT_PREVIOUS','api-context-aes-previous',True),('RESPONSE_CURRENT','api-inbox-response-aes-current',False),('RESPONSE_PREVIOUS','api-inbox-response-aes-previous',True)]
    units=[('API','schubert-nk-api.service'),('WEB','schubert-nk-web.service'),('MORNING','schubert-nk-morning-controller.service'),('CLEANUP','schubert-nk-cleanup.service'),('EXPIRY','schubert-nk-expiry-cleanup.service'),('INSPECTOR','schubert-nk-inbox-inspector.service'),('BROKER','artemis.service'),('CADDY','caddy.service')]
    for rows in [credentials,units]:
        for column in [0,1]:
            positions=[text.index('"'+r[column]+'"') for r in rows];require(positions==sorted(positions) and len(set(positions))==len(rows),'independent literal order')
    require('List.of(false, true, false, true)' in text and 'ObjectStreamClass.lookup(type)' in text
            and 'assertEquals(0, descriptor.getFields().length' in text and 'assertEquals(0L, descriptor.getSerialVersionUID()' in text,'original schema/optional constants')
    require(not any(v in text for v in ['ObjectInputStream','ObjectOutputStream','Files.','NativeIo','new SystemManagerObservation','DriverManager','@Before']),'no stream input/native/manager operation')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    approved=(data.ROOT/design).read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    closures={AES:[AES],MANAGER:sorted([MANAGER,MANAGER+'$Budget',MANAGER+'$Factory',MANAGER+'$Owner',MANAGER+'$Property',MANAGER+'$Service',MANAGER+'$Session'])}
    meta={MANAGER+'$Budget',MANAGER+'$Factory',MANAGER+'$Session'};unexecuted={MANAGER,MANAGER+'$Owner',MANAGER+'$Property'}
    counts={'LINE':dict(covered=24,missed=63),'METHOD':dict(covered=7,missed=12),'CLASS':dict(covered=2,missed=3),'BRANCH':dict(covered=0,missed=42)}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW[1],'same actual source/run')
        require((v['tests'],v['suites'],v['newTestIds'],v['targetSourceUnits'])==(1,1,0,2) and v['cases']==raw['cases'],'one whole original')
        require(v['completeSourceUnitClosure']==closures and len(v['physicalClasses'])==8 and set(v['metadataClasses'])==meta
                and v['totals']==counts and v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'],'complete physical and actual exec')
        require(v['targetUnitFour100'] is v['allMeasuredApplicableCountersCovered'] is False and v['strictFour100GateExit']==1
                and v['manualCounterExclusions']==[],'whole incomplete, no suppression')
        require(type(v['fullSourceUnits']) is dict and set(v['fullSourceUnits'])=={AES,MANAGER},'exact two Source keyset before lookup')
        a,b=v['fullSourceUnits'][AES],v['fullSourceUnits'][MANAGER]
        require(a['branchNaturallyZero'] is a['threeCounter100'] is True and a['four100'] is False
                and a['totals']=={'LINE':dict(covered=11,missed=0),'METHOD':dict(covered=4,missed=0),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=0,missed=0)},'natural B0 only, never strict four100')
        require(b['four100'] is b['branchNaturallyZero'] is b['threeCounter100'] is False and all(c['covered']==0 for n in unexecuted for c in v['executable'][n]['counters'].values()),'unexecuted Code retained')
        require(v['publicEnumLabelsAndSerializationSchemaOnly'] is v['normalOrdinaryTestSourceDomain'] is True and v['ownThreadCount']==v['ownTaskCount']==0,'pure labels and schema only')
        require(all(v[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and v['effortPercent'] is None,'no authority/acceptance')
        for name in meta:
            inv=v['sourcePhysicalInventory'][name];require(inv['flags']==1536 and inv['methods'] and not any(x['hasCode'] for x in inv['methods']),'genuine abstract interfaces, not Code exclusions')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',12),('suites',2),('newTestIds',1),('targetSourceUnits',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('metadataClasses',[]),('totals',{}),('singleSession',False),('crcMismatch',1),('targetUnitFour100',True),('allMeasuredApplicableCountersCovered',True),('strictFour100GateExit',0),('manualCounterExclusions',['outer']),('fullSourceUnits',{}),('publicEnumLabelsAndSerializationSchemaOnly',False),('normalOrdinaryTestSourceDomain',False),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('actualFilesOpenedByProduct',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false enum qualification '+key)
    shapes=[]
    for bad_map in [{},{AES:p['fullSourceUnits'][AES],'OTHER':p['fullSourceUnits'][MANAGER]},{**p['fullSourceUnits'],'EXTRA':p['fullSourceUnits'][AES]}]:
        bad=copy.deepcopy(p);bad['fullSourceUnits']=bad_map
        try:contract(bad)
        except ValueError:shapes.append('rejected')
        else:raise ValueError('malformed Source map accepted')
    for v in (p,old):verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=1,semanticNegativeVectors=len(labels),negativeLabels=labels,
        independentOracleVectors=12,sourceMapStructureNegativeVectors=len(shapes),newSourcePrograms=2,metadataPhysicalClasses=3,newPhysicalClasses=8,wholeSourceIncompleteCount=1,naturalBranchZeroCompleteSources=1,
        productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
