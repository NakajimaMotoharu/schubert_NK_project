"""Independent encoder/interrupt/deadline scalar oracles and Frame Guard-only probe qualification."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16556_management_encoder_original_three_pt as original
POST=('PG16558-management-encoder-original-three-post-v1','74db80ee6173cb1ae309f125572070673008dd3d86cadd70c50186b6ec6e4e54')
RAW=('PG16556-management-encoder-original-three-pt-v1','2e67fbf506cd1129ca9fec9c62485736d60257349eb85f78254edc032456a803')
PREV=('PG16547-current2264-artemis-unknown-registry-v2','a0adfe5eea43bfa8ee31dee06915388363e4ffdb839878c03689aca59c25b2db')
OUT=data.BASE/'PG16560-management-encoder-original-three-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'same actual source')
    name='dev.codex.schubert.nk.batch.mq.ArtemisManagementEncoderBoundaryTest';path=original.TESTS['ArtemisManagementEncoderBoundaryTest'];blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==original.TEST_PINS['ArtemisManagementEncoderBoundaryTest']==raw['begin']['testSourceHashes'][str(path)],'unchanged whole Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==3,'all sixteen declarations');expected={(name,m) for m in methods}
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    require(expected=={(v['className'],v['method']) for v in bindings if v['className']==name} and not expected&{(v['classname'],v['name']) for v in old['cases']},'whole new current methods')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original XML pin');root=ET.fromstring(content)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==3 and set(actual)==expected,'whole original sixteen actual cases')
    vectors=[
      ['assertSame(message, actualMessage)','assertSame(resource, actualResource)','assertSame(operation, actualOperation)','assertSame(arguments, actualArguments)','assertArrayEquals(new Object[] {"PT_SELECTOR", 7L}, actualArguments)'],
      ['new IllegalStateException("PT_PUBLIC_UNKNOWN")','new NullPointerException("PT_PUBLIC_NULL")','var fatal = new AssertionError("PT_PUBLIC_FATAL")','assertSame(marker, actual)'],
      ['new Exception("PT_PUBLIC_PROVIDER")','new InterruptedException("PT_PUBLIC_INTERRUPT")','assertNull(failure.getCause())','failure.getSuppressed().length','declared instanceof InterruptedException'],
      ['checks.incrementAndGet() == 2 && expireBeforeStart','return 1_000_000_000L','assertEquals(2, checks.get())','assertEquals(expireBeforeStart ? 0 : 1, starts.get())'],
      ['throw new ActiveMQException("PT_PUBLIC_START")','assertEquals("start", method.getName())','assertEquals(2000L, ArtemisManagementReadinessClient.requestTimeoutMillis())'],
      ['assertFalse(Thread.currentThread().isInterrupted())','finally {','Thread.interrupted()']]
    require(all(all(v in text for v in group) for group in vectors),'independent forwarding/unknown/checked/interrupt/two-check/start/reset oracles')
    require(not any(v in text for v in ['parentsGuard(', 'queryTimeoutSeconds(', 'new MaintenanceOwnerFrame(', 'ChildStartupContext', 'LinuxMonotonicClock', 'EmbeddedActiveMQ', 'DriverManager', 'ProcessBuilder', 'Files.', 'TemporaryInfrastructureException', 'WebStartupException']),'only supplied scalar lambda and fake session, no actual owner/native/backend/Graph')
    callee='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame.java'
    require(raw['begin']['sourceHashes'][callee]=='48645538321f59775ceca14b6c4ee201db6cbad142e7ca7551e35145f886f4e7'==data.sha((data.ROOT/callee).read_bytes()),'reviewed Guard default method and whole outer initializer source binding')
    counts={k:dict(missed=m,covered=c) for k,m,c in [('LINE',98,26),('METHOD',33,7),('CLASS',0,1),('BRANCH',53,5)]}
    physical=set(original.CLOSURES[original.NAME])
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==original.SOURCE and value['originalManifestSha256']==RAW[1],'actual source/run')
        require((value['tests'],value['suites'],value['targetSourceUnits'],value['newTestIds'])==(3,1,1,0) and value['cases']==raw['cases'],'unchanged whole16')
        require(value['completeSourceUnitClosure']==original.CLOSURES and set(value['physicalClasses'])==physical and set(value['executable'])=={original.NAME} and set(value['metadataClasses'])==physical-{original.NAME} and value['unexecutedCodeClasses']==[],'complete Source and all three Code')
        require(value['totals']==counts==value['fullSourceUnits'][original.NAME]['totals'],'all counters no missed')
        require(value['strictFour100GateExit']==1 and value['targetUnitFour100'] is value['allMeasuredApplicableCountersCovered'] is False and value['manualCounterExclusions']==[],'actual four100 no exclusions')
        require(value['singleSession'] is True and value['crcMismatch']==0,'one actual exec matching physical CRC')
        require(value['borrowedScalarGuardOnly'] is True and value['actualParentAuthorityEstablished'] is value['actualFrameCreated'] is False and value['cryptoOrKeyOperationsInvoked'] is value['actualSecretKeysLoaded'] is False,'synthetic claims not crypto/signature trust')
        require(value['ownThreadCount']==value['ownTaskCount']==0,'own declared four parser tasks, measured thread count unknown')
        frame='dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame';guard=frame+'$Guard';fr=value['maintenanceFrameProbeAudit']
        require(set(fr)=={frame,guard,frame+'$Clock',frame+'$Parent',frame+'$ParentProbe'} and value['maintenanceFrameAllowedScalarInterface']==guard and fr[guard]['recordPresent'] is True and fr[guard]['trueProbeHits']>0 and all(not row['recordPresent'] and row['trueProbeHits']==0 for n,row in fr.items() if n!=guard),'only Guard check probes, not outer Frame/native owner auth')
        require(len(value['rootRecoveryProbeAudit'])==27 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in value['rootRecoveryProbeAudit'].values()),'no Root recovery execution')
        require(all(value[k] is False for k in ['actualFilesOpenedByProduct','rootMainInvoked','actualPermitIssueSignPublishOrRetire','actualAuthenticationOrSessionIssued','actualCredentialValuesUsed','testPublicUnitSourceRead','testOwnScalarTraceWritten','formalUpdated','whole451Accepted','oldCoverageTransferred']) and value['actualSqlStatementsPreparedOrExecuted']==0 and value['effortPercent'] is None,'no external authority/formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',4),('suites',2),('targetSourceUnits',2),('newTestIds',1),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('executable',{}),('metadataClasses',[]),('unexecutedCodeClasses',['missing']),('totals',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('allMeasuredApplicableCountersCovered',True),('manualCounterExclusions',['hidden']),('singleSession',False),('crcMismatch',1),('borrowedScalarGuardOnly',False),('actualParentAuthorityEstablished',True),('actualFrameCreated',True),('maintenanceFrameProbeAudit',{}),('cryptoOrKeyOperationsInvoked',True),('actualSecretKeysLoaded',True),('ownThreadCount',4),('ownTaskCount',1),('rootRecoveryProbeAudit',{}),('actualSqlStatementsPreparedOrExecuted',1),('formalUpdated',True),('effortPercent',100)]:
        require(p[key]!=value,'nondegenerate '+key);bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false release claim qualification '+key)
    paths=list((data.ROOT/'documents/300_SS').glob('*/343_*.md'));require(len(paths)==1,'unique approved SS343')
    relative=str(paths[0].relative_to(data.ROOT));body=paths[0].read_bytes();require(body==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS byte')
    for row in [p,old]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=3,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(vectors),newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=5,partialSourceProgramsMeasured=1,existingSourceProofMustBeRetained=True,approvedDesignHashes={relative:data.sha(body)},reviewedCalleeSha256='48645538321f59775ceca14b6c4ee201db6cbad142e7ca7551e35145f886f4e7',productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
