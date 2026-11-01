"""Independent User display/C-byte/page/null oracles; preserve and correct Unicode explanation without Product replay."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18340_user_search_form_twelve_pt as original
SOURCE=original.SOURCE
POST=('PG18342-user-search-form-twelve-post-v1','b2e58e47102d412d28a1a1fc3ef7bf07fe1edca3ca94ff49a0c152563c38a594')
RAW='df3fbed9e58662eebdcbd2cc93634879d168b081fbd78dfe9210797a4a329d8b'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18340-user-search-form-twelve-pt-v1'
OUT=data.BASE/'PG18344-user-search-form-twelve-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18344-user-search-form-twelve-independent-v1'
METHODS={"dev.codex.schubert.nk.web.form.UserSearchInputContractTest":["usrform001DefaultsDoNotConferAuthentication","usrform002RoleAndStateLiteralsAreIndependentOptionalEnums","usrform003NormalizationPrecedesByteValidationAndOuterTrim","usrform004Utf8BoundariesUseIndependentOneTwoAndFourByteWidths","usrform005PageClampAndUpperBoundHaveLiteralExpectations","usrform006MalformedUpperAndOverflowPageNeverBecomeARequest","usrform007UnknownAndNonSingleFieldsHaveExplicitIssueKeys","usrform008ControlAndSurrogateRejectionIsNotUnicodeRejection","usrform009UnknownEnumsAreFieldFailuresWithoutGrant","usrform010NullAtEveryCollectionBoundaryIsRejected","usrform011CallerMutationCannotAlterTheCapturedRequest","usrform012InvalidConversionAndDiagnosticsStayValueFree"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18340-user-search-form-twelve-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(12,1,1,1),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==12 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':54},'METHOD':{'missed':0,'covered':13},'CLASS':{'missed':0,'covered':1},'BRANCH':{'missed':0,'covered':34}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==12 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is False and v['nfcAndUtf8ValidationInvoked'] is v['pureUserSearchFormOnly'] is True and v['actualExternalAuthorizationOrMutation'] is v['actualBusinessProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==12 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrBusinessProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['jdkNamedTimeZoneInitializationInvoked'] is False and v['maintenanceBusinessDateMethodInvoked'] is False and v['jdkTimezoneProviderCallsAndResourceReads'] is None and v['fileEffectBoundary']=='NO_EXPLICIT_APPLICATION_FILE_API; PLATFORM_INITIALIZATION_IO_UNOBSERVED','no fabricated JDK timezone/IO absence')
        require(v['localDisplayRoleGuardInvoked'] is v['fixedOffsetJstDisplayFormattingInvoked'] is False and v['requestScopedSyntheticSearchFormBindingInvoked'] is True and v['productJstWireTimestampInvoked'] is False and v['jdkNamedTimeZoneInitializationEffectScope']=='EXPLICIT_PRODUCT_CALL_PATH_ONLY_NOT_PLATFORM_TRANSITIVE_INITIALIZATION','local display guard/fixed offset only, no invented platform absence')
        require(set(v['originalUnusedHelperProbeAudit'])==set(["dev/codex/schubert/nk/web/view/NotificationListViewModel","dev/codex/schubert/nk/web/view/NotificationDetailViewModel","dev/codex/schubert/nk/web/view/QuestionListViewModel","dev/codex/schubert/nk/web/view/QuestionDetailViewModel","dev/codex/schubert/nk/protocol/time/JstWireTimestamp"]) and all(x==dict(recordPresent=False,trueProbeHits=0) for x in v['originalUnusedHelperProbeAudit'].values()),'held N/Q helpers and named Product wire formatter absent')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureUserSearchFormOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for key,value in [('jdkNamedTimeZoneInitializationInvoked',True),('maintenanceBusinessDateMethodInvoked',True),('jdkTimezoneProviderCallsAndResourceReads',0),('fileEffectBoundary','ALL_IO_ABSENT')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false JDK initialization disclosure')
    for key,value in [('localDisplayRoleGuardInvoked',True),('requestScopedSyntheticSearchFormBindingInvoked',False),('fixedOffsetJstDisplayFormattingInvoked',True),('jdkNamedTimeZoneInitializationEffectScope','ALL_PLATFORM_ABSENT'),('productJstWireTimestampInvoked',True),('originalUnusedHelperProbeAudit',{})]:
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
    text=original.TESTS['UserSearchInputContractTest'].read_text()
    for token in ['Optional.empty()', 'assertEquals(50,dto.pageSize())', 'String[] roles={"","USER","ADMIN"}', 'String[] states={"","ACTIVE","DISABLED","LOCKED"}', '"e\\u0301".repeat(32)', '"é".repeat(32)', '"x".repeat(65)', '"\\uD800\\uDC00".repeat(17)', 'int[] expected={1,1,1,1,1,1,2,999999,2}', '"2147483648"', '"-2147483649"', 'List.<String>of()', '"\\u0085"', '"\\uD800"', '"\\uDC00"', 'UserSearchForm.bind(null)', 'key.put(null,List.of("PUBLIC"))', 'list.put("username",null)', 'elements.add(null)', 'values.set(0,"CHANGED")', 'input.clear()', 'UnsupportedOperationException.class', '"invalid user search form"', '"UserSearchForm[REDACTED]"']:
        require(token in text,'independent SS input/normalization/byte/page/null oracle '+token)
    require(not any(x in text for x in ['DriverManager','getConnection(','NotificationListViewModel','NotificationDetailViewModel','QuestionListViewModel','QuestionDetailViewModel','Class.forName','preserveFatal(','MockMvc','WebLogDatabaseFixture','UserAdminControllerTest','EncryptedWebSessionRepository','new Thread','Executors.']), 'no held/DB/authority fixture or worker')
    import unicodedata
    vectors=[('ascii63','x'*63,63),('ascii64','x'*64,64),('ascii65','x'*65,65),('two64','é'*32,64),('two66','é'*33,66),('four64','\U00010000'*16,64),('four68','\U00010000'*17,68)]
    independent=[dict(id=n,expectedUtf8Bytes=width,actualUtf8Bytes=len(value.encode('utf-8'))) for n,value,width in vectors]
    require(all(v['expectedUtf8Bytes']==v['actualUtf8Bytes'] for v in independent),'independent Python standard-codec widths')
    require(unicodedata.normalize('NFC','e\u0301'*32)=='é'*32,'independent normalization fixed literal, not Production')
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
    require(len(crc)==1 and {r[1] for r in crc}==set(names) and not any(v.startswith('METADATA'+chr(9)) for v in lines),'two original Code Test classes only')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=12,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureUserSearchFormOnly=True,independentByteAndNormalizationVectors=8,independentByteVectors=independent,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=12,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=12,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
