"""Independent public proof field/numeric oracle, XML and complete Source denominator; no rerun."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16234-public-proof-eight-post-v1','6bd10e6f210bea7ce5ccada4b03f5763894b6a4db630cb076ccb72fc18f26474')
RAW=('PG16232-public-proof-eight-pt-v1','c4b8b8c86eaf6180929e6bcf05f79aa8fe623a6df65d371ee1f505cf98e2ca86')
PREV=('PG16222-current2149-public-launch-registry-v1','11e0c12b6368a686b092ad955272ce70ca9883bed67a29101e3b44be182ddc6e')
NAME='dev/codex/schubert/nk/bootstrap/StartupProofFrame'
OUT=data.BASE/'PG16236-public-proof-eight-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,old)),'actual current source chain')
    path=data.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/StartupProofFrameTest.java'
    blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==raw['begin']['testSourceHashes'][str(path)]=='658c1736b4d4d0927d4db12eac869c5bf66dd8a29c862993d26780d52341fa59','unchanged whole original Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
    expected={('dev.codex.schubert.nk.bootstrap.StartupProofFrameTest',v) for v in methods}
    require(len(methods)==len(expected)==8 and all(any(v.startswith('proof00'+str(i)) for v in methods) for i in range(1,9)),'all eight Test IDs')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original copied XML')
        xml=ET.fromstring(content);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no nonpass')
        for case in xml.findall('testcase'):
            require(not list(case),'no hidden skipped case');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==8 and set(actual)==expected
            and not expected&{(v['classname'],v['name']) for v in old['cases']} and NAME not in old['fullSourceUnits'],'current source first whole qualification')
    literal=re.search(r'private static final String GOLDEN =\s*"""\n(.*?)\s*""";',text,re.S)
    require(literal is not None,'literal independent golden')
    golden='\n'.join(v[6:] for v in literal[1].splitlines())+'\n'
    rows=golden.split('\n');keys=['service','boot_id','invocation_id','pid','start_ticks','admission_fd','admission_device','admission_inode','service_uid','service_gid','service_groups','permit_epoch','permit_sha256','release_sha256','config_sha256','roots_sha256','broker_invocation_id']
    require(rows[0]=='NKSTART1' and rows[-1]=='' and len(rows)==19
            and [v.split('=',1)[0] for v in rows[1:-1]]==keys,'independent exact 17-field order/EOF')
    require(all(v in text for v in ['List.of(0, 9, 13, 31, 127, 128, 255)','List.of(0, 8192, 8193)',
        '"18446744073709551615"','"4294967294"','"18446744073709551616"','"1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17"',
        'Executors.newFixedThreadPool(8)','i < 32','executor.invokeAll(work)','assertArrayEquals(bytes(GOLDEN), result.get())']), 'independent boundaries and pool32 retained')
    require(not any(v in text for v in ['java.nio.file','ProcessBuilder','DriverManager','FingerprintKeyRing','ResponseSnapshotCodec','ChildStartupContext','LinuxMonotonicClock','@Before']),'pure JDK value and self-owned pool closure')
    def decimal(value,low,high):
        return re.fullmatch(r'[1-9][0-9]*',value) is not None and low<=int(value)<=high
    vectors=[('2',2,2147483647),('1',2,2147483647),('128',128,65535),('127',128,65535),
        ('65535',128,65535),('65536',128,65535),('18446744073709551615',1,2**64-1),('18446744073709551616',1,2**64-1)]
    require([decimal(*v) for v in vectors]==[True,False,True,False,True,False,True,False],'eight independent mathematical vectors')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    body=(data.ROOT/design).read_bytes();require(body==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    closure={NAME,NAME+'$Bounds',NAME+'$Field'}
    require(set(p['sourcePhysicalInventory'])==closure and all(any(m['hasCode'] for m in v['methods']) for v in p['sourcePhysicalInventory'].values()),'all three genuine Code classes included')
    counts={'LINE':dict(covered=71,missed=0),'METHOD':dict(covered=13,missed=0),'CLASS':dict(covered=3,missed=0),'BRANCH':dict(covered=38,missed=0)}
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE
                and value['originalManifestSha256']==RAW[1],'same actual source/run')
        require((value['tests'],value['suites'],value['newTestIds'],value['targetSourceUnits'])==(8,1,0,1) and value['cases']==raw['cases'],'original eight only')
        require(value['totals']==counts and value['fullSourceUnits'][NAME]['totals']==counts
                and value['completeSourceUnitClosure']=={NAME:sorted(closure)} and value['metadataClasses']==[]
                and set(value['physicalClasses'])==closure,'complete three physical Code denominator')
        require(value['singleSession'] is True and value['crcMismatch']==0 and value['execSha256']==raw['execSha256']
                and value['sessionIdentity']=='PG16232-PUBLIC-PROOF-EIGHT','actual one exec/CRC')
        require(value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is True
                and value['strictFour100GateExit']==0 and value['manualCounterExclusions']==[],'four counters only actual all covered')
        require(value['normalOrdinaryTestSourceDomain'] is value['onlyPublicProofTextAndNumericValues'] is True
                and (value['ownThreadCount'],value['ownTaskCount'])==(8,32),'original normal domain and finite fixture')
        require(all(value[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed',
                'actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted'])
                and value['effortPercent'] is None,'no authority/actual crypto or hidden acceptance')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('originalManifestSha256','0'*64),('tests',9),('suites',2),('newTestIds',8),('cases',[]),
        ('totals',{}),('completeSourceUnitClosure',{}),('metadataClasses',['X']),('physicalClasses',{}),('singleSession',False),('crcMismatch',1),
        ('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('strictFour100GateExit',1),('manualCounterExclusions',['X']),
        ('normalOrdinaryTestSourceDomain',False),('onlyPublicProofTextAndNumericValues',False),('ownThreadCount',0),('ownTaskCount',0),
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
        semanticNegativeVectors=26,negativeLabels=labels,independentOracleVectors=8,approvedDesignHashes={design:data.sha(body)},
        newSourcePrograms=1,metadataPhysicalClasses=0,newPhysicalClasses=3,productTestsReexecuted=0,newAccepted=0,
        formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
