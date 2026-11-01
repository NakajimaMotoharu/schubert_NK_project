"""Independent five query catalogs: literal codes/messages, null invariant and four strict/B0 distinction."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18031_query_catalogs_five_pt_v2 as original
SOURCE=original.SOURCE
POST=('PG18032-query-catalogs-five-post-v1','dddbe3c2e48becc1d44be386e444f1e3c94b4ca1ddecc0c9bd606e73b0b51e20')
RAW='6da8524044ce83418527b837e3a885b9aca3f23c3da996ce6b324138ac273498'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18031-query-catalogs-five-pt-v2'
OUT=data.BASE/'PG18034-query-catalogs-five-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18034-query-catalogs-five-independent-v1'
METHODS={"dev.codex.schubert.nk.api.persistence.QueryCatalogContractTest":["queryCatalog001LogCapacityUsesOnlyFixedCodesAndDiagnostic","queryCatalog002MediaCapacityUsesOnlyFixedCodesAndDiagnostic","queryCatalog003ScenarioCapacityUsesOnlyFixedCodesAndDiagnostic","queryCatalog004UserCapacityUsesOnlyFixedCodesAndDiagnostic","queryCatalog005QuestionRetainsItsRequiredCodeWithoutInventingClassification"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18031-query-catalogs-five-pt-v2/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(5,1,5,5),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==5 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':20},'METHOD':{'missed':0,'covered':10},'CLASS':{'missed':0,'covered':5},'BRANCH':{'missed':0,'covered':8}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and (v['fullSourceUnits'][n]['four100'] is True if not n.endswith('/QuestionQueryException') else v['fullSourceUnits'][n]['branchNaturallyZero'] is True) for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==5 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['nfcAndUtf8ValidationInvoked'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['pureQueryFixedExceptionCatalogOnly'] is True and v['actualAdminMutationOrAuthorization'] is v['actualProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==5 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureQueryFixedExceptionCatalogOnly',False)]:
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
    text=original.TESTS['QueryCatalogContractTest'].read_text()
    for token in ["capacity ? \"9001\" : \"9000\"","\"log query is unavailable\"","\"media query is unavailable\"","\"scenario query is unavailable\"","\"user query is unavailable\"","\"question query is unavailable\"","String[] wire = {\"9000\", \"9001\"}","assertSame(codes[index], value.resultCode())","new QuestionQueryException(null)","assertNull(value.getCause())","assertEquals(0, value.getSuppressed().length)"]:
        require(token in text,"independent literal capacity/null/catalog oracle "+token)
    require(not any(x in text for x in ["DriverManager","getConnection(","preserveFatal(","attachSecondary(","Executors.","Instant.now","UUID.randomUUID"]), "no graph/business IO")
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=5,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureQueryFixedExceptionCatalogOnly=True,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=5,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=5,newPhysicalClasses=5,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=5,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
