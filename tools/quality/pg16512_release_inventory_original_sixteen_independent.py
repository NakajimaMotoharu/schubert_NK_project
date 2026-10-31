"""Independent literal release JSON oracle review and actual complete parser counters."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16508_release_inventory_original_sixteen_pt as original
POST=('PG16510-release-inventory-original-sixteen-post-v1','42594a2adf6a6a3bf914262bc67019c8f09592871dc4b78d7e25b675a041a6d1')
RAW=('PG16508-release-inventory-original-sixteen-pt-v1','8726645ea60f442ea55eae754966a201e312554351b497792e0d53b8a1947a71')
PREV=('PG16498-current2236-web-trace-registry-v1','22e410c2d964d99e5a0932286bcebc400490368362f13e82689f1747d8887e1f')
OUT=data.BASE/'PG16512-release-inventory-original-sixteen-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'same actual source')
    name='dev.codex.schubert.nk.bootstrap.ReleaseInventoryTest';path=original.TESTS['ReleaseInventoryTest'];blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==original.TEST_PINS['ReleaseInventoryTest']==raw['begin']['testSourceHashes'][str(path)],'unchanged whole Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==16,'all sixteen declarations');expected={(name,m) for m in methods}
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    require(expected=={(v['className'],v['method']) for v in bindings if v['className']==name} and not expected&{(v['classname'],v['name']) for v in old['cases']},'whole new current methods')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original XML pin');root=ET.fromstring(content)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==16 and set(actual)==expected,'whole original sixteen actual cases')
    vectors=[
      ['assertEquals(13, value.artifacts().size())','assertEquals(3, value.dependencies().size())','assertEquals(2, value.migrations().size())'],
      ['new byte[0]','new byte[1_048_577]','1_048_576 - bytes(golden()).length','new byte[] {(byte) 0xff}'],
      ['Long.MAX_VALUE','"9223372036854775808"','"1e0"','"-0"','"01"'],
      ['"a".repeat(202)','"a".repeat(201)','"a/".repeat(8) + "a"'],
      ['"RELEASE-MANIFEST.json"','"SHA256SUMS"','"api/lib"','"db/migration"'],
      ['"api/lib/unknown.jar"','"api/lib/unknown.txt"','"operations/lib/storage.jar"','"api/lib/zprotocol.jar"'],
      ['"-2147483648"','"2147483647"','"-2147483649"','"2147483648"'],
      ['assertArrayEquals(saved, input)','Arrays.fill(input, (byte) 0)','UnsupportedOperationException.class'],
      ['List.of(2048, 2049)','List.of(512, 513)','assertEquals(1000,','f.migrations.add(SQL)'],
      ['new CyclicBarrier(4)','Executors.newFixedThreadPool(4)','barrier.await(5, TimeUnit.SECONDS)','future.get(5, TimeUnit.SECONDS)']]
    require(all(all(v in text for v in group) for group in vectors),'independent literal caps/numeric/ordering/copy/thread oracles')
    require(not any(v in text for v in ['.inspect(','.verify(','DriverManager','ProcessBuilder','Files.','Signature.','KeyFactory','TemporaryInfrastructureException','WebStartupException']),'original fixture never executes JDBC/crypto/file/native/Graph')
    callee='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.java'
    require(raw['begin']['sourceHashes'][callee]=='4c0d9cd86b28b98d08d223dbb6f87c80f40d1b5226a9361add1ba28ea327fd2c'==data.sha((data.ROOT/callee).read_bytes()),'reviewed constructor/Row invariant binding')
    counts={k:dict(missed=0,covered=c) for k,c in [('LINE',246),('METHOD',29),('CLASS',3),('BRANCH',102)]}
    physical=set(original.CLOSURES[original.NAME])
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==original.SOURCE and value['originalManifestSha256']==RAW[1],'actual source/run')
        require((value['tests'],value['suites'],value['targetSourceUnits'],value['newTestIds'])==(16,1,1,0) and value['cases']==raw['cases'],'unchanged whole16')
        require(value['completeSourceUnitClosure']==original.CLOSURES and set(value['physicalClasses'])==set(value['executable'])==physical and value['metadataClasses']==[] and value['unexecutedCodeClasses']==[],'complete Source and all three Code')
        require(value['totals']==counts==value['fullSourceUnits'][original.NAME]['totals'] and all(c['missed']==0 for row in value['executable'].values() for c in row['counters'].values()),'all counters no missed')
        require(value['strictFour100GateExit']==0 and value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is True and value['manualCounterExclusions']==[],'actual four100 no exclusions')
        require(value['singleSession'] is True and value['crcMismatch']==0,'one actual exec matching physical CRC')
        require(value['pureReleaseManifestClaimsOnly'] is value['syntheticPublicHashLabelsOnly'] is True and value['cryptoOrKeyOperationsInvoked'] is value['actualSecretKeysLoaded'] is False,'synthetic claims not crypto/signature trust')
        require(value['ownThreadCount'] is None and value['declaredOwnWorkerPoolSize']==4 and value['ownTaskCount']==4,'own declared four parser tasks, measured thread count unknown')
        require(len(value['rootRecoveryProbeAudit'])==27 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in value['rootRecoveryProbeAudit'].values()),'no Root recovery execution')
        require(all(value[k] is False for k in ['actualFilesOpenedByProduct','rootMainInvoked','actualPermitIssueSignPublishOrRetire','actualAuthenticationOrSessionIssued','actualCredentialValuesUsed','testPublicUnitSourceRead','testOwnScalarTraceWritten','formalUpdated','whole451Accepted','oldCoverageTransferred']) and value['actualSqlStatementsPreparedOrExecuted']==0 and value['effortPercent'] is None,'no external authority/formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',17),('suites',2),('targetSourceUnits',2),('newTestIds',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('executable',{}),('metadataClasses',['missing']),('unexecutedCodeClasses',['missing']),('totals',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('manualCounterExclusions',['hidden']),('singleSession',False),('crcMismatch',1),('pureReleaseManifestClaimsOnly',False),('syntheticPublicHashLabelsOnly',False),('cryptoOrKeyOperationsInvoked',True),('actualSecretKeysLoaded',True),('ownThreadCount',4),('ownTaskCount',0),('rootRecoveryProbeAudit',{}),('actualSqlStatementsPreparedOrExecuted',1),('formalUpdated',True),('effortPercent',100)]:
        require(p[key]!=value,'nondegenerate '+key);bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false release claim qualification '+key)
    paths=list((data.ROOT/'documents/300_SS').glob('*/343_*.md'));require(len(paths)==1,'unique approved SS343')
    relative=str(paths[0].relative_to(data.ROOT));body=paths[0].read_bytes();require(body==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS byte')
    for row in [p,old]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=16,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(vectors),newSourcePrograms=1,newPhysicalClasses=3,metadataPhysicalClasses=0,four100SourcePrograms=1,approvedDesignHashes={relative:data.sha(body)},reviewedCalleeSha256='4c0d9cd86b28b98d08d223dbb6f87c80f40d1b5226a9361add1ba28ea327fd2c',productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
