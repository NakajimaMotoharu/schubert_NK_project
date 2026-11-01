"""Independent User display/C-byte/page/null oracles; preserve and correct Unicode explanation without Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18210_user_display_eight_pt as original
SOURCE=original.SOURCE
POST=('PG18212-user-display-eight-post-v1','1ae44fb4997505174d3b36cc7058b67bf5876c8929a8ac56d7f84d166c298445')
RAW='7bc53799010fd5d23a4e35c665c604407f7144f9288f76c021f4fd14cbf9cabe'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18210-user-display-eight-pt-v1'
OUT=data.BASE/'PG18214-user-display-eight-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18214-user-display-eight-independent-v1'
METHODS={"dev.codex.schubert.nk.web.view.UserDisplayContractTest":["userDisplay001EmptyListRetainsOnlyClosedDisplayAndNoNavigation","userDisplay002MiddlePageLinksUseIndependentPercentVectorAndRowsAreCopies","userDisplay003ByteOrderAndIdTieBreakAreCheckedWithoutRepair","userDisplay004SuccessRejectsDamagedPageCountFormAndEveryNullBoundary","userDisplay005InvalidFormHasNoRowsPageLinksAndRejectsNonAdminDisplay","userDisplay006DetailRetainsOnlyApprovedFieldsForStatesCountsVersionsAndSelf","userDisplay007DetailRejectsEachRoleTargetAndSessionCountMismatch","userDisplay008NullAndUnrepresentableDateNeverPublishARepairedDisplay"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18210-user-display-eight-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(8,1,2,3),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==8 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':113},'METHOD':{'missed':0,'covered':34},'CLASS':{'missed':0,'covered':3},'BRANCH':{'missed':0,'covered':36}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==8 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['nfcAndUtf8ValidationInvoked'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is True and v['pureUserDisplayValuesOnly'] is True and v['actualExternalAuthorizationOrMutation'] is v['actualBusinessProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==8 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrBusinessProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['jdkNamedTimeZoneInitializationInvoked'] is False and v['maintenanceBusinessDateMethodInvoked'] is False and v['jdkTimezoneProviderCallsAndResourceReads'] is None and v['fileEffectBoundary']=='NO_EXPLICIT_APPLICATION_FILE_API; PLATFORM_INITIALIZATION_IO_UNOBSERVED','no fabricated JDK timezone/IO absence')
        require(v['localDisplayRoleGuardInvoked'] is v['requestScopedSyntheticSearchFormBindingInvoked'] is v['fixedOffsetJstDisplayFormattingInvoked'] is True and v['productJstWireTimestampInvoked'] is False and v['jdkNamedTimeZoneInitializationEffectScope']=='EXPLICIT_PRODUCT_CALL_PATH_ONLY_NOT_PLATFORM_TRANSITIVE_INITIALIZATION','local display guard/fixed offset only, no invented platform absence')
        require(set(v['originalUnusedHelperProbeAudit'])==set(["dev/codex/schubert/nk/web/view/NotificationListViewModel","dev/codex/schubert/nk/web/view/NotificationDetailViewModel","dev/codex/schubert/nk/web/view/QuestionListViewModel","dev/codex/schubert/nk/web/view/QuestionDetailViewModel","dev/codex/schubert/nk/protocol/time/JstWireTimestamp"]) and all(x==dict(recordPresent=False,trueProbeHits=0) for x in v['originalUnusedHelperProbeAudit'].values()),'held N/Q helpers and named Product wire formatter absent')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureUserDisplayValuesOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for key,value in [('jdkNamedTimeZoneInitializationInvoked',True),('maintenanceBusinessDateMethodInvoked',True),('jdkTimezoneProviderCallsAndResourceReads',0),('fileEffectBoundary','ALL_IO_ABSENT')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false JDK initialization disclosure')
    for key,value in [('localDisplayRoleGuardInvoked',False),('requestScopedSyntheticSearchFormBindingInvoked',False),('fixedOffsetJstDisplayFormattingInvoked',False),('jdkNamedTimeZoneInitializationEffectScope','ALL_PLATFORM_ABSENT'),('productJstWireTimestampInvoked',True),('originalUnusedHelperProbeAudit',{})]:
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
    text=original.TESTS['UserDisplayContractTest'].read_text()
    for token in ["new PagedResponseData(1, 50, 0, 1, 0, 0)","new PagedResponseData(2, 50, 101, 3, 51, 100)","A%20%2B%26%E3%81%82&role=ADMIN&state=LOCKED&page=1","A%20%2B%26%E3%81%82&role=ADMIN&state=LOCKED&page=3","\"A +&あ000051\"","\"A +&あ000100\"","caller.clear()","assertEquals(50, page.getRows().size())","\"UserListRow[REDACTED]\"","\"2026-11-01 09:01:00.123\"","\"2026-11-01 08:59:59.123\"","\"2026-11-01 09:00:01.123\"","form(\"999\")","\"duplicate user identity\"","\"invalid user display order\"","\"invalid successful user form\"","\"user response page does not match request\"","\"inconsistent user record count\"","Arrays.asList((UserRecord) null)","\"user display requires administrator\"","List.of(UserRole.USER, UserRole.ADMIN)","List.of(UserState.ACTIVE, UserState.DISABLED, UserState.LOCKED)","new int[] {0, 1, 2}","new long[] {0, 999_999_999L}","\"public_display\" : \"OTHER\"","\"ログイン失敗によるロック\"","Map.entry(\"role\", role == UserRole.ADMIN ? \"ADMIN\" : \"USER\")","Map.entry(\"activeSessionCount\", count)","Map.entry(\"version\", version)","\"UserDetailViewModel[REDACTED]\"","\"invalid user detail projection\"","new int[] {3, 999}","assertThrows(DateTimeException.class","Instant.MAX"]:
        require(token in text,'independent UI/SS/C-byte/page/null/field oracle '+token)
    require(not any(x in text for x in ['DriverManager','getConnection(','NotificationListViewModel','NotificationDetailViewModel','QuestionListViewModel','QuestionDetailViewModel','Class.forName','preserveFatal(','MockMvc','WebLogDatabaseFixture']), 'no held family/DB/authority installation')
    before=data.read_checked(data.BASE/'PG18211-user-display-oracle-basis-before-v1/manifest.json','b5d775a90b75ee543c6c6bf68eb8046f25a4ad72dae05378584f101f3cf146ce')
    require(before['actualExit'] is None and before['status']=='ORACLE_BASIS_UNQUALIFIED_BEFORE_CORRECTION' and before['originalProductTestExit']==0 and before['originalProductFailures']==0,'doc error is not product failure')
    require(data.sha((data.BASE/'PG18211-user-display-oracle-basis-before-v1/3472-before.md').read_bytes())==before['originalSpecificationSha256']=='a443d04136a1c58d4e1c5bb79fdc3836e33445a661c8769ba54b7cd4ed22feb8','exact old incorrect basis preserved')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/3472_User表示二Source独立単体テスト仕様.md'
    require(data.sha(spec.read_bytes())=='e15ca367ce07647acc8675867170e15225a8d3917db7a3963018fad842d9cbb6','corrected independent spec')
    literal=dict(e000Utf8='ee8080',u10000Utf8='f0908080',e000Utf16='e000',u10000Utf16='d800dc00',ascending=['E000','10000'])
    computed=dict(e000Utf8='\ue000'.encode('utf-8').hex(),u10000Utf8='\U00010000'.encode('utf-8').hex(),e000Utf16='\ue000'.encode('utf-16-be').hex(),u10000Utf16='\U00010000'.encode('utf-16-be').hex(),ascending=['E000','10000'])
    def unicode_contract(v):
        require(v==computed==literal and bytes.fromhex(v['e000Utf8'])<bytes.fromhex(v['u10000Utf8']) and bytes.fromhex(v['e000Utf16'])>bytes.fromhex(v['u10000Utf16']),'independent UTF8 differs from UTF16 order')
    unicode_contract(literal);unicode_negative=[]
    for key,value in [('e000Utf8','ef8080'),('ascending',['10000','E000'])]:
        bad=copy.deepcopy(literal);bad[key]=value
        try:unicode_contract(bad)
        except ValueError:unicode_negative.append(key)
        else:raise ValueError('false Unicode basis accepted')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=8,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureUserDisplayValuesOnly=True,independentUnicodeBasis=literal,independentUnicodeBasisVectors=4,independentUnicodeBasisNegativeVectors=len(unicode_negative),independentUnicodeBasisNegativeLabels=unicode_negative,correctedSpecificationSha256='e15ca367ce07647acc8675867170e15225a8d3917db7a3963018fad842d9cbb6',oldSpecificationSha256=before['originalSpecificationSha256'],junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=8,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=2,newPhysicalClasses=3,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=8,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
