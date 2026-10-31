"""Independent RFC public tuple identities and complete signature primitive Source counters."""
import copy
import hashlib
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16524_release_public_signature_original_eight_pt as original
POST=('PG16526-release-public-signature-original-eight-post-v1','adcbf15d515e0b0d46e6844d4400f2c1931bf206e831968264db6bb3f05f8844')
RAW=('PG16524-release-public-signature-original-eight-pt-v1','3cf39551215d747b93f4f81d1b709394b0002ae235548a643b50ce7987946be7')
PREV=('PG16514-current2252-release-inventory-registry-v1','14e8a27f44cfaed103801f6a098b2b78e2ce7937800bceb9fc619f3c06b50ce6')
OUT=data.BASE/'PG16528-release-public-signature-original-eight-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'same actual source')
    name='dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest';path=original.TESTS['ReleaseSignatureVerifierTest'];blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==original.TEST_PINS['ReleaseSignatureVerifierTest']==raw['begin']['testSourceHashes'][str(path)],'unchanged whole Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==8,'all sixteen declarations');expected={(name,m) for m in methods}
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    require(expected=={(v['className'],v['method']) for v in bindings if v['className']==name} and not expected&{(v['classname'],v['name']) for v in old['cases']},'whole new current methods')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original XML pin');root=ET.fromstring(content)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==8 and set(actual)==expected,'whole original sixteen actual cases')
    vectors=[
      ['first().verify(new byte[0], hex(SIGN1))','verify(hex("72"), hex(SIGN2))','corrupted[0] ^= 1'],
      ['List.of(0, 43, 45)','for (int i = 0; i < 12; i++)','new ReleaseSignatureVerifier(null)'],
      ['List.of(0, 63, 65)','new byte[1_048_577]','new byte[1_048_576]'],
      ['Arrays.fill(inputKey, (byte) 0)','assertArrayEquals(new byte[owned.length], owned)','assertArrayEquals(hex("72"), message)'],
      ['new GeneralSecurityException("PRIVATE")','"release signature unavailable"','assertNull(actual.getCause())','actual.getSuppressed().length'],
      ['new IllegalStateException("PRIVATE")','new AssertionError("PRIVATE")','assertSame('],
      ['new CyclicBarrier(4)','Executors.newFixedThreadPool(4)','barrier.await(5, TimeUnit.SECONDS)','future.get(5, TimeUnit.SECONDS)','"ff".repeat(32)','"ff".repeat(64)']]
    require(all(all(v in text for v in group) for group in vectors),'independent bounds/null/redaction/identity/erasure/four-task oracles')
    public={}
    for key in ['PREFIX','PUBLIC1','PUBLIC2','SIGN1','SIGN2']:
        match=re.search(r'private static final String '+key+r'\s*=\s*"([0-9a-f]+)";',text)
        require(match is not None,'closed public fixture constant');public[key]=bytes.fromhex(match.group(1))
    require(public['PREFIX']==bytes.fromhex('302a300506032b6570032100') and all(len(public[k])==32 for k in ['PUBLIC1','PUBLIC2']) and all(len(public[k])==64 for k in ['SIGN1','SIGN2']),'public DER prefix/widths')
    expected_hashes=['0e1d4c11a5a51315bf2daccae025f9654fd7309bf941e57dece4caeea65c280c','6097870ca6d0211b3dd4e7a4ce26bc35d0c3b21f295f8f503426a521610a5ba8']
    tuples=[public['PUBLIC1']+b''+public['SIGN1'],public['PUBLIC2']+bytes.fromhex('72')+public['SIGN2']]
    require([hashlib.sha256(v).hexdigest() for v in tuples]==expected_hashes,'RFC8032 7.1 TEST1/2 public tuple hashes manually checked at official publication, no Production calculation')
    require(not any(v in text for v in ['KeyPairGenerator','PrivateKey','generatePrivate','initSign','Files.','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException']),'no private/runtime keys/signing/external/Graph calls')
    counts={k:dict(missed=0,covered=c) for k,c in [('LINE',32),('METHOD',8),('CLASS',2),('BRANCH',10)]}
    physical=set(original.CLOSURES[original.NAME])
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==original.SOURCE and value['originalManifestSha256']==RAW[1],'actual source/run')
        require((value['tests'],value['suites'],value['targetSourceUnits'],value['newTestIds'])==(8,1,1,0) and value['cases']==raw['cases'],'unchanged whole16')
        require(value['completeSourceUnitClosure']==original.CLOSURES and set(value['physicalClasses'])==physical and set(value['executable'])==physical-{original.NAME+'$Crypto'} and value['metadataClasses']==[original.NAME+'$Crypto'] and value['unexecutedCodeClasses']==[],'complete Source and all three Code')
        require(value['totals']==counts==value['fullSourceUnits'][original.NAME]['totals'] and all(c['missed']==0 for row in value['executable'].values() for c in row['counters'].values()),'all counters no missed')
        require(value['strictFour100GateExit']==0 and value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is True and value['manualCounterExclusions']==[],'actual four100 no exclusions')
        require(value['singleSession'] is True and value['crcMismatch']==0,'one actual exec matching physical CRC')
        require(value['publicRfcSignatureVerificationOnly'] is value['publicRfcKeyMaterialOnly'] is True and value['cryptoOrKeyOperationsInvoked'] is value['publicRfcKeysDecoded'] is True and value['actualSecretKeysLoaded'] is value['actualRuntimeKeyFilesRead'] is value['actualSigningOrKeyPairGeneration'] is False,'synthetic claims not crypto/signature trust')
        require(value['ownThreadCount'] is None and value['declaredOwnWorkerPoolSize']==4 and value['ownTaskCount']==4,'own declared four parser tasks, measured thread count unknown')
        require(len(value['rootRecoveryProbeAudit'])==27 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in value['rootRecoveryProbeAudit'].values()),'no Root recovery execution')
        require(all(value[k] is False for k in ['actualFilesOpenedByProduct','rootMainInvoked','actualPermitIssueSignPublishOrRetire','actualAuthenticationOrSessionIssued','actualCredentialValuesUsed','testPublicUnitSourceRead','testOwnScalarTraceWritten','formalUpdated','whole451Accepted','oldCoverageTransferred']) and value['actualSqlStatementsPreparedOrExecuted']==0 and value['effortPercent'] is None,'no external authority/formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',9),('suites',2),('targetSourceUnits',2),('newTestIds',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('executable',{}),('metadataClasses',[]),('unexecutedCodeClasses',['missing']),('totals',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('manualCounterExclusions',['hidden']),('singleSession',False),('crcMismatch',1),('publicRfcSignatureVerificationOnly',False),('publicRfcKeyMaterialOnly',False),('cryptoOrKeyOperationsInvoked',False),('actualSecretKeysLoaded',True),('publicRfcKeysDecoded',False),('actualRuntimeKeyFilesRead',True),('actualSigningOrKeyPairGeneration',True),('ownThreadCount',4),('ownTaskCount',0),('rootRecoveryProbeAudit',{}),('actualSqlStatementsPreparedOrExecuted',1),('formalUpdated',True),('effortPercent',100)]:
        require(p[key]!=value,'nondegenerate '+key);bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false release claim qualification '+key)
    paths=list((data.ROOT/'documents/300_SS').glob('*/343_*.md'));require(len(paths)==1,'unique approved SS343')
    relative=str(paths[0].relative_to(data.ROOT));body=paths[0].read_bytes();require(body==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS byte')
    for row in [p,old]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=8,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(vectors)+2,rfcPublicTupleSha256=expected_hashes,rfcPublicVectorSource='https://www.rfc-editor.org/rfc/rfc8032.html#section-7.1',rfcPublicVectorViewedJST='2026-10-31T23:33:00+09:00',privateRfcSeedUsedOrStored=False,newSourcePrograms=1,newPhysicalClasses=3,metadataPhysicalClasses=1,four100SourcePrograms=1,approvedDesignHashes={relative:data.sha(body)},productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
