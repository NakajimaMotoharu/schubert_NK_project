"""Independent original literals, POSIX boundary oracle and complete NoCode denominator checks."""
import copy
import json
import re
import stat
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16178-morning-backup-value-eight-post-v1','a8c75609656307b4b0a137bad96605a2e667bd0a997215ffc5bfb69e4691569f')
RAW=('PG16176-morning-backup-value-eight-pt-v1','dae38c90812c790779017a08736e3b264408d8a1855a2976687bbe8c629f5a67')
PREV=('PG16166-current2136-caddy-config-registry-v1','8f4646787f63d7060a25143c36c8250ffc650086d591ce413f5a477f7d8a3842')
NAME='dev/codex/schubert/nk/batch/file/MorningBackupArtifacts'
OUT=data.BASE/'PG16180-morning-backup-value-eight-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,previous=[read(v) for v in (POST,RAW,PREV)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (p,raw,previous)),'same-source original chain')
    selected={'MorningBackupMetadataTest':4,'MorningBackupCatalogTest':1,'MorningBackupInputModeTest':3}
    expected=set();texts={}
    for name,count in selected.items():
        path=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'/(name+'.java');text=path.read_text();texts[name]=text
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==count and len(set(methods))==count,'unchanged whole Test declarations')
        require(raw['begin']['testSourceHashes'][str(path)]==data.sha(text.encode()),'raw actual source pin')
        expected.update(('dev.codex.schubert.nk.batch.file.'+name,n) for n in methods)
        calls=set(re.findall(r'MorningBackupArtifacts\.(\w+)\s*\(',text))
        require(calls<={'requireDirectoryMetadata','requireFileMetadata','requireToolMetadata','requireNoAccessAcl','inputMode'}
                and not any(t in text for t in ['new MorningBackupArtifacts','Files.','ProcessBuilder','DriverManager','RootStartupContext','@Before','MessageDigest','KeyStore']),'only reviewed pure static guards')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original copiedXML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no nonpass')
        for row in xml.findall('testcase'):
            require(not list(row),'no ignored case');actual.append((row.get('classname'),row.get('name')))
    require(len(actual)==len(set(actual))==8 and set(actual)==expected
            and not expected&{(r['classname'],r['name']) for r in previous['cases']},'eight new whole originals')
    require(NAME not in previous['fullSourceUnits'],'new measured Source, not requalified old')
    require(all(t in texts['MorningBackupMetadataTest'] for t in ['040700','040750','0100640','0100644, 0100755','0, 1, 4096','268435456','268435457','assertArrayEquals(new byte[] {1, 2, 3}, acl)']),'independent boundary assertions retained')
    require(all(t in texts['MorningBackupInputModeTest'] for t in ['0100640','0100600','inbox-inspector.env','db-inbox-inspector','../api.env','null, credential'])
            and 'CONFIG.add("runtime.env")' in texts['MorningBackupCatalogTest'] and 'CREDENTIALS.clear()' in texts['MorningBackupCatalogTest'],'catalog separation/immutability retained')
    require(stat.S_IFMT(0o40700)==stat.S_IFDIR and stat.S_IMODE(0o40750)==0o750
            and stat.S_IFMT(0o100640)==stat.S_IFREG and stat.S_IMODE(0o100755)==0o755,'independent POSIX type/mode values')
    def oracle(kind,mode,uid,gid,links,size):
        if kind=='directory':return mode==0o40700 and uid==gid==0 and links>=2 and size>=0
        if kind=='file':return mode==0o100640 and uid==0 and gid==2001 and links==1 and 0<=size<=4096
        return mode in (0o100644,0o100755) and uid==gid==0 and links==1 and 1<=size<=268435456
    vectors=[('directory',0o40700,0,0,2,0),('directory',0o40755,0,0,2,0),('file',0o100640,0,2001,1,4096),
             ('file',0o100640,0,2001,1,4097),('tool',0o100755,0,0,1,268435456),('tool',0o100755,0,0,1,0)]
    require([oracle(*v) for v in vectors]==[True,False,True,False,True,False],'six independent fixed table vectors')
    designs={}
    for path in ['documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md','documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md']:
        body=(data.ROOT/path).read_bytes();require(body==subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT),'approved design same bytes');designs[path]=data.sha(body)
    meta={NAME+'$Work':('run','()Ljava/lang/Boolean;'),NAME+'$Writer':('write','(Ljava/nio/file/Path;)Ljava/lang/Boolean;')}
    for name,(method,descriptor) in meta.items():
        value=p['sourcePhysicalInventory'][name]
        require(value['flags']==1536 and value['sourceFile']=='MorningBackupArtifacts.java'
                and value['methods']==[dict(name=method,descriptor=descriptor,flags=1025,hasCode=False,codeLength=0)],'genuine abstract interface not excluded Code')
    counters={'LINE':dict(covered=34,missed=255),'METHOD':dict(covered=6,missed=45),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=50,missed=36)}
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['originalManifestSha256']==RAW[1],'same actual source')
        require((value['tests'],value['suites'],value['newTestIds'],value['targetSourceUnits'])==(8,3,0,1)
                and wire(value['cases'])==wire(raw['cases']),'whole eight original matrix')
        require(value['totals']==counters and value['fullSourceUnits'][NAME]['totals']==counters
                and value['completeSourceUnitClosure']=={NAME:sorted([NAME,*meta])}
                and set(value['metadataClasses'])==set(meta) and set(value['physicalClasses'])=={NAME,*meta},'complete oneSource/threephysical/twoNoCode')
        require(value['singleSession'] is True and value['crcMismatch']==0 and value['execSha256']==raw['execSha256']
                and value['sessionIdentity']=='PG16176-ORIGINAL-MORNING-BACKUP-VALUES-EIGHT','actual single exec')
        require(value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is False
                and value['strictFour100GateExit']==1 and value['manualCounterExclusions']==[],'unexecuted Backup remains missed')
        require(value['normalOrdinaryTestSourceDomain'] is value['onlySyntheticBackupMetadataAndPublicCatalogValues'] is True
                and value['actualBackupOrArchiveOperations']==0,'synthetic values only')
        require(all(value[k] is False for k in ['actualCredentialFileValuesRead','actualFilesOpenedByProduct','cryptoOrKeyOperationsInvoked',
                'actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','rootMainInvoked',
                'oldCoverageTransferred','formalUpdated','whole451Accepted']) and value['effortPercent'] is None,'no hidden access or acceptance')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('originalManifestSha256','0'*64),('tests',9),('suites',2),('cases',[]),('totals',{}),
        ('completeSourceUnitClosure',{}),('metadataClasses',[]),('physicalClasses',{}),('singleSession',False),('crcMismatch',1),
        ('targetUnitFour100',True),('allMeasuredApplicableCountersCovered',True),('strictFour100GateExit',0),('manualCounterExclusions',['X']),
        ('normalOrdinaryTestSourceDomain',False),('onlySyntheticBackupMetadataAndPublicCatalogValues',False),('actualBackupOrArchiveOperations',1),
        ('actualCredentialFileValuesRead',True),('actualFilesOpenedByProduct',True),('cryptoOrKeyOperationsInvoked',True),
        ('actualSecretKeysLoaded',True),('rootMainInvoked',True),('oldCoverageTransferred',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false Backup value qualification '+key)
    require(len(labels)==26,'finite26')
    require('invocation' not in raw and 'invocation' in raw['begin'],'explicit original invocation envelope')
    for v in (p,previous):verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=8,
        semanticNegativeVectors=26,negativeLabels=labels,independentOracleVectors=6,approvedDesignHashes=designs,
        newSourcePrograms=1,metadataPhysicalClasses=2,newPhysicalClasses=3,productTestsReexecuted=0,
        actualBackupOrArchiveOperations=0,actualCredentialValuesRead=False,newAccepted=0,formalUpdated=False,
        wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
