"""Independent public-provider12 literals/absence boundary and original Test CRC, no native authority."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17620_checkpoint_public_provider_twelve_pt_v1 as original
SOURCE=original.SOURCE
POST=('PG17622-checkpoint-public-provider-twelve-post-v1','763b612944c5e1559664c5ff6d99ec9b3de81459a30c4bb3c0036f2091645745')
RAW='2b1c9fe2b25c4f058b64649c2b15dd916d7ca92f9370fe73b86ce3a6ce5b45b9'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17620-checkpoint-public-provider-twelve-pt-v1'
OUT=data.BASE/'PG17624-checkpoint-public-provider-twelve-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17624-checkpoint-public-provider-twelve-independent-v1'
METHODS={"dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpointTest":["common922001CurrentJvmFactoryRejectsMissingRoleWithoutCreatingAgentAuthority","ncheck597005TerminalFactoryWithNoReservedAgentDoesNotCreateNativeAuthority","ncheck597001RealPublicReflectionReadsLiteralDataWithoutReset","ncheck597002ConstructorMissingNullTypeAndProviderFailuresNeverExposeRawCause","ncheck597003NullWrongTypesAndReflectionFailuresAtEveryPublicGetterAreFixed","ncheck597004CodeSourceMetadataNullLocationForeignAndFixedPathAreSeparate","ncheck193001DefaultDoesNotLoadReservedAgentOrOutput","ncheck193002FourRolesAndTwoRootPointsHaveIndependentNamesAndNoReset","ncheck193003UnknownVersionSessionNullShortLargeHeaderAndChangedSessionReject","ncheck193004NullAndOrdinaryBeforeExecCannotConsumeOrExport","ncheck193005KnownOrUnknownExportNeverRetriesOrNormalizes","ncheck193006ConcurrentCaptureHasExactlyOneDataAndExport"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17620-checkpoint-public-provider-twelve-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(12,1,1,8),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==12 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':9,'covered':89},'METHOD':{'missed':3,'covered':16},'CLASS':{'missed':0,'covered':3},'BRANCH':{'missed':6,'covered':69}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount'] is None and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',[]),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100)]:
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
    text=original.TESTS['FixedNativeCoverageCheckpointTest'].read_text()
    tokens=['byte[] GOLDEN = {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1}','assertFalse(fixture.reset)','assertEquals(1, fixture.reads)','List.of("getAgent", "getVersion", "getSessionId", "getExecutionData")','agentRefused(FixedNativeCoverageCheckpoint.PublicAgent::new)','"/PUBLIC_WRONG/agent.jar"','"/opt/pgpt-tools-pg390/jacoco-agent.jar"','Metadata-only path check is not hash/owner/real-Unit/authority acceptance.','List.of("getVersion", "getSessionId", "getExecutionData")','"version"','"session"','"changedVersion"','"changedSession"','"null"','"short"','"large"','"header0"','"header1"','"header2"','"header3"','"header4"','new byte[16 * 1024 * 1024 + 1]','assertEquals(0, exports.get())','assertEquals(before, agent.dataCalls)','assertEquals(1, exports.get())','newFixedThreadPool(4)','n < 32','result.get(5, TimeUnit.SECONDS)','assertEquals(1, winners)','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)']
    for token in tokens:require(token in text,'independent original provider/ownership literal '+token)
    require('setAccessible' not in text and 'ProcessBuilder' not in text and 'System.setProperty' not in text and 'NativeCoveragePrivateFile' not in text,'no private reflection/child/profile modification/exporter invocation in whole Test')
    main=(data.ROOT/original.source_path(original.MAIN_UNITS[original.NAME])).read_text()
    require(main.index('if (profile.isEmpty()) return Optional.empty();')<main.index('NativeCoveragePrivateFile.verifyPinnedAgent();'),'default reserved-absent returns before native file gate')
    native_key='dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile'
    require(p['reviewedInactiveBoundaryAudit'][native_key]==dict(recordPresent=False,trueProbeHits=0),'real native private exporter absent, not synthetic qualification')
    require(p['publicOnlyReflectionInvoked'] is True and p['syntheticAgentProviderCallsInvoked'] is True and p['syntheticMemoryExportCallbacksInvoked'] is True and p['actualNativeExporterOperation'] is False and p['testOwnPublicClassResourceRead'] is True,'honest public metadata/fake provider effects')
    require(p['declaredOwnPlatformThreadCount']==4 and p['declaredOwnExecutorInstances']==1 and p['declaredOwnTaskCount']==32,'bounded original concurrent schedule, actual thread total unmeasured')
    golden=bytes([0x01,0xC0,0xC0,0x10,0x07,0x10,0x01])
    require(golden.hex()=='01c0c010071001' and len(golden)==7,'independent public format vector not native execution data')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=12,suites=1,independentLiteralGoldenHex=golden.hex(),semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=12,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=8,metadataPhysicalClasses=5,partialSourcePrograms=1,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
