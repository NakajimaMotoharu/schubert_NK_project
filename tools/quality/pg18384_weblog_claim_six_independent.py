"""Independent User display/C-byte/page/null oracles; preserve and correct Unicode explanation without Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18380_weblog_claim_six_pt as original
SOURCE=original.SOURCE
POST=('PG18382-weblog-claim-six-post-v1','9db43a417108ef03b99763c892d720600b575ee85bef2266f5a2c208d2c3f6e8')
RAW='48d9c1c823c3baa5395c6568af60b51f0df1743c01d896c97552732a46861a92'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18380-weblog-claim-six-pt-v1'
OUT=data.BASE/'PG18384-weblog-claim-six-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18384-weblog-claim-six-independent-v1'
METHODS={"dev.codex.schubert.nk.web.logging.WebLogClaimValueContractTest":["wlgclaim001AllClosedValuesAndBothNumericBoundsAreRetained","wlgclaim002N12BoundsDoNotWrapOrClamp","wlgclaim003AttemptBoundsDoNotBecomeRetryPolicy","wlgclaim004WorkerIsOnlyABoundedAsciiValueNotAnOwnerProof","wlgclaim005EachRequiredBoundaryRejectsNull","wlgclaim006DiagnosticAndPayloadCopiesExposeNoLeaseOrMutableBuffer"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18380-weblog-claim-six-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(6,1,1,1),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==6 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':17},'METHOD':{'missed':0,'covered':3},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':10}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==6 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is True,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['nfcAndUtf8ValidationInvoked'] is False and v['pureWebLogClaimValueOnly'] is v['syntheticPayloadBufferOnly'] is v['publicKeyVersionLabelOnly'] is True and v['actualExternalAuthorizationOrMutation'] is v['actualBusinessProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==6 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrBusinessProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['jdkNamedTimeZoneInitializationInvoked'] is False and v['maintenanceBusinessDateMethodInvoked'] is False and v['jdkTimezoneProviderCallsAndResourceReads'] is None and v['fileEffectBoundary']=='NO_EXPLICIT_APPLICATION_FILE_API; PLATFORM_INITIALIZATION_IO_UNOBSERVED','no fabricated JDK timezone/IO absence')
        require(v['localDisplayRoleGuardInvoked'] is v['fixedOffsetJstDisplayFormattingInvoked'] is False and v['requestScopedSyntheticSearchFormBindingInvoked'] is False and v['productJstWireTimestampInvoked'] is False and v['jdkNamedTimeZoneInitializationEffectScope']=='EXPLICIT_PRODUCT_CALL_PATH_ONLY_NOT_PLATFORM_TRANSITIVE_INITIALIZATION','local display guard/fixed offset only, no invented platform absence')
        require(set(v['originalUnusedHelperProbeAudit'])==set(["dev/codex/schubert/nk/web/view/NotificationListViewModel","dev/codex/schubert/nk/web/view/NotificationDetailViewModel","dev/codex/schubert/nk/web/view/QuestionListViewModel","dev/codex/schubert/nk/web/view/QuestionDetailViewModel","dev/codex/schubert/nk/protocol/time/JstWireTimestamp"]) and all(x==dict(recordPresent=False,trueProbeHits=0) for x in v['originalUnusedHelperProbeAudit'].values()),'held N/Q helpers and named Product wire formatter absent')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',False),('publicFixedUuidFixtureOnly',False),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureWebLogClaimValueOnly',False),('syntheticPayloadBufferOnly',False),('publicKeyVersionLabelOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for key,value in [('jdkNamedTimeZoneInitializationInvoked',True),('maintenanceBusinessDateMethodInvoked',True),('jdkTimezoneProviderCallsAndResourceReads',0),('fileEffectBoundary','ALL_IO_ABSENT')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false JDK initialization disclosure')
    for key,value in [('localDisplayRoleGuardInvoked',True),('requestScopedSyntheticSearchFormBindingInvoked',True),('fixedOffsetJstDisplayFormattingInvoked',True),('jdkNamedTimeZoneInitializationEffectScope','ALL_PLATFORM_ABSENT'),('productJstWireTimestampInvoked',True),('originalUnusedHelperProbeAudit',{})]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false local display/held-family boundary')
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['testSourceHashes'][str(path)]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    text=original.TESTS['WebLogClaimValueContractTest'].read_text()
    for token in ['new long[]{1,999_999_999_999L}','new int[]{0,100}','new long[]{-1,0,1_000_000_000_000L}','new int[]{-1,101}','"web log row ID is outside N12"','"web log attempt count is outside 0..100"','"web log lease owner is invalid"','"A".repeat(64)','"A".repeat(65)','"PUBLIC/OTHER"','new ClaimedWebLog(1,null,','new ClaimedWebLog(1,identity(),null,','0,null,CREATED','0,NEXT,null,','0,NEXT,CREATED,null,','"PUBLIC",null)','"ClaimedWebLog[identity/payload/lease=<redacted>]"','expected[7]=3','input[7]=9','returned[7]=8','new UUID(0,91)','new UUID(0,92)','"PUBLIC",new byte[29]']:
        require(token in text,'independent bounded value/null/copy/redaction oracle '+token)
    require(not any(x in text for x in ['DriverManager','getConnection(','NotificationListViewModel','NotificationDetailViewModel','QuestionListViewModel','QuestionDetailViewModel','Class.forName','preserveFatal(','MockMvc','WebLogDatabaseFixture','WebLogOutboxRepository','new Thread','Executors.','MessageDigest','Cipher.']), 'no held/DB/crypto/claim/worker')
    numeric=[('id',1,True),('id',999999999999,True),('id',-1,False),('id',0,False),('id',1000000000000,False),('attempt',0,True),('attempt',100,True),('attempt',-1,False),('attempt',101,False)]
    for field,value,expected_value in numeric:
        require((1<=value<=999999999999 if field=='id' else 0<=value<=100)==expected_value,'independent numeric bounds')
    workers=[('A',True),('A'*64,True),('PUBLIC._-09',True),('',False),('A'*65,False),(' ',False),('PUBLIC/OTHER',False),('é',False),('PUBLIC\n',False)]
    require(all((re.fullmatch('[A-Za-z0-9._-]{1,64}',value) is not None)==expected_value for value,expected_value in workers),'independent worker grammar fullmatch')
    independent=dict(numericVectors=len(numeric),workerVectors=len(workers),publicFixtureOnly=True)
    for path,pin in original.PUBLIC_READS.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'unchanged pure payload helper')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=6,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureWebLogClaimValueOnly=True,independentNumericAndWorkerVectors=18,independentBoundVectors=independent,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=6,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=6,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
