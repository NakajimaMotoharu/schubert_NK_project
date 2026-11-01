"""Independent public metadata copies/limits/null; no crypto operation or actual replay acceptance."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18300_web_terminal_flag_four_pt as original
SOURCE=original.SOURCE
POST=('PG18302-web-terminal-flag-four-post-v1','df15b6c4de3afa0ddcddd150564a9b9ff860737950ecc907cbeda100b20d5777')
RAW='af06a7c2c8b234835b61c148d8bb3f0d9271b0f4b9e136bf081d1b370632c398'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18300-web-terminal-flag-four-pt-v1'
OUT=data.BASE/'PG18304-web-terminal-flag-four-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18304-web-terminal-flag-four-independent-v1'
METHODS={"dev.codex.schubert.nk.web.bootstrap.WebTerminalFlagContractTest":["signalValue001MissingCapturedFlagRejects","signalValue002RunnableMutatesTheSameCallerFlagAndIsIdempotent","signalValue003ConsumerSignalsWithoutMutatingThrowableValues","signalValue004ConcurrentNotificationsFinishBeforeOwnedPoolIsClosed"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18300-web-terminal-flag-four-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(4,1,1,1),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==4 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':7},'METHOD':{'missed':0,'covered':3},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':0}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and (v['fullSourceUnits'][n]['four100'] is False and v['fullSourceUnits'][n]['branchNaturallyZero'] is True) for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is True and v['newTestIds']==4 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['nfcAndUtf8ValidationInvoked'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['pureCapturedTerminalFlagOnly'] is True and v['actualAdminMutationOrAuthorization'] is v['actualBusinessProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==4 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['syntheticEncryptedPayloadMetadataOnly'] is False and v['actualPayloadEncryptionOrDecryption'] is v['actualJmsIsolationOrCommitInvoked'] is False,'synthetic metadata, not crypto or actual commit')
        require(v['selfOwnedExecutorFixtureInvoked'] is True and v['declaredOwnExecutorInstances']==1 and v['declaredOwnTaskCount']==64 and v['declaredOwnPlatformThreadMaximum']==4 and v['actualAllJvmThreadCount'] is None,'explicit self-owned workers, not process thread total')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==v['actualOwnPlatformThreadCount'] and 1<=v['ownThreadCount']<=4 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrBusinessProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['jdkNamedTimeZoneInitializationInvoked'] is False and v['businessDateConversionInvoked'] is False and v['jdkTimezoneProviderCallsAndResourceReads'] is None and v['fileEffectBoundary']=='NO_EXPLICIT_APPLICATION_FILE_API; PLATFORM_INITIALIZATION_IO_UNOBSERVED','no fabricated JDK timezone/IO absence')
        require(v['publicSyntheticFingerprintDigestBytesOnly'] is False and v['publicSyntheticCiphertextBytesOnly'] is False and v['actualHmacOrEncryptionPerformed'] is False,'public data only; no HMAC/AES/keyring')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',-1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureCapturedTerminalFlagOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for key,value in [('jdkNamedTimeZoneInitializationInvoked',True),('businessDateConversionInvoked',True),('jdkTimezoneProviderCallsAndResourceReads',0),('fileEffectBoundary','ALL_IO_ABSENT')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false JDK initialization disclosure')
    for key,value in [('publicSyntheticFingerprintDigestBytesOnly',True),('publicSyntheticCiphertextBytesOnly',True),('actualHmacOrEncryptionPerformed',True),('syntheticEncryptedPayloadMetadataOnly',True),('actualPayloadEncryptionOrDecryption',True),('actualJmsIsolationOrCommitInvoked',True),('selfOwnedExecutorFixtureInvoked',False),('declaredOwnTaskCount',0),('actualAllJvmThreadCount',0)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false crypto effect boundary')
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['testSourceHashes'][str(path)]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    text=original.TESTS['WebTerminalFlagContractTest'].read_text()
    for token in ["new WebRuntimeFailureSignal<Throwable>(null)","signal.run()","captured.set(false)","signal.accept(ordinary)","signal.accept(fatal)","\"PUBLIC_FLAG\"","i < 64","Executors.newFixedThreadPool(4)","pool.invokeAll(jobs, 5, TimeUnit.SECONDS)","assertEquals(64, futures.size())","assertTrue(future.isDone())","assertFalse(future.isCancelled())","assertTrue(pool.isTerminated())","workers.size() >= 1 && workers.size() <= 4","\"SIGNAL_OWNED_WORKERS=\""]:
        require(token in text,'independent flag/owned task/resource invariant '+token)
    require(not any(x in text for x in ['DriverManager','getConnection(','FingerprintKeyRing','ResponseSnapshotCodec','Mac.getInstance','Cipher.getInstance','preserveFatal(','Files.','Instant.now','randomUUID']), 'no key/crypto/held fixture/DB')
    for path,pin in original.PUBLIC_READS.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'typed protocol helper reference unchanged')
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
    require(len(crc)==1 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=4,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureCapturedTerminalFlagOnly=True,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=4,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=4,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
