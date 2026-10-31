"""Independent literal inspection count/run oracle and complete Source denominator; no rerun."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16298-inspection-attempt-eight-post-v1','46c0ca95ecc46b9590392e3feec38b09f8940a7f6c93e9b19a23b283f634fc39')
RAW=('PG16296-inspection-attempt-eight-pt-v1','26cabfc47c9ef58e155d1c16687a6ed48977a5df4785e2699b83d29076d22a5c')
PREV=('PG16280-current2164-storage-registry-v1','57e0226d76bb40fa0db7b73c9dc041e82fcd7506d54d890569454648a2145118')
NAME='dev/codex/schubert/nk/batch/cleanup/InspectionAttempt'
OUT=data.BASE/'PG16300-inspection-attempt-eight-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,old)),'actual current source chain')
    path=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/InspectionAttemptTest.java'
    blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==raw['begin']['testSourceHashes'][str(path)]=='f80fec36648c7a4934626d1f7820dedfa731d2fc79962108265ea41cb7d16780','unchanged whole original Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
    expected={('dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest',v) for v in methods}
    require(len(methods)==len(expected)==8 and set(methods)=={'matchingSuccessAndWarning','zeroAndResumedAttemptCounts','completedBaselineImmutability','countRegressionAndOverflow','runIdentityAndMissingEnd','receiptCodesAndNulls','redactionAndValueOwnership','independentConcurrentObservations'},'all eight Test IDs')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original copied XML')
        xml=ET.fromstring(content);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no nonpass')
        for case in xml.findall('testcase'):
            require(not list(case),'no hidden skipped case');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==8 and set(actual)==expected
            and not expected&{(v['classname'],v['name']) for v in old['cases']} and NAME not in old['fullSourceUnits'],'current source first whole qualification')
    require(all(v in text for v in ['new CleanupCounts(4, 3, 1)','new CleanupCounts(9, 5, 4)','new CleanupCounts(1, 0, 1)',
        'List.of(-1, 1, 20, 30, 50, 70, Integer.MIN_VALUE, Integer.MAX_VALUE)','Long.MAX_VALUE',
        'InspectionAttempt[observation=<redacted>]','Executors.newVirtualThreadPerTaskExecutor()','i < 64','get(10, TimeUnit.SECONDS)',
        'new CleanupCounts(i + 4, i + 3, 1)','new CleanupCounts(i + 9, i + 5, 4)']),'literal original count/code/redaction/concurrency oracles')
    require(not any(v in text for v in ['java.nio.file','java.sql','ProcessBuilder','DriverManager','FingerprintKeyRing','ResponseSnapshotCodec','ChildStartupContext','@Before']),'pure value and self executor only')
    vectors=[((7,7,0),(0,0,0),(7,7,0),0),((7,3,4),(0,0,0),(7,3,4),10),((0,0,0),(0,0,0),(0,0,0),0),
             ((9,5,4),(5,2,3),(4,3,1),10),((5,2,3),(5,2,3),(0,0,0),10),
             ((2**63-1,2**63-2,1),(2**63-2,2**63-2,0),(1,0,1),10),
             ((2**63-1,0,2**63-1),(0,0,0),(2**63-1,0,2**63-1),10),
             ((2**63-1,2**63-1,0),(0,0,0),(2**63-1,2**63-1,0),0)]
    for cumulative,baseline,delta,receipt in vectors:
        require(cumulative[0]==cumulative[1]+cumulative[2] and delta==tuple(a-b for a,b in zip(cumulative,baseline))
                and all(0<=v<=2**63-1 for v in delta) and receipt==(0 if cumulative[2]==0 else 10),'eight independent integer vectors')
    for i in range(64):
        delta=tuple(a-b for a,b in zip((i+9,i+5,4),(5,2,3)))
        require(delta==(i+4,i+3,1) and delta[0]==delta[1]+delta[2],'64 independent differences')
    design='documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md'
    body=(data.ROOT/design).read_bytes();require(body==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    closure={NAME}
    require(set(p['sourcePhysicalInventory'])==closure and all(any(m['hasCode'] for m in v['methods']) for v in p['sourcePhysicalInventory'].values()),'whole one genuine Code class included')
    counts={'LINE':dict(covered=36,missed=0),'METHOD':dict(covered=5,missed=0),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=24,missed=0)}
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE
                and value['originalManifestSha256']==RAW[1],'same actual source/run')
        require((value['tests'],value['suites'],value['newTestIds'],value['targetSourceUnits'])==(8,1,0,1) and value['cases']==raw['cases'],'original eight only')
        require(value['totals']==counts and value['fullSourceUnits'][NAME]['totals']==counts
                and value['completeSourceUnitClosure']=={NAME:sorted(closure)} and value['metadataClasses']==[]
                and set(value['physicalClasses'])==closure,'complete one physical Code denominator')
        require(value['singleSession'] is True and value['crcMismatch']==0 and value['execSha256']==raw['execSha256']
                and value['sessionIdentity']=='PG16296-INSPECTION-ATTEMPT-EIGHT','actual one exec/CRC')
        require(value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is True
                and value['strictFour100GateExit']==0 and value['manualCounterExclusions']==[],'four counters only actual all covered')
        require(value['normalOrdinaryTestSourceDomain'] is value['pureCountRunReconciliation'] is True
                and value['ownThreadCount'] is None and value['ownTaskCount']==64 and value['ownVirtualThreadPerTaskExecutorDeclared'] is True,'original normal domain and finite fixture')
        require(all(value[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed',
                'actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted'])
                and value['effortPercent'] is None,'no authority/actual crypto or hidden acceptance')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('originalManifestSha256','0'*64),('tests',9),('suites',2),('newTestIds',8),('cases',[]),
        ('totals',{}),('completeSourceUnitClosure',{}),('metadataClasses',['X']),('physicalClasses',{}),('singleSession',False),('crcMismatch',1),
        ('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('strictFour100GateExit',1),('manualCounterExclusions',['X']),
        ('normalOrdinaryTestSourceDomain',False),('pureCountRunReconciliation',False),('ownThreadCount',64),('ownTaskCount',0),
        ('cryptoOrKeyOperationsInvoked',True),('actualSecretKeysLoaded',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),
        ('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false proof qualification '+key)
    require(len(labels)==26,'finite26')
    for v in (p,old):verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=8,
        semanticNegativeVectors=26,negativeLabels=labels,independentOracleVectors=8,independentConcurrentCountVectors=64,approvedDesignHashes={design:data.sha(body)},
        newSourcePrograms=1,metadataPhysicalClasses=0,newPhysicalClasses=1,productTestsReexecuted=0,newAccepted=0,
        formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
