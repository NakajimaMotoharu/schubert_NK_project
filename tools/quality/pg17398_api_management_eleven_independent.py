"""Independent HTTP/ownership literals and scoped network disclosure; passive original Test CRC."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17395_api_management_eleven_pt_v3 as original
SOURCE=original.SOURCE
POST=('PG17396-api-management-eleven-post-v2','d0c5dbda2ec74f00bb1f6bf136c70ab9a15d3ac75673303a1d4ddd5617584ede')
RAW='34557bd7fd577a3f5c0d06f1a4d4788e64909df20f054e85746930e49657626d'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17395-api-management-eleven-pt-v3'
OUT=data.BASE/'PG17398-api-management-eleven-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17398-api-management-eleven-independent-v1'
METHODS={
'dev.codex.schubert.nk.api.bootstrap.ApiManagementServerTest':['httpOwn001FactoryFailureIdentityAndNullAreNotStarted','ready005JdkStopMustPreserveCallerInterruptFlag','ready003ActualVendorStartedServerFailureClosesBoundOwner','ready001ActualDownUpDownPublicOnlyAndClosedRoutes','ready002HandoffFailureAndConcurrentStopNeverPromote','ready004OwnerClosedDuringAdmissionReleaseCannotPublishUp','ready003InformationNullUnknownInvalidAndRealBindCollision'],
'dev.codex.schubert.nk.api.bootstrap.ApiManagementStopTest':['apiStop001FailedStopNeverMakesLaterCloseAFalseSuccess','apiStop002InvalidBudgetsLeaveReadyOwnerUntouched','apiStop003LockDeadlineAndNewInterruptNeverDuplicateStop','apiStop004WorkerTimeoutInterruptAndActualRejoinRemainDistinct']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17395-api-management-eleven-pt-v3/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(11,2,1,2),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==11 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':17,'covered':130},'METHOD':{'missed':4,'covered':17},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':15,'covered':67}},'complete partial counters')
        require(set(v['fullSourceUnits'])=={original.NAME} and set(v['fullSourceUnits'][original.NAME]['physical'])==set(original.CLOSURES[original.NAME]) and v['fullSourceUnits'][original.NAME]['four100'] is False,'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions'] is None and v['actualOwnedLoopbackFixtureNetwork'] is True and v['actualExternalNetworkActions']==v['actualProductionServiceActions']==0,'actual self-owned network, operation count unknown not zero')
        require(raw['begin']['declaredLoopbackAddresses']==['127.0.0.1'] and raw['actualOwnedLoopbackNetworkExercised'] is True and raw['actualNetworkScopeProof']=='ALL_EXPECTED_CASES_PASS_ASSERT_REAL_LOOPBACK_TRANSACTIONS','raw scoped actual HTTP assertion witness')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is True and v['ownThreadCount'] is None and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',12),('suites',1),('targetSourceUnits',2),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',0),('actualOwnedLoopbackFixtureNetwork',False),('actualExternalNetworkActions',1),('actualProductionServiceActions',1),('testOwnJavaMonotonicClockRead',False),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',False),('ownThreadCount',0),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['sourceHashes'][str(path.relative_to(data.ROOT))]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    server=original.TESTS['ApiManagementServerTest'].read_text();stop=original.TESTS['ApiManagementStopTest'].read_text()
    for token in ['assertEquals(503,','assertEquals(200,','assertEquals(404,','assertEquals(405,','"no-store"','"a".repeat(40)','"/actuator/%69nfo"','"/actuator/shutdown"','assertEquals(8091, server.port())','assertEquals(1, releases.get())','get(replacement,','Thread.interrupted();']:
        require(token in server,'independent HTTP/ownership oracle '+token)
    for token in ['new InetSocketAddress','HttpServer.create(address, backlog)','getHostAddress()','assertEquals(0, address.getPort())','assertEquals(32, backlog)','assertEquals(\n            2, captured.get().stops.get()','Duration.ZERO','Duration.ofSeconds(30).plusNanos(1)','second.interrupt()','executor.awaitTermination(5, TimeUnit.SECONDS)','while (!condition.getAsBoolean() && System.nanoTime() - deadline < 0) Thread.sleep(1);']:
        if token=='new InetSocketAddress':continue
        require(token in stop,'independent stop/worker oracle '+token)
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'original-test-component';component.mkdir();physical={}
    names=[n.replace('.','/') for n in METHODS]+['dev/codex/schubert/nk/api/bootstrap/ApiManagementStopTest$StopFailureServer']
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
    require(len(crc)==3 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=11,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=11,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=2,metadataPhysicalClasses=1,partialSourcePrograms=1,actualOwnedLoopbackFixtureNetwork=True,networkOperationCount=None,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
