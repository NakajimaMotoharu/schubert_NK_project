"""Independent SS343 ASCII marker/invariant oracles; original eight and pure four CRC."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17970_pure_retirement_codec_twelve_pt as original
SOURCE=original.SOURCE
POST=('PG17972-pure-retirement-codec-twelve-post-v1','651a946af4db1a730567d32c7bb1484b002a33d72ffcea2410940820547124a2')
RAW='5bb7b7fdc77ba7fe89b06112999f8ae06649a2f27955ace7aaf8af918a1f9dfe'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17970-pure-retirement-codec-twelve-pt-v1'
OUT=data.BASE/'PG17974-pure-retirement-codec-twelve-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17974-pure-retirement-codec-twelve-independent-v1'
METHODS={'dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest':['literalRecords','identityTemporalBoundaries','malformedSources','scalarAliases','completionInvariants','nullContracts','ownershipAndRedaction','concurrentUse'],'dev.codex.schubert.nk.batch.file.PureRetirementCodecContractTest':['retirementCodec001CanonicalMarkersUseIndependentExactBytesAndPositiveCounts','retirementCodec002EveryValueInvariantHasAnIndependentBoundary','retirementCodec003NonCanonicalOrMalformedMarkersHaveOneFixedDiagnostic','retirementCodec004NullsOwnershipAndRedactionNeverIssuePermission']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17970-pure-retirement-codec-twelve-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(12,2,2,2),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==12 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':83},'METHOD':{'missed':0,'covered':18},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':0,'covered':31}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['newTestIds']==4 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is True,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['nfcAndUtf8ValidationInvoked'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['pureRetirementRecordCodecOnly'] is v['testOwnRelativePublicTraceFilesWritten'] is v['testOwnTemporaryContentWritten'] is True and v['actualRetirementOrGcOperations']==0 and v['normalOrdinaryTestSourceDomain']=='MIXED_ORIGINAL_EIGHT_AND_SEPARATE_QUALITY_FOUR' and v['normalOrdinaryMethodCount']==8 and v['independentQualityMethodCount']==4 and v['declaredOwnExecutorInstances']==1 and v['declaredOwnTaskCount']==64 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount'] is None and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',False),('publicFixedUuidFixtureOnly',False),('physicalClasses',{'unknown':'0'*64}),('pureRetirementRecordCodecOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['testSourceHashes'][str(path)]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    text=original.TESTS['PureRetirementCodecContractTest'].read_text()
    for token in ['"NKRET1\\n" + ID','count == 1 ? 195 : 204','"2147483647"','"2020-01-01T00:00:00.000000Z"','"2021-02-04T00:00:00.000001Z"','"2021-02-04T00:00:00Z"','"2021-02-03T23:59:59.999999Z"','"9999-12-31T23:59:59.999999Z"','"a".repeat(63)','"A".repeat(64)','"g".repeat(64)','new byte[0]','Arrays.copyOf(original, 194)','Arrays.copyOf(original, 205)','"\\n0000000001\\n"','"\\n+1\\n"','high[20] = (byte) 128','extraField[20] = \'\\n\'','MaintenanceRecords.readRetirement(null)','"MaintenanceRetirement[identity/time/plan=<redacted>]"','"maintenance record is invalid"','"invalid maintenance retirement"','assertNotSame(first, second)','Arrays.fill(second, (byte) 0)']:
        require(token in text,'independent canonical ASCII/400day/null/ownership oracle '+token)
    require(not any(x in text for x in ['LinuxDirectoryCalls','OwnedTransferDirectory','Files.','DriverManager','RootFailedStartRecovery','getConnection(','Executors.']), 'new pure codec does not replace actual GC/native/storage')
    whole=original.TESTS['MaintenanceRecordsTest'].read_text()
    for token in ['Path.of("target/maintenance-record-traces")','Executors.newFixedThreadPool(8)','future.get(5, TimeUnit.SECONDS)','assertEquals(64, actual.size())','assertEquals(32, warnings)','assertArrayEquals(ascii(ANCHOR), anchorBytes)']:
        require(token in whole,'unchanged original owned literal/parallel oracle '+token)
    for path,pin in original.PUBLIC_READS.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'auxiliary pure value callee unchanged')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=12,suites=2,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureRetirementRecordCodecOnly=True,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=12,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=4,requiredRepeatedMethods=8,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
