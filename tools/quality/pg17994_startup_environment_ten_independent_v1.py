"""Independent environment/source-zero and original input literals; natural branch N/A, public SHA256."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg17990_startup_environment_ten_pt as original
SOURCE=original.SOURCE
POST=('PG17992-startup-environment-ten-post-v1','7ab47d6e2acfdf8fd9da99c99d11884b0174b94cf001ea986c6f6fea3d20f4da')
RAW='0aaad556590d4bed0ac329b72eee78cbcbb64d24288e12a884b8cdbc036dc020'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17990-startup-environment-ten-pt-v1'
OUT=data.BASE/'PG17994-startup-environment-ten-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17994-startup-environment-ten-independent-v1'
METHODS={'dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest':['opsApiInput001CombinesIndependentFixedInputs','opsApiInput002MissingPrivateLocationStopsBeforeSourceRead','opsApiInput003SourceFailureAndConfigAdmissionStayDistinct','opsApiInput004NullContracts'],'dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest':['opsWebInput001CombinesIndependentFixedInputs','opsWebInput002MissingPrivateLocationStopsBeforeSourceRead','opsWebInput003SourceFailureAndConfigAdmissionStayDistinct','opsWebInput004NullContracts'],'dev.codex.schubert.nk.api.bootstrap.ApiEnvironmentGateContractTest':['environmentGate001FixedConfigRootAndNamespaceAreCheckedWithoutSourceRead'],'dev.codex.schubert.nk.web.bootstrap.WebEnvironmentGateContractTest':['environmentGate001FixedConfigRootAndNamespaceAreCheckedWithoutSourceRead']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG17990-startup-environment-ten-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(10,4,2,4),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==10 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':26},'METHOD':{'missed':0,'covered':8},'CLASS':{'missed':0,'covered':4},'BRANCH':{'missed':0,'covered':0}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['four100'] is False and v['fullSourceUnits'][n]['branchNaturallyZero'] is v['fullSourceUnits'][n]['threeCounter100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(type(v['strictFour100GateExit']) is int and v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['allMeasuredApplicableCountersCovered'] is v['naturalZeroBranch'] is True and v['newTestIds']==2 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['nfcAndUtf8ValidationInvoked'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['suppliedNonsecretEnvironmentGuardOnly'] is v['childDescriptorNameRecognitionOnly'] is True and v['actualDescriptorAdoptionOrNativeIo'] is False and v['normalOrdinaryTestSourceDomain']=='MIXED_ORIGINAL_EIGHT_AND_SEPARATE_QUALITY_TWO' and v['normalOrdinaryMethodCount']==8 and v['independentQualityMethodCount']==2 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['publicDigestOnly'] is True and v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',False),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('suppliedNonsecretEnvironmentGuardOnly',False)]:
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
    for kind,prefix in [('Api','API'),('Web','Web')]:
        text=original.TESTS[kind+'EnvironmentGateContractTest'].read_text()
        for token in ['assertDoesNotThrow(new '+kind+'StartupInputs(source, environment)::validateEnvironment)','new String[] {"", "/other", "/etc/schubert-nk/", "/etc/../etc/schubert-nk"}','environment.remove("SCHUBERT_NK_CONFIG_DIR")','environment.put("SCHUBERT_NK_CONFIG_DIR", null)','environment.put("SCHUBERT_NK_UNKNOWN", "PUBLIC_VALUE")','assertEquals(0, reads.get())','"'+prefix+' non-secret environment unavailable"','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)']:
            require(token in text,'independent config-root/namespace/source-zero oracle '+token)
        require(not any(x in text for x in ['Files.','getenv(','LinuxDirectoryCalls','new ChildStartupContext','DriverManager','Socket','.production(','Executors.']), 'no new runtime/native/private IO')
        whole=original.TESTS[kind+'StartupInputsTest'].read_text()
        for token in ['assertEquals("DEBUG", result.config().value("nk.monitoring.mode"))','assertEquals(Path.of(ROOT), result.credentials().directory())','assertEquals(1, reads.get())','"service credential location unavailable"','assertEquals(0, reads.get())','assertSame(\n        failure,','new '+kind+'StartupInputs.Values(null, credentials)','new '+kind+'StartupInputs.Values(config, null)']:
            require(token in whole,'unchanged original nonsecret config/location/null oracle '+token)
    for path,pin in original.PUBLIC_READS.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'closed auxiliary parser/loader/value reference unchanged')
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
    require(len(crc)==4 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=10,suites=4,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,suppliedNonsecretEnvironmentGuardOnly=True,publicDigestOnly=True,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=10,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=2,requiredRepeatedMethods=8,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
