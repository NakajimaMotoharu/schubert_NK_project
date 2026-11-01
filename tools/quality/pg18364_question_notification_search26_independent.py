"""Independent User display/C-byte/page/null oracles; preserve and correct Unicode explanation without Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18360_question_notification_search26_pt as original
SOURCE=original.SOURCE
POST=('PG18362-question-notification-search26-post-v1','37517334dc95f2fa471bd820d6e24a3f497c4a8b6b55f63626684e9afcfff1ce')
RAW='6aa3a82b4c677591d963e0a170e64f3aa433242bc7549550649eae5d52ceb038'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18360-question-notification-search26-pt-v1'
OUT=data.BASE/'PG18364-question-notification-search26-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18364-question-notification-search26-independent-v1'
METHODS={"dev.codex.schubert.nk.web.form.QuestionSearchInputContractTest":["qsform001EmptyInputsHaveClosedRoleSpecificDefaults","qsform002UserCannotSupplyEvenEmptyUsernameButAdminCanFilter","qsform003NfcAndIndependentByteWidthsRespectBothLimits","qsform004StatesMapOnlyTheThreeFixedEnums","qsform005ValidPageValuesHaveIndependentLiteralResults","qsform006InvalidAndOverflowPagesCannotConvert","qsform007JstDatesUseFixedUtcGoldensWithMissingSides","qsform008InclusiveEndOfDayDefinesThe366DayAndReverseBounds","qsform009StrictDatesRejectYearZeroFormatAndImpossibleDays","qsform010UnknownAndNonSingleParametersKeepExplicitFailures","qsform011ControlAndSurrogateValidationIsBeforeNormalization","qsform012NullBoundariesDoNotCreatePartialForms","qsform013CopiesAndRoleSnapshotsCannotBeMutatedByCallers","qsform014InvalidConversionAndDiagnosticsDoNotRetainInput"],"dev.codex.schubert.nk.web.form.NotificationSearchInputContractTest":["ntform001DefaultsHaveNoOwnerOrDates","ntform002OnlyThreeNotificationTypesBecomeEnums","ntform003PageClampAndUpperBoundaryHaveLiteralResults","ntform004InvalidAndOverflowPagesRemainFailures","ntform005IndependentJstUtcPairsAndMissingSides","ntform006SameDayAnd366DayMinusMillisecondAreAllowedNotTheNextDay","ntform007StrictDatesRejectInvalidYearFormatAndCalendar","ntform008UnknownOwnerAndNonSingleParametersAreNeverIgnored","ntform009ControlAndSurrogateChecksPrecedeTrimWhileSpacesRemainOptional","ntform010NullMapKeyListAndElementNeverCreateAForm","ntform011SnapshotsAndIssueMapsAreImmutableCopies","ntform012ConversionFailureAndDiagnosticRemainValueFree"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18360-question-notification-search26-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(26,2,2,2),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==26 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':150},'METHOD':{'missed':0,'covered':25},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':0,'covered':104}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==26 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['nfcAndUtf8ValidationInvoked'] is v['pureQuestionNotificationSearchFormsOnly'] is True and v['localSearchRoleGuardInvoked'] is True and v['actualExternalAuthorizationOrMutation'] is v['actualBusinessProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==26 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrBusinessProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['jdkNamedTimeZoneInitializationInvoked'] is False and v['maintenanceBusinessDateMethodInvoked'] is False and v['jdkTimezoneProviderCallsAndResourceReads'] is None and v['fileEffectBoundary']=='NO_EXPLICIT_APPLICATION_FILE_API; PLATFORM_INITIALIZATION_IO_UNOBSERVED','no fabricated JDK timezone/IO absence')
        require(v['localDisplayRoleGuardInvoked'] is False and v['fixedOffsetJstDisplayFormattingInvoked'] is True and v['requestScopedSyntheticSearchFormBindingInvoked'] is True and v['productJstWireTimestampInvoked'] is False and v['jdkNamedTimeZoneInitializationEffectScope']=='EXPLICIT_PRODUCT_CALL_PATH_ONLY_NOT_PLATFORM_TRANSITIVE_INITIALIZATION','local display guard/fixed offset only, no invented platform absence')
        require(set(v['originalUnusedHelperProbeAudit'])==set(["dev/codex/schubert/nk/web/view/NotificationListViewModel","dev/codex/schubert/nk/web/view/NotificationDetailViewModel","dev/codex/schubert/nk/web/view/QuestionListViewModel","dev/codex/schubert/nk/web/view/QuestionDetailViewModel","dev/codex/schubert/nk/protocol/time/JstWireTimestamp"]) and all(x==dict(recordPresent=False,trueProbeHits=0) for x in v['originalUnusedHelperProbeAudit'].values()),'held N/Q helpers and named Product wire formatter absent')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureQuestionNotificationSearchFormsOnly',False),('localSearchRoleGuardInvoked',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for key,value in [('jdkNamedTimeZoneInitializationInvoked',True),('maintenanceBusinessDateMethodInvoked',True),('jdkTimezoneProviderCallsAndResourceReads',0),('fileEffectBoundary','ALL_IO_ABSENT')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false JDK initialization disclosure')
    for key,value in [('localDisplayRoleGuardInvoked',True),('requestScopedSyntheticSearchFormBindingInvoked',False),('fixedOffsetJstDisplayFormattingInvoked',False),('jdkNamedTimeZoneInitializationEffectScope','ALL_PLATFORM_ABSENT'),('productJstWireTimestampInvoked',True),('originalUnusedHelperProbeAudit',{})]:
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
    texts={name:original.TESTS[name].read_text() for name in original.COUNTS}
    qtext=texts['QuestionSearchInputContractTest'];ntext=texts['NotificationSearchInputContractTest']
    common=['"0000-01-01"','"2025-02-29"','"2024-13-01"','"2024-01-32"','"2024-2-29"','"2024-02-29T00:00"','"2024-02-28T15:00:00Z"','"2024-02-29T14:59:59.999Z"','"2023-12-31T15:00:00Z"','"2024-12-31T14:59:59.999Z"','"2025-01-01"','"2024-01-02"','"2024-01-01"','"2147483648"','"-2147483649"','List.<String>of()','"\\u0085"','"\\uD800"','"\\uDC00"','UnsupportedOperationException.class','assertEquals(50,']
    for text in texts.values():
        for token in common:require(token in text,'independent date/page/null/copy literal '+token)
        require(not any(x in text for x in ['DriverManager','getConnection(','NotificationListViewModel','NotificationDetailViewModel','QuestionListViewModel','QuestionDetailViewModel','Class.forName','preserveFatal(','MockMvc','WebLogDatabaseFixture','UserAdminControllerTest','EncryptedWebSessionRepository','new Thread','Executors.']), 'no held/DB/view/worker')
    for token in ['UserRole.USER','UserRole.ADMIN','one("username",value)','assertEquals("",user.getValues().get("username"))','"x".repeat(256)','"x".repeat(257)','"é".repeat(128)','"é".repeat(129)','"e\\u0301".repeat(128)','"\\uD800\\uDC00".repeat(65)','QuestionSearchForm.bind(null,UserRole.ADMIN)','QuestionSearchForm.bind(Map.of(),null)','"QuestionSearchForm[REDACTED]"','"invalid question search form"']:
        require(token in qtext,'question SS literal '+token)
    for token in ['NotificationType.ACCEPTED','NotificationType.COMPLETED','NotificationType.ERROR','NotificationSearchForm.bind(null)','one("owner","PUBLIC")','"NotificationSearchForm[REDACTED]"','"invalid notification search form"']:
        require(token in ntext,'notification SS literal '+token)
    import unicodedata
    from datetime import datetime,timezone,timedelta
    vectors=[('keyword256','x'*256,256),('keyword257','x'*257,257),('keywordTwo256','é'*128,256),('keywordTwo258','é'*129,258),('username64','x'*64,64),('username65','x'*65,65)]
    independent=[dict(id=n,expectedUtf8Bytes=w,actualUtf8Bytes=len(value.encode('utf-8'))) for n,value,w in vectors]
    require(all(v['expectedUtf8Bytes']==v['actualUtf8Bytes'] for v in independent) and unicodedata.normalize('NFC','e\u0301'*128)=='é'*128,'independent codec/NFC')
    jst=timezone(timedelta(hours=9))
    inputs=[(2024,2,29,0,0,0,0),(2024,2,29,23,59,59,999000),(2024,1,1,0,0,0,0),(2024,12,31,23,59,59,999000),(2025,1,1,23,59,59,999000)]
    golden=['2024-02-28T15:00:00.000Z','2024-02-29T14:59:59.999Z','2023-12-31T15:00:00.000Z','2024-12-31T14:59:59.999Z','2025-01-01T14:59:59.999Z']
    instants=[datetime(*v,tzinfo=jst).astimezone(timezone.utc) for v in inputs]
    actual=[v.isoformat(timespec='milliseconds').replace('+00:00','Z') for v in instants]
    require(actual==golden,'independent fixed-offset JST UTC goldens')
    ranges=[(instants[3]-instants[2],timedelta(days=366,milliseconds=-1)),(instants[4]-instants[2],timedelta(days=367,milliseconds=-1)),(datetime(2024,1,1,23,59,59,999000,tzinfo=jst)-datetime(2024,1,2,tzinfo=jst),timedelta(milliseconds=-1))]
    require(all(a==b for a,b in ranges),'366-day and reverse millisecond boundaries')
    for path,pin in original.PUBLIC_READS.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'typed helper reference unchanged')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=26,suites=2,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureQuestionNotificationSearchFormsOnly=True,localSearchRoleGuardInvoked=True,independentByteAndNormalizationVectors=7,independentJstDateVectors=5,independentDateRangeVectors=3,independentUtcGoldens=golden,independentByteVectors=independent,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=26,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=2,newPhysicalClasses=2,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=26,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
