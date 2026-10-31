"""Independent synthetic wrapper/null/redaction oracle, retaining all unexecuted outer Code."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16330-current-observation-one-post-v1','b852ea2d21812f14ce578dd4bad4936d23f33e2c8d1c1e8312bb6f07a5f1dc80')
RAW=('PG16328-current-observation-one-pt-v1','62fb2d17490afc9d6ac90860f1577a2e8285175c46ad34eccbdb49b9319f241c')
PREV=('PG16318-current2173-bootstrap-enum-registry-v1','7c618826ff3db2244157c3b1df5fe0c7af7790db3e7d6c45176fbf0b7549e6be')
NAME='dev/codex/schubert/nk/batch/file/RootCurrentPermitPreflight'
OUT=data.BASE/'PG16332-current-observation-one-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,old)),'genuine current chain')
    path=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CurrentObservationValueTest.java';body=path.read_bytes();text=body.decode()
    require(data.sha(body)==raw['begin']['testSourceHashes'][str(path)]=='527f57cd6b2068338c965c939e9a04bdace62ac71c6fe4a481a9ffd56a82a1d4','whole fixed original')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(methods==['data511001WrapperRetainsValuesButNeverPrintsPublicBindings'],'one original method')
    expected={('dev.codex.schubert.nk.batch.file.CurrentObservationValueTest',methods[0])};actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'copied original XML');xml=ET.fromstring(blob)
        require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'no nonpass')
        for case in xml.findall('testcase'):require(not list(case),'no hidden skip');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==1 and set(actual)==expected and not expected&{(v['classname'],v['name']) for v in old['cases']} and NAME not in old['fullSourceUnits'],'first current original case')
    require(all(v in text for v in ['new String[] {"1", "2"}','assertSame(current, value.current())','assertSame(permit, value.permit())',
        '"RootIssued[identity=<redacted>]"','new RootCurrentPermitPreflight.Observed(null, permit)','new RootCurrentPermitPreflight.Observed(current, null)',
        'Instant.parse("2026-09-29T00:00:00Z")','Optional.of("a".repeat(64))']),'literal two inputs/null/identity/redaction oracle')
    require(re.search(r'RootCurrentPermitPreflight\.(?!Observed\b)',text) is None and re.search(r'StartupPermitRecords\.(?!(?:Epoch|Permit|State)\b)',text) is None,'no Root/permit operations in whole original')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';approved=(data.ROOT/design).read_bytes()
    require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    closure=[NAME,NAME+'$Observed'];counts={'LINE':dict(covered=5,missed=32),'METHOD':dict(covered=2,missed=5),'CLASS':dict(covered=1,missed=1),'BRANCH':dict(covered=0,missed=16)}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW[1],'actual source/run')
        require((v['tests'],v['suites'],v['newTestIds'],v['targetSourceUnits'])==(1,1,0,1) and v['cases']==raw['cases'],'one whole original')
        require(v['completeSourceUnitClosure']=={NAME:closure} and set(v['physicalClasses'])==set(closure) and v['metadataClasses']==[]
                and type(v['fullSourceUnits']) is dict and set(v['fullSourceUnits'])=={NAME} and set(v['executable'])==set(closure),'exact Code/source keysets before lookup')
        require(v['totals']==v['fullSourceUnits'][NAME]['totals']==counts and all(c['covered']==0 for c in v['executable'][NAME]['counters'].values()),'all outer Code unexecuted retained')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']=='PG16328-CURRENT-OBSERVATION-ONE','one actual exec')
        require(v['targetUnitFour100'] is v['allMeasuredApplicableCountersCovered'] is False and v['strictFour100GateExit']==1 and v['manualCounterExclusions']==[],'honest incomplete whole Source')
        require(v['syntheticPublicBindingValuesOnly'] is v['syntheticPermitValueOnly'] is v['normalOrdinaryTestSourceDomain'] is True and v['actualPermitIssueSignPublishOrRetire'] is False,'synthetic values not authority')
        require(all(v[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and v['effortPercent'] is None,'no authority/acceptance transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',2),('suites',2),('newTestIds',1),('targetSourceUnits',2),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('metadataClasses',['outer']),('fullSourceUnits',{}),('executable',{}),('totals',{}),('singleSession',False),('crcMismatch',1),('targetUnitFour100',True),('allMeasuredApplicableCountersCovered',True),('strictFour100GateExit',0),('manualCounterExclusions',['outer']),('syntheticPublicBindingValuesOnly',False),('syntheticPermitValueOnly',False),('normalOrdinaryTestSourceDomain',False),('actualPermitIssueSignPublishOrRetire',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false wrapper qualification '+key)
    for v in (p,old):verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=1,semanticNegativeVectors=len(labels),negativeLabels=labels,
        independentOracleVectors=2,newSourcePrograms=1,metadataPhysicalClasses=0,newPhysicalClasses=2,wholeSourceIncompleteCount=1,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
