"""Independent SS333 byte-slice and resource-ownership oracles for original whole streamer2."""
import copy
import hashlib
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16572_media_body_stream_original_two_pt as original
POST=('PG16574-media-body-stream-original-two-post-v1','4af1a3553a0e298c32650d8c3de8ddddca2f22d43cb3c3effc74185e3d688b57')
RAW=('PG16572-media-body-stream-original-two-pt-v1','5018198c35b345ba7ae6855284d204c7c17d817cb64c5e54bc199a22d94cd1b1')
PREV=('PG16562-current2267-management-encoder-registry-v1','4ed1fa5d5c1a4297d884710c05a76905bc279b12d2c1ff9f35022d3250a18bef')
OUT=data.BASE/'PG16576-media-body-stream-original-two-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'same genuine source')
    name='dev.codex.schubert.nk.web.media.MediaBodyStreamerTest';path=original.TESTS['MediaBodyStreamerTest'];blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==original.TEST_PINS['MediaBodyStreamerTest']==raw['begin']['testSourceHashes'][str(path)],'original whole Test bytes')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);expected={(name,m) for m in methods};require(len(methods)==2,'all two declarations')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    require(expected=={(v['className'],v['method']) for v in bindings if v['className']==name} and not expected&{(v['classname'],v['name']) for v in old['cases']},'two new ordinary identities')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original XML hash');root=ET.fromstring(content)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'genuine PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==2 and set(actual)==expected,'whole original two')
    vectors=[
      ['(byte) (index * 17 + 3)','new int[] {0, 1, 65_536, 65_537, 1_048_576}','Arrays.copyOfRange(data, 3, 3 + length)'],
      ['target.maxWrite <= 65_536','assertEquals(length, target.bytes.size())','assertEquals(3 + length, source.position())'],
      ['assertTrue(source.isOpen())','assertFalse(target.closed)','assertFalse(target.flushed)'],
      ['shortSource.maxRead = 3','shortSource, target, 5, 12','Arrays.copyOfRange(shortSource.data, 5, 17)','new Output(), 100, 0'],
      ['NullPointerException.class','new long[][] {{-1, 1}, {0, -1}, {Long.MAX_VALUE, 1}}'],
      ['List.of("size", "position", "read", "zero", "eof", "write", "outside")','IOException.class','"media transfer did not complete"','assertNull(failure.getCause())','failure.getSuppressed().length'],
      ['source.failAfter = 1','new byte[] {0, 1, 2}','assertTrue(source.isOpen())'],
      ['@TempDir Path root','Files.write(file, data)','FileChannel.open(file, StandardOpenOption.READ)','try (var source =','throw new AssertionError("source write")','throw new AssertionError("source truncate")']]
    require(all(all(v in text for v in group) for group in vectors),'independent bound/slice/progress/redaction/ownership oracles')
    require(not any(v in text for v in ['LinuxDirectoryCalls','OwnedTransferDirectory','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','HttpClient','Socket','RootFailedStartRecovery']),'no retained/native/Graph/backend operations')
    unit=next(iter(original.MAIN_UNITS));counts={k:dict(missed=0,covered=c) for k,c in [('LINE',19),('METHOD',1),('CLASS',1),('BRANCH',12)]}
    expected_fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=2,suites=1,newTestIds=0,cases=raw['cases'],completeSourceUnitClosure=original.CLOSURES,metadataClasses=[],unexecutedCodeClasses=[],totals=counts,strictFour100GateExit=0,targetUnitFour100=True,allMeasuredApplicableCountersCovered=True,manualCounterExclusions=[],singleSession=True,crcMismatch=0,actualFilesOpenedByProduct=False,testOwnTemporaryContentWritten=True,testOwnedFileChannelsOpened=True,callerResourcesClosedByProduct=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualAuthenticationOrSessionIssued=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualVmActions=0,actualServiceActions=0,actualNetworkActions=0,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    def contract(value):
        require(all(type(value[k]) is type(v) and value[k]==v for k,v in expected_fields.items()),'independent typed run/counter/effect contract')
        require(set(value['physicalClasses'])==set(value['executable'])=={unit} and value['fullSourceUnits'][unit]['totals']==counts,'all physical Source counters')
        require(len(value['rootRecoveryProbeAudit'])==27 and all(not v['recordPresent'] and v['trueProbeHits']==0 for v in value['rootRecoveryProbeAudit'].values()),'Root no execution records')
        require(value['forbiddenProductProbeHits']==0 and len(value['passiveNativeBoundaryAbsence']['rows'])==6 and all(v[3]=='0' for v in value['passiveNativeBoundaryAbsence']['rows']),'held/native absence')
    contract(p);labels=[]
    for key,value in expected_fields.items():
        bad=copy.deepcopy(p)
        if type(value) is bool:bad[key]=not value
        elif type(value) is int:bad[key]=value+1
        elif isinstance(value,str):bad[key]='BAD'
        elif value is None:bad[key]=100
        elif isinstance(value,list):bad[key]=['BAD']
        else:bad[key]={}
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false metadata accepted '+key)
    for key in ['physicalClasses','rootRecoveryProbeAudit','passiveNativeBoundaryAbsence']:
        bad=copy.deepcopy(p);bad[key]={}
        try:contract(bad)
        except (ValueError,KeyError):labels.append(key)
        else:raise ValueError('incomplete physical or absence accepted')
    ss='documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md';body=(data.ROOT/ss).read_bytes()
    require(data.sha(body)=='d861735e91a6930bbf239937deda29f3675fbf50817953a61e07c0255387fa66' and body==subprocess.check_output(['git','show','origin/main:'+ss],cwd=data.ROOT),'approved SS333 exact bytes')
    golden=[dict(start=3,length=n,sha256=hashlib.sha256(bytes(((i*17+3)&255) for i in range(3,3+n))).hexdigest()) for n in [0,1,65536,65537,1048576]]
    require(bytes(((i*17+3)&255) for i in range(3,6))==bytes([54,71,88]),'independent literal prefix')
    for row in [p,old]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=2,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(vectors),independentlyCalculatedSliceHashes=golden,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,approvedDesignHashes={ss:data.sha(body)},productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(vectors))
if __name__=='__main__':main()
