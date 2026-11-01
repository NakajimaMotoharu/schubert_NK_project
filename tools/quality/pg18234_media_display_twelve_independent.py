"""Independent media projection/stored-pair/URL/null and six fixed Current-title oracles."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18230_media_display_twelve_pt as original
SOURCE=original.SOURCE
POST=('PG18232-media-display-twelve-post-v1','e492146f19bfaeb173f9680f96d041fa2e6ad7df57659f29f6b70aa50ab49832')
RAW='849dd6e2f213158bda3df193489f75b604b27328ed12f437de6bd05f83e9f140'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18230-media-display-twelve-pt-v1'
OUT=data.BASE/'PG18234-media-display-twelve-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18234-media-display-twelve-independent-v1'
METHODS={"dev.codex.schubert.nk.web.view.MediaDisplayContractTest":["mediaDisplay001VideoCategoryNavigationAndPublicFieldsAreExactlyBounded","mediaDisplay002VideoMissingAndDotIdsAndNullsRejectWithoutOpeningDescriptor","mediaDisplay003EmptyBackgroundMusicHasNoPairsAndOnlyClosedOutput","mediaDisplay004MaximumTwoHundredRowsAreIndependentImmutableTrackSnapshots","mediaDisplay005StoredMainAndInstrumentalRolesWinInEitherArrivalOrder","mediaDisplay006NoneAndMissingStoredSidesNeverInferMatchesFromTitles","mediaDisplay007CurrentTitleRuleUsesIndependentLiteralVectorsNotFilesystemMatching","mediaDisplay008OversizeAndDeclaredCountMismatchAreRejected","mediaDisplay009EachRecordBindingIdentitySizeAndOrderFailureIsRejected","mediaDisplay010PairedRolesRequireStoredKeyAndRejectDuplicateSlots","mediaDisplay011LinkSegmentsRejectEmptyAndDotAndEncodeReservedBytes","mediaDisplay012RequiredActorCategorySectionDataCollectionAndElementsRejectNull"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18230-media-display-twelve-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(12,1,2,3),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==12 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':89},'METHOD':{'missed':0,'covered':11},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':0,'covered':41}},'complete partial counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and v['fullSourceUnits'][n]['four100'] is True for n in original.MAIN_UNITS),'one whole partial closure')
        require(v['strictFour100GateExit']==0 and v['targetUnitFour100'] is True and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==12 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is False,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['syntheticOwnedReceiptJdbcFaultPortsOnly'] is v['syntheticJdbcPortsOnly'] is v['syntheticJdbcApiCallsInvoked'] is v['syntheticJdbcPrepareBindUpdateCloseInvoked'] is False and v['memoryServletHeaderFixtureOnly'] is v['directNumericIpLiteralParsingInvoked'] is False and v['memorySessionPrincipalValueOnly'] is v['nfcAndUtf8ValidationInvoked'] is v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is True and v['pureMediaDisplayValuesOnly'] is True and v['actualAdminMutationOrAuthorization'] is v['actualBusinessProviderInvoked'] is v['actualThrowableGraphTraversal'] is False and v['normalOrdinaryTestSourceDomain'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==12 and v['actualAuthenticationOrSessionIssued'] is False and v['explicitDnsLookupInvoked'] is False and v['platformJdkInitializationEffects'] is None,'owned JDBC proxy calls only')
        require(v['syntheticDescriptorMetadataOnly'] is v['storedMusicPairMetadataOnly'] is v['stubDescriptorContentHashNotVerified'] is True and v['actualFileContentOrHashValidated'] is False,'stub descriptor is not real hash verification')
        require(v['currentIndependentOracleSourceReference']==dict(path=str(original.CURRENT_MUSIC_SOURCE),sha256=original.CURRENT_MUSIC_SHA,readOnly=True,copiedToGit=False,executed=False),'Current readonly reference, never oracle execution')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrBusinessProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['jdkNamedTimeZoneInitializationInvoked'] is False and v['businessDateConversionInvoked'] is False and v['jdkTimezoneProviderCallsAndResourceReads'] is None and v['fileEffectBoundary']=='NO_EXPLICIT_APPLICATION_FILE_API; PLATFORM_INITIALIZATION_IO_UNOBSERVED','no fabricated JDK timezone/IO absence')
        filtered='dev/codex/schubert/nk/web/view/AnimationWatchViewModel$1'
        require(v['officialFilteredSyntheticClasses']==[filtered] and set(v['officialFilteredClassProof'])=={filtered},'exact generated-filter denominator, not NoCode')
        proof=v['officialFilteredClassProof'][filtered]
        require(proof['flags']&4096 and proof['sourceFile']=='AnimationWatchViewModel.java' and proof['methods'] and all(x['hasCode'] and x['name']=='<clinit>' for x in proof['methods']) and proof['notNoCode'] is proof['allJaCoCoCountersZero'] is True and proof['filterBasis']=='UNCHANGED_OFFICIAL_SYNTHETIC_CLASS_FILTER','official fully filtered Code remains physical and Code-bearing')
        require(v['reusedCompletedPassiveStages']=={} and v['failedPriorPostPreserved'] is False,'reuse genuine completed stages, preserve failed prior')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',1),('targetUnitFour100',False),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureMediaDisplayValuesOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for key,value in [('jdkNamedTimeZoneInitializationInvoked',True),('businessDateConversionInvoked',True),('jdkTimezoneProviderCallsAndResourceReads',0),('fileEffectBoundary','ALL_IO_ABSENT')]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false JDK initialization disclosure')
    filtered='dev/codex/schubert/nk/web/view/AnimationWatchViewModel$1'
    for label in ['synthetic','Code','counter','inventory']:
        bad=copy.deepcopy(p)
        proof=bad['officialFilteredClassProof'][filtered]
        if label=='synthetic':proof['flags'] &= ~4096
        if label=='Code':proof['methods'][0]['hasCode']=False
        if label=='counter':proof['allJaCoCoCountersZero']=False
        if label=='inventory':bad['officialFilteredSyntheticClasses']=[]
        try:contract(bad)
        except ValueError:labels.append('official-filter-'+label)
        else:raise ValueError('false filtered proof accepted')
    for key,value in [('stubDescriptorContentHashNotVerified',False),('actualFileContentOrHashValidated',True),('storedMusicPairMetadataOnly',False),('currentIndependentOracleSourceReference',{})]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false media effect accepted')
    require(data.sha(original.CURRENT_MUSIC_SOURCE.read_bytes())==original.CURRENT_MUSIC_SHA,'unchanged Current read-only oracle reference')
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['testSourceHashes'][str(path)]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    text=original.TESTS['MediaDisplayContractTest'].read_text()
    for token in ["VideoCategory.MAIN, List.of(\"メインパート\", \"/animation/main\", \"メインパート一覧\")","VideoCategory.SUBTRACK, List.of(\"メインパート\", \"/animation/main\", \"メインパート一覧\")","VideoCategory.OVA, List.of(\"OVA\", \"/animation/ova\", \"OVA一覧\")","VideoCategory.OPENING, List.of(\"オープニング\", \"/animation\", \"アニメ視聴\")","\"/animation/media/public%2Fid%3F%E3%81%82\"","assertEquals(200, tracks.size())","assertEquals(1, list(values, \"pairs\").size())","assertEquals(\"MAIN\", pair.get(\"title\"))","assertEquals(2, list(none, \"pairs\").size())","assertTrue(slot(onlyInst, \"main\").isEmpty())","String[] expected = {\"PUBLIC SONG\", \"PUBLIC SONG\", \"PUBLIC SONG\", \"PUBLIC SONG\", \"さくら\", \"PUBLIC SONG\"}","new MusicTrackResponseData(201)","\"invalid bound music track\"","\"duplicate music pair role\"","\"/music/download/public%2Fid%3F%E3%81%82\"","Arrays.asList((MusicTrackRecord) null)","() -> tracks.clear()"]:
        require(token in text,'independent literal UI/pair/boundary/URL/null oracle '+token)
    require(not any(x in text for x in ['DriverManager','getConnection(','preserveFatal(','attachSecondary(','Executors.','Instant.now','UUID.randomUUID','MockMvc','WebLogDatabaseFixture']), 'no held fixture/actual HTTP/DB')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=12,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureMediaDisplayValuesOnly=True,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=12,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=2,newPhysicalClasses=3,officialFilteredSyntheticCodePhysicalClasses=1,metadataPhysicalClasses=0,partialSourcePrograms=0,newUniqueMethods=12,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
