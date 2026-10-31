"""Independent literals, XML, complete closure and parent-probe audit qualification, no Product JVM."""
import copy
import hashlib
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16218-public-launch-five-post-v1','e61aea9c4b13c891c619e0686c3ed0ca37eebfd8e41be3c31310b0b57b37ca51')
RAW=('PG16219-public-launch-five-pt-v1','65287a1afc4a8fab08f73a260e50f87b9ad600d34aab6a8aa10fc8c4301fe749')
PREV=('PG16182-current2144-backup-values-registry-v1','11c34b85628be56cb0365f3889a747953e5540746b3484014650752de9f0597e')
NAME='dev/codex/schubert/nk/batch/file/StartupLaunchRecord'
OUT=data.BASE/'PG16220-public-launch-five-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,old)),'same actual source')
    root=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'
    tests={'StartupLaunchRecordTest':(root/'StartupLaunchRecordTest.java',4),
           'PublicLaunchFramingBoundaryTest':(data.ROOT/'tools/quality/architecture/PublicLaunchFramingBoundaryTest.java',1)}
    expected=set();texts={}
    for name,(path,count) in tests.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(raw['begin']['testSourceHashes'][str(path)]==data.sha(blob),'actual unchanged Test input')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text)
        require(len(methods)==len(set(methods))==count,'whole fixed test selection')
        expected.update(('dev.codex.schubert.nk.batch.file.'+name,n) for n in methods)
        require(not set(re.findall(r'(?<![\w$])(Files|ProcessBuilder|DriverManager|HttpClient)\s*[.(]',text)), 'no actual file/network/command entry')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original copied XML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no nonpass')
        for case in xml.findall('testcase'):
            require(not list(case),'no skipped or failed child');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==5 and set(actual)==expected
            and not expected&{(v['classname'],v['name']) for v in old['cases']},'new current-source four+one, not historical addition')
    require(NAME not in old['fullSourceUnits'],'new measured Source')
    original=texts['StartupLaunchRecordTest'];boundary=texts['PublicLaunchFramingBoundaryTest']
    golden=('NKLAUNCH1\nservice=API\nboot=31100027-3333-4333-8444-555555555555\n'
        'epoch=31100027-4444-4333-8444-555555555555\npermit_sha256='+'a'*64+'\nowner_sha256='+'b'*64+
        '\ninvocation='+'2'*32+'\npid=300\nstart_ticks=200\n')
    literal=re.search(r'private static final String FRAME =\s*"""\n(.*?)\s*""";',boundary,re.S)
    require(literal is not None,'independent hand-written frame')
    frame='\n'.join(line[6:] for line in literal[1].splitlines())+'\n'
    require(frame==golden and len(golden.split('\n'))==10 and golden.endswith('\n'),'eight fixed fields/order/EOF')
    require(all(v in boundary for v in ['del[0] = 0x7f;', '(FRAME + "x")', 'assertThrows(IOException.class, () -> StartupLaunchRecord.consume(del))',
            'assertThrows(IOException.class, () -> StartupLaunchRecord.consume(trailing))']) and 'encode(' not in boundary,'independent malformed expectations')
    require(all(v in original for v in ['wholeIndependentFrameBothServicesAndFields','malformedAndNonCanonicalAllFields','nullAndConstructorInvariants',
            'independentShaVectorAlgorithmFailureAndUnknownIdentity','new NoSuchAlgorithmException("private")','assertSame('])
            and hashlib.sha256(b'abc').hexdigest()=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','independent SHA256 vector/unknown identity')
    # Declarative SS ASCII/EOF oracle. Does not invoke Production consume or encode.
    def framing(blob):
        return bool(blob) and len(blob)<=1024 and all(v==10 or 32<=v<=126 for v in blob) and blob.split(b'\n')[-1]==b'' and len(blob.split(b'\n'))==10
    encoded=golden.encode('ascii')
    vectors=[encoded,b'\x7f'+encoded[1:],encoded+b'x',encoded+b'\n',b'',b'\xff']
    require([framing(v) for v in vectors]==[True,False,False,False,False,False],'six independent table vectors')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    body=(data.ROOT/design).read_bytes()
    require(body==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT)
            and 'launch byteはASCII/LF' in body.decode() and 'key=value' in body.decode(),'approved SS unchanged')
    meta=NAME+'$DigestFactory';inventory=p['sourcePhysicalInventory'][meta]
    require(inventory['flags']==1536 and inventory['sourceFile']=='StartupLaunchRecord.java'
            and inventory['methods']==[dict(name='create',descriptor='()Ljava/security/MessageDigest;',flags=1025,hasCode=False,codeLength=0)],'genuine one NoCode interface')
    counts={'LINE':dict(covered=53,missed=0),'METHOD':dict(covered=9,missed=0),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=34,missed=0)}
    receipt=p['passivePublicLaunchParentRestriction']
    require(receipt['metadataNegativeChecks']==2 and receipt['execUnchanged'] is True
            and receipt['productClassesLoaded'] is receipt['productMethodsInvoked'] is False
            and receipt['results']=={'ORIGINAL':dict(actualExit=0,diagnostic='PUBLIC_LAUNCH_RECORDED_SCOPE_OK'),
                'FORGED_CLASS':dict(actualExit=1,diagnostic='UNREVIEWED_TRUE_PROBE'),
                'FORGED_PARENT':dict(actualExit=1,diagnostic='NONVALUE_PARENT_RECORDED_INSTRUCTION')},'actual and synthetic metadata modes separated')
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE
                and value['originalManifestSha256']==RAW[1],'actual source/run')
        require((value['tests'],value['suites'],value['ordinaryTests'],value['qualityFixtureTests'],value['newTestIds'])==(5,2,4,1,1)
                and value['cases']==raw['cases'],'four original/one new fixture domain')
        require(value['totals']==counts and value['fullSourceUnits'][NAME]['totals']==counts
                and value['completeSourceUnitClosure']=={NAME:sorted([NAME,meta])}
                and value['metadataClasses']==[meta] and set(value['physicalClasses'])=={NAME,meta},'whole Source, no metadata exclusion')
        require(value['singleSession'] is True and value['crcMismatch']==0 and value['sessionIdentity']=='PG16219-PUBLIC-LAUNCH-FIVE'
                and value['execSha256']==raw['execSha256'],'single actual exec/CRC')
        require(value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is True
                and value['strictFour100GateExit']==0 and value['manualCounterExclusions']==[],'all required counters measured')
        require(value['normalOrdinaryTestSourceDomain'] is False and value['mixedNormalAndQualityFixtureDomain'] is True
                and value['cryptoOrKeyOperationsInvoked'] is value['onlyPublicCorrelationCodecAndNonSecretSha256'] is True,'SHA is real, domain disclosed')
        require(value['passivePublicLaunchParentRestriction']==receipt,'parent restriction evidence kept')
        require(all(value[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued',
                'actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted'])
                and value['effortPercent'] is None,'no actual authority/hidden operations/formal promotion')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('originalManifestSha256','0'*64),('tests',6),('suites',1),('ordinaryTests',5),('qualityFixtureTests',0),
        ('newTestIds',5),('cases',[]),('totals',{}),('completeSourceUnitClosure',{}),('metadataClasses',[]),('physicalClasses',{}),
        ('singleSession',False),('crcMismatch',1),('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),
        ('strictFour100GateExit',1),('manualCounterExclusions',['X']),('normalOrdinaryTestSourceDomain',True),
        ('mixedNormalAndQualityFixtureDomain',False),('cryptoOrKeyOperationsInvoked',False),('actualSecretKeysLoaded',True),
        ('actualFilesOpenedByProduct',True),('passivePublicLaunchParentRestriction',{}),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false public launch qualification '+key)
    require(len(labels)==26,'finite26')
    for value in (p,old):verify(value['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=5,
        ordinaryTests=4,qualityFixtureTests=1,semanticNegativeVectors=26,negativeLabels=labels,independentOracleVectors=6,
        approvedDesignHashes={design:data.sha(body)},newSourcePrograms=1,metadataPhysicalClasses=1,newPhysicalClasses=2,
        productTestsReexecuted=0,passiveMetadataNegativeChecks=2,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,
        whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
