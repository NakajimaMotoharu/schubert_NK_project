"""Independent original seven XML, explicit mode/size oracle and owned temporary lifecycle."""
import copy
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16276-storage-attribute-seven-post-v1','bb990997b2629a6e93ab31938c04d6b18cc267feac2c0bf57b7d433497c9f0f9')
RAW=('PG16277-storage-attribute-seven-pt-v2','030a60ffd749aec6b5c48fda69d8c77b840633930d78a6c3d817191e4c4c614a')
PREV=('PG16238-current2157-public-proof-registry-v1','deb61775f9c16b20528879ed54854353ea1edb23cdff5cc99cc00a022b8ac031')
NAME='dev/codex/schubert/nk/storage/StorageAttributeGuard'
OUT=data.BASE/'PG16278-storage-attribute-seven-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,old)),'actual source chain')
    path=data.ROOT/'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/StorageAttributeGuardTest.java'
    blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==raw['begin']['testSourceHashes'][str(path)]=='1c0dd9629f7225661dd682f967ec0ae35fd1c93928144ed9349849d6ea1676c3','whole original Test unchanged')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
    expected={('dev.codex.schubert.nk.storage.StorageAttributeGuardTest',v) for v in methods};actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original copied XML')
        xml=ET.fromstring(content);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no nonpass')
        for case in xml.findall('testcase'):
            require(not list(case),'no hidden skipped');actual.append((case.get('classname'),case.get('name')))
    require(len(methods)==len(actual)==len(set(actual))==7 and set(actual)==expected
            and not expected&{(v['classname'],v['name']) for v in old['cases']} and NAME not in old['fullSourceUnits'],'first current seven, not old-source transfer')
    require(all(v in text for v in ['0b100_000_111_101_000','0b001_000_000_110_100_000','new byte[] {1, 2, 3}',
        'new long[] {0, 1, 4799, 4800, 48_000_000}','new long[] {4800, 9600, 48_000_000}',
        'new long[] {0, 1, 4799, 4801, 47_999_999}','Long.MAX_VALUE','a".repeat(32)','a".repeat(33)',
        'StandardOpenOption.CREATE_NEW','LinkOption.NOFOLLOW_LINKS','Files.createSymbolicLink(root.resolve(',
        'Files.createLink(root.resolve(','assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(hard))',
        'PosixFilePermissions.fromString("rw-r--r--"), Files.getPosixFilePermissions(other)']), 'explicit original independent assertions retained')
    require(int('100000111101000',2)==0o040750 and int('001000000110100000',2)==0o100640,'independent binary/Unix modes')
    require(48_000_000//4800==10000 and 48_000_000%4800==0 and 47_999_999%4800==4799,'independent record arithmetic')
    vectors=[0,1,4799,4800,9600,48_000_000,4801,47_999_999]
    require([0<n<=48_000_000 and n%4800==0 for n in vectors]==[False,False,False,True,True,True,False,False],'eight independent size vectors')
    require(not any(v in text for v in ['ProcessBuilder','java.sql','DriverManager','FingerprintKeyRing','ResponseSnapshotCodec','ChildStartupContext','@Before']),'no held boundary dependency')
    require(text.count('Linux')==1 and '// Integer is not the Linux long size contract.' in text,'single comment is not native call')
    for design in ['documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md','documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md']:
        require((data.ROOT/design).read_bytes()==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    core=data.ROOT.parent/'toolchain/m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    require(data.sha(core.read_bytes())=='ade1e0fdb4cd80d8537b57c6edb70a1360c47fdc518c20c65314517479bc4d0d','official fixed filter library')
    with zipfile.ZipFile(core) as jar:
        filter_name='org/jacoco/core/internal/analysis/filter/PrivateEmptyNoArgConstructorFilter.class'
        filter_pin=data.sha(jar.read(filter_name))
    counts={'LINE':dict(covered=44,missed=0),'METHOD':dict(covered=8,missed=0),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=42,missed=0)}
    lifecycle=raw['stages'][1]['ownedTemporaryParentLifecycle']
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['originalManifestSha256']==RAW[1],'same actual run')
        require((value['tests'],value['suites'],value['newTestIds'],value['targetSourceUnits'])==(7,1,0,1) and value['cases']==raw['cases'],'original seven only')
        require(value['totals']==counts and value['fullSourceUnits'][NAME]['totals']==counts and value['completeSourceUnitClosure']=={NAME:[NAME]}
                and value['metadataClasses']==[] and set(value['physicalClasses'])=={NAME},'whole Source denominator')
        require(value['singleSession'] is True and value['crcMismatch']==0 and value['execSha256']==raw['execSha256'] and value['sessionIdentity']=='PG16277-STORAGE-ATTRIBUTE-SEVEN','one exec CRC')
        require(value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is True and value['strictFour100GateExit']==0 and value['manualCounterExclusions']==[],'all four required counters')
        require(value['normalOrdinaryTestSourceDomain'] is value['onlySyntheticAttributeAndOwnedFileFixture'] is True
                and value['actualFilesOpenedByTestAndTempDirSpi'] is value['actualSyntheticFileAndLinkOperations'] is value['actualChildPermissionChanges'] is True,'real own test file effects disclosed')
        require(value['ownedTemporaryParentLifecycle']==lifecycle and lifecycle['before']==lifecycle['after'] and lifecycle['sevenUniqueChildrenRemoved'] is True,'actual owned lifecycle')
        require(value['privateEmptyConstructorDefaultFilter']==dict(physicalMethods=9,measuredMethods=8,privateEmptyConstructorCount=1,filter='JaCoCo0.8.15 PrivateEmptyNoArgConstructorFilter',manualExclusionAdded=False),'default filter, not nine actual executed methods')
        require(all(value[k] is False for k in ['cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and value['effortPercent'] is None,'no authority or global credit')
    contract(p);labels=[]
    vectors=[('source','OLD'),('originalManifestSha256','0'*64),('tests',8),('suites',2),('newTestIds',7),('cases',[]),('totals',{}),('completeSourceUnitClosure',{}),('metadataClasses',['X']),('physicalClasses',{}),('singleSession',False),('crcMismatch',1),('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('strictFour100GateExit',1),('manualCounterExclusions',['X']),('normalOrdinaryTestSourceDomain',False),('onlySyntheticAttributeAndOwnedFileFixture',False),('actualFilesOpenedByTestAndTempDirSpi',False),('ownedTemporaryParentLifecycle',{}),('privateEmptyConstructorDefaultFilter',{}),('actualSyntheticFileAndLinkOperations',False),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('formalUpdated',True),('effortPercent',100)]
    for key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false storage qualification '+key)
    require(len(labels)==26,'finite26')
    for v in (p,old):verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=7,
        semanticNegativeVectors=26,negativeLabels=labels,independentOracleVectors=8,newSourcePrograms=1,metadataPhysicalClasses=0,newPhysicalClasses=1,
        officialPrivateEmptyConstructorFilterSha256=filter_pin,ownedTemporaryLifecycleConfirmed=True,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
