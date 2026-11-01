"""Independent Web HTTP/exception/deadline literals and passive original eight Test CRC classes."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17816_admission_actual_wait_five_pt as original
SOURCE=original.SOURCE
POST=('PG17818-admission-actual-wait-five-post-v1','42a733fb6590631f6e6f52886a0a01853c036d9a167b28aeab0ea4e1267ab180')
RAW='6eddd61a889e0ebb85a9f1eb3451ace5a272c803e1ee3b606cada04a21203f8e'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17816-admission-actual-wait-five-pt-v1'
OUT=data.BASE/'PG17820-admission-actual-wait-five-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17820-admission-actual-wait-five-independent-v1'
METHODS={
'dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionTest':['stop005OwnerTermRefusesImmediatelyWithoutWaitingForOwnerPolling','stop001002BoundaryInterruptAndConcurrentCompletion','stop003ActualAsyncRemainsOwnedAfterServletReturns'],
'dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionWaitingContractTest':['admissionWait001CompletionAfterActualTimedWaitIsConfirmed','admissionWait002InterruptDuringActualTimedWaitIsUnconfirmedAndRestored']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17816-admission-actual-wait-five-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(5,2,1,1),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==5 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':48},'METHOD':{'missed':0,'covered':9},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':24}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['newTestIds']==2 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions'] is None and v['actualOwnedLoopbackFixtureNetwork'] is True and v['actualExternalNetworkActions']==v['actualProductionServiceActions']==0,'actual self-owned network, operation count unknown not zero')
        require(raw['begin']['declaredLoopbackAddresses']==['127.0.0.1'] and raw['actualOwnedLoopbackNetworkExercised'] is True and raw['actualNetworkScopeProof']=='ALL_EXPECTED_CASES_PASS_ASSERT_REAL_LOOPBACK_TRANSACTIONS','raw scoped actual HTTP assertion witness')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is True and v['ownThreadCount'] is None and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['publicClasspathTemplatesOpened'] is True and v['transientOwnWildcardPortRebindWithoutAccept'] is False and v['actualJdbcBackendConnected'] is False and v['declaredOwnExecutorInstances']==v['declaredOwnTaskCount']==3 and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',4),('suites',1),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',0),('actualOwnedLoopbackFixtureNetwork',False),('actualExternalNetworkActions',1),('actualProductionServiceActions',1),('testOwnJavaMonotonicClockRead',False),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',False),('ownThreadCount',0),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',False),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['testSourceHashes'][str(path)]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    waiting=original.TESTS['WebHttpAdmissionWaitingContractTest'].read_text();admission=original.TESTS['WebHttpAdmissionTest'].read_text()
    for token in ['Thread.State.TIMED_WAITING','worker.set(Thread.currentThread())','assertTrue(entered.await(3, TimeUnit.SECONDS))','assertFalse(result.isDone(),','worker.get().interrupt()','gate.completed()','result.get(3, TimeUnit.SECONDS)','assertEquals(!interrupt, outcome.confirmed())','assertEquals(interrupt, outcome.interrupted())','assertEquals("Web HTTP drain unconfirmed", outcome.failure().getMessage())','assertNull(outcome.failure().getCause())','assertEquals(0, outcome.failure().getSuppressed().length)','Thread.interrupted()','executor.shutdownNow()','assertTrue(executor.awaitTermination(3, TimeUnit.SECONDS))']:
        require(token in waiting,'independent actual-wait/termination/exception oracle '+token)
    require(waiting.index('worker.set(Thread.currentThread())')<waiting.index('entered.countDown()') and waiting.index('assertTrue(entered.await')<waiting.index('worker.get().getState()'),'null-safe captured worker publication, no result-derived expected')
    for token in ['assertEquals(503, get(client, base + FIXTURE_LOGIN_F843C044).statusCode())','assertEquals(200, get(client, base + FIXTURE_LOGIN_F843C044).statusCode())','assertThrows(IOException.class, () -> gate.drain(Duration.ZERO))','assertTrue(Thread.interrupted())','assertTrue(waiting.get(3, TimeUnit.SECONDS))','assertEquals("done", result.body())','assertThrows(IllegalStateException.class, server::port)']:
        require(token in admission,'unchanged original lease/async oracle '+token)
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[n.replace('.','/') for n in METHODS]
    for name in names:
        src=RUN/'fresh-test-classes'/(name+'.class');dst=component/(name+'.class');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);physical[name]=data.sha(src.read_bytes())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    require(data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3','qualified passive class')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(all(data.sha(Path(k).read_bytes())==v for k,v in runtime['toolAndDependencyHashes'].items()),'same reader SDK')
    stage=runner.step('passive-original-test-crc',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*names],SLOT,timeout=120)
    require(stage['actualExit']==0 and not stage['timedOut'],'same original Test CRC')
    lines=(SLOT/'passive-original-test-crc.stdout').read_text().splitlines();crc=[v.split(chr(9)) for v in lines if v.startswith('CLASS'+chr(9))]
    require(len(crc)==2 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=5,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=5,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=0,partialSourcePrograms=0,measuredSourcePrograms=1,measuredPhysicalClasses=1,newUniqueMethods=2,requiredRepeatedMethods=3,actualOwnedLoopbackFixtureNetwork=True,networkOperationCount=None,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
