"""Independent seven original failure-priority oracles; whole Source and exact physical metadata."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16414_process_scope_original_seven_pt import NAME,CLOSURES,METADATA,SOURCE

POST=('PG16416-process-scope-original-seven-post-v1','b8be11c72b5711b54148e5e71f23af4e94db1196655bac3dd7b8972ec61aba3d')
RAW=('PG16414-process-scope-original-seven-pt-v1','02ba364646cec1677ed33a35cccb22f94adfa047102cbee668480d280c070c5b')
PREV=('PG16404-current2182-legacy-policy-registry-v1','34386ddf6c7fe6c067f5b5909735d8f487de5a8fc0b95d959bedb201b8ed9889')
OUT=data.BASE/'PG16418-process-scope-original-seven-independent-v1'
METHODS=['queryown001LiteralTwentyFourFailurePriorityRows','queryown002FactoryAndNullBoundariesNeverReleaseUnownedResource','queryown003SharedAndPreexistingExceptionsKeepIdentityWithoutSelfSuppression','queryown004ParallelScopesRetainDistinctOwnersAndReverseNestedRelease','queryown005SystemctlDefersNullButOwnsEveryPriorGetter','queryown006InspectorRejectsEachMissingGetterBeforeNextInBothModes','queryown007StreamingDeadlineAndDrainCancellationUseIndependentMonotonicVectors']
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [p,raw,old]),'genuine current chain')
    path=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScopeTest.java';blob=path.read_bytes();text=blob.decode()
    require(data.sha(blob)==raw['begin']['testSourceHashes'][str(path)]=='cf94df05fa8559b35af74879256271b41df718f7f5eb1b5251cc0a9f42d99d06','whole fixed original')
    require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==METHODS,'seven whole original methods')
    expected={('dev.codex.schubert.nk.batch.platform.ProcessResourceScopeTest',name) for name in METHODS};actual=[]
    for file,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/file).read_bytes();require(data.sha(b)==pin,'original XML')
        xml=ET.fromstring(b);require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in xml.findall('testcase'):require(not list(case),'no nonpass');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==7 and set(actual)==expected and not expected&{(v['classname'],v['name']) for v in old['cases']},'current first unique seven')
    oracles=[
        ['"Ncre", "bbce", "bbce", "bbce", "bbbb", "bbbb"','List.of(false, true)','assertSame(expected == \'b\' ? body : cleanup, actual)'],
        ['new IOException("private factory")','new IllegalStateException("private factory")','new AssertionError("private factory")','assertEquals(0, calls.get())'],
        ['same.addSuppressed(original)','assertEquals(count + 1, same.getSuppressed().length)','assertSame(original, same.getSuppressed()[0])'],
        ['Thread.startVirtualThread(task)','"left inner", "left outer"','"right inner", "right outer"','thread.join(5000)','assertFalse(thread.isAlive())'],
        ['new SystemctlStateSource(command -> child)','missing ? 3 : index + 1','assertEquals(0, child.waits)'],
        ['new InspectorUnitProbe.NativeReader(command -> child)','assertEquals(index + 1, child.getters)','new InspectorUnitProbe.NativeReader(command -> null)'],
        ['List.of("beforeWait", "wait", "exit", "beforeGet", "timeout", FIXTURE_INTERRUPT_DDE42D5D)','TimeUnit.SECONDS.toNanos(1)','assertEquals(0, starts.get())','child.drained.countDown()']]
    require(all(all(token in text for token in row) for row in oracles),'independent literal/identity/finite-time oracle')
    design=list((data.ROOT/'documents/300_SS/340_batch・基盤').glob('343_*.md'));require(len(design)==1,'SS343 unique')
    relative=str(design[0].relative_to(data.ROOT));approved=design[0].read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved design same byte')
    counts={k:dict(covered=n,missed=0) for k,n in [('LINE',32),('METHOD',2),('CLASS',1),('BRANCH',22)]}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW[1],'actual current source/run')
        require((v['tests'],v['suites'],v['newTestIds'],v['targetSourceUnits'])==(7,1,0,1) and v['cases']==raw['cases'],'whole original seven')
        require(v['completeSourceUnitClosure']==CLOSURES and set(v['physicalClasses'])==set(CLOSURES[NAME]) and set(v['fullSourceUnits'])=={NAME} and set(v['executable'])=={NAME} and set(v['metadataClasses'])==METADATA,'exact Source/Code/NoCode before lookup')
        require(v['totals']==v['fullSourceUnits'][NAME]['totals']==v['executable'][NAME]['counters']==counts,'whole four counters no miss')
        require(all(not any(m['hasCode'] for m in v['sourcePhysicalInventory'][n]['methods']) for n in METADATA),'genuine two abstract interfaces')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['strictFour100GateExit']==0 and v['targetUnitFour100'] is v['allMeasuredApplicableCountersCovered'] is True and v['manualCounterExclusions']==[],'one exec all full')
        require(v['existingFakeProcessFixtureUsed'] is True and v['productExternalProcessesStarted']==0 and v['defaultNativeCallbackInvoked'] is False and v['ownThreadCount'] is None and v['declaredOwnOwnerThreads']==2 and v['ownTaskCount']==2,'fake Process and declared versus measured threads')
        require(all(v[k] is False for k in ['actualPermitIssueSignPublishOrRetire','cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and v['effortPercent'] is None,'no cross-domain acceptance')
    contract(p);negative=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',8),('suites',2),('newTestIds',1),('targetSourceUnits',2),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('fullSourceUnits',{}),('executable',{}),('metadataClasses',[]),('totals',{}),('singleSession',False),('crcMismatch',1),('strictFour100GateExit',1),('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('manualCounterExclusions',[NAME]),('existingFakeProcessFixtureUsed',False),('productExternalProcessesStarted',1),('defaultNativeCallbackInvoked',True),('ownThreadCount',2),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false scope qualification '+key)
    for v in [p,old]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=7,suites=1,semanticNegativeVectors=len(negative),negativeLabels=negative,independentOracleVectors=7,sourcePrograms=1,physicalClasses=3,metadataPhysicalClasses=2,four100SourcePrograms=1,wholeSourceIncompleteCount=0,approvedDesignHashes={relative:data.sha(approved)},productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
