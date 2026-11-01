"""Independent Web HTTP/exception/deadline literals and passive original eight Test CRC classes."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17786_web_mvc_loopback_fifteen_pt as original
SOURCE=original.SOURCE
POST=('PG17788-web-mvc-loopback-fifteen-post-v1','404e3c94fb1fb6be7444c86647c38b53fa071a68d22fc0783a40120822c97bfb')
RAW='f7f82c9e3d5606ce8b54d484cb09e0ceca353b1cf00952248c40cc4da7dea58d'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17786-web-mvc-loopback-fifteen-pt-v1'
OUT=data.BASE/'PG17790-web-mvc-loopback-fifteen-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17790-web-mvc-loopback-fifteen-independent-v1'
METHODS={
'dev.codex.schubert.nk.web.bootstrap.WebHttpServerTest':['httpOwn003FailedSupplierIdentityAndNullNeverNotifyOwner','nativeOwner001CapturePrecedesVendorStartAndFatalKeepsRetryableOwner','nativeOwner002ActualOwnedSuccessAndNullRefusal','nativeOwner003LegacyFatalCleanupPreservesIdentityAndSelfSuppression','rerun008UnknownHttpStopAndDestroyRemainRetryableWithoutSkippingPhase','scr109ActualLoopbackLoginAndClosedRoutes','scr110InvalidStartupFailsBeforeBinding','scr112StartupWithoutStartedContextAndCleanupFailureAreVisible','scr111CloseIsIdempotentAndPortBecomesUnavailable','scr120CallerOwnedPortReachesRealFeatureController','scr121InvalidPortRegistrationFailsBeforeTomcatCreation','scr123LegacyFactoryOverloadReturnsStartedServer'],
'dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionTest':['stop005OwnerTermRefusesImmediatelyWithoutWaitingForOwnerPolling','stop001002BoundaryInterruptAndConcurrentCompletion','stop003ActualAsyncRemainsOwnedAfterServletReturns']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17786-web-mvc-loopback-fifteen-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(15,2,2,2),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==15 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':10,'covered':153},'METHOD':{'missed':0,'covered':24},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':5,'covered':67}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions'] is None and v['actualOwnedLoopbackFixtureNetwork'] is True and v['actualExternalNetworkActions']==v['actualProductionServiceActions']==0,'actual self-owned network, operation count unknown not zero')
        require(raw['begin']['declaredLoopbackAddresses']==['127.0.0.1'] and raw['actualOwnedLoopbackNetworkExercised'] is True and raw['actualNetworkScopeProof']=='ALL_EXPECTED_CASES_PASS_ASSERT_REAL_LOOPBACK_TRANSACTIONS','raw scoped actual HTTP assertion witness')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is True and v['ownThreadCount'] is None and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['publicClasspathTemplatesOpened'] is v['transientOwnWildcardPortRebindWithoutAccept'] is True and v['actualJdbcBackendConnected'] is False and v['declaredOwnExecutorInstances']==v['declaredOwnTaskCount']==1 and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',14),('suites',1),('targetSourceUnits',1),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',0),('actualOwnedLoopbackFixtureNetwork',False),('actualExternalNetworkActions',1),('actualProductionServiceActions',1),('testOwnJavaMonotonicClockRead',False),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',False),('ownThreadCount',0),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',False),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
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
    server=original.TESTS['WebHttpServerTest'].read_text();admission=original.TESTS['WebHttpAdmissionTest'].read_text()
    for token in ['assertEquals(200, login.statusCode())','assertEquals("schubert NK - ログイン", document.title())','assertEquals("fixture", document.selectFirst("input[name=_csrf]").val())','assertEquals(1, destroys.get())','assertEquals(mode == 1 ? 1 : 0, primary.getSuppressed().length)','assertSame(secondary, primary.getSuppressed()[0])','assertEquals("PG227-PORT", response.body())','assertEquals(0, starts.get())','assertEquals("synthetic startup failure", failure.getMessage())','assertEquals("synthetic cleanup failure", failure.getSuppressed()[0].getMessage())']:
        require(token in server,'independent original HTTP/identity/cleanup oracle '+token)
    for token in ['assertEquals(503, get(client, base + FIXTURE_LOGIN_F843C044).statusCode())','assertEquals(200, get(client, base + FIXTURE_LOGIN_F843C044).statusCode())','assertThrows(IOException.class, () -> gate.drain(Duration.ZERO))','assertTrue(Thread.interrupted())','assertTrue(waiting.get(3, TimeUnit.SECONDS))','assertEquals("done", result.body())','assertThrows(IllegalStateException.class, server::port)']:
        require(token in admission,'independent async/lease/deadline oracle '+token)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=15,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=15,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,partialSourcePrograms=2,measuredSourcePrograms=2,measuredPhysicalClasses=2,actualOwnedLoopbackFixtureNetwork=True,networkOperationCount=None,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
