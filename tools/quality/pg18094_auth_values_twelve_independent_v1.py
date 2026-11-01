"""Independent SS314 pure auth values/catalogs with NoCode interface and literal oracles, no session issuance."""
import copy
import os
from pathlib import Path
import re
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
import pg18090_auth_values_twelve_pt as original
SOURCE=original.SOURCE
POST=('PG18092-auth-values-twelve-post-v1','60181f567c9bda57f67b07a482bc3064aa4f5d4562fea2065a7d1e05f21e3576')
RAW='f55a5c6f9f5d54619d17f7379923a8554d830396939f2ae61b3a831a78b3cac4'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg18090-auth-values-twelve-pt-v1'
OUT=data.BASE/'PG18094-auth-values-twelve-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18094-auth-values-twelve-independent-v1'
METHODS={"dev.codex.schubert.nk.api.security.AuthImmutableValueContractTest":["authValue001AccountRetainsOnlyItsSuppliedImmutableValuesAndRedactsAllFields","authValue002AccountRejectsNullUtf8LengthAndWrongAttemptKind","authValue003IssuedValueRetainsExactReferencesAndNeverExposesPublicFixtureText","authValue004IssuedValueRejectsEveryNullAndNonIncreasingExpiry","authValue005RevokedValueHasOnlySuccessAndIdempotentShapes","authValue006RevokedValueRejectsNullAndEveryOtherClosedResultCode","authValue007LockedAttemptRetainsSnapshotAndOnlyCanonicalNumericIp","authValue008LockedAttemptRejectsNullWrongKindScopeAndNonLiteral","authValue009LoginSuccessRetainsSameOwnerAndUsesOnlyFixedSuccessProfile","authValue010LoginFailureHasClosedCodesAndExactRetryBounds","authValue011RolesAndInternalReasonsHaveOnlyLiteralClosedNamesAndOrder","authValue012InvalidContextExceptionHasOnlyItsFixedCatalog"]}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1]);raw=data.read_checked(data.BASE/'PG18090-auth-values-twelve-pt-v1/manifest.json',RAW)
    expected={(c,n) for c,ns in METHODS.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW,'exact source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],len(v['physicalClasses']))==(12,1,9,11),'one complete Source denominator')
        require(set(v['metadataClasses'])==original.METADATA and v['unexecutedCodeClasses']==[],'Factory NoCode, all Main Code denominators')
        require(len(v['cases'])==12 and {(x['classname'],x['name']) for x in v['cases']}==expected and all(x['result']=='PASS' for x in v['cases']),'whole original11 only')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['execSha256']==raw['execSha256'] and v['sessionIdentity']==original.SESSION,'one session/CRC')
        require(v['totals']=={'LINE':{'missed':0,'covered':79},'METHOD':{'missed':0,'covered':18},'CLASS':{'missed':0,'covered':10},'BRANCH':{'missed':0,'covered':30}},'all nine Source/eleven physical counters')
        require(set(v['fullSourceUnits'])==set(original.MAIN_UNITS) and all(set(v['fullSourceUnits'][n]['physical'])==set(original.CLOSURES[n]) and v['fullSourceUnits'][n]['threeCounter100'] is True and (v['fullSourceUnits'][n]['four100'] is True if n.rsplit('/',1)[1] in {'LoginAccount','IssuedContext','RevokedContext','LockedLoginAttempt','LoginResult'} else v['fullSourceUnits'][n]['branchNaturallyZero'] is True) for n in original.MAIN_UNITS),'whole closures, strict and natural categories')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False and v['allMeasuredApplicableCountersCovered'] is True and v['naturalZeroBranch'] is False and v['newTestIds']==12 and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'no exclusions')
        require(v['publicSyntheticUuidFixture'] is v['publicFixedUuidFixtureOnly'] is True,'no active UUID fixture')
        require(set(v['physicalClasses'])=={n for ns in original.CLOSURES.values() for n in ns},'exact physical identity set')
        require(v['pureAuthImmutableValuesAndCatalogOnly'] is True and v['publicSyntheticAuthenticationContextValueOnly'] is v['syntheticAuthenticationContextValueUsed'] is v['directNumericIpLiteralParsingInvoked'] is True and v['actualAdminMutationOrAuthorization'] is v['actualProviderInvoked'] is v['actualThrowableGraphTraversal'] is v['normalOrdinaryTestSourceDomain'] is v['actualAuthenticationOrSessionIssued'] is v['explicitDnsLookupInvoked'] is False and v['normalOrdinaryMethodCount']==0 and v['independentQualityMethodCount']==12 and v['platformJdkInitializationEffects'] is None,'public synthetic DTO values and numeric literals only')
        require(v['actualNetworkActions']==0,'actual self-owned network, operation count unknown not zero')
        require(v['testOwnJavaMonotonicClockRead'] is v['ownCurrentThreadInterruptFlagModifiedAndFinallyCleared'] is False and v['ownThreadCount']==0 and v['cryptoOrKeyOperationsInvoked'] is v['actualNativeHookOrProviderOperation'] is False,'owned JDK clock/interrupt, no invented thread total/native')
        require(v['forbiddenProductProbeHits']==0 and all(not x['recordPresent'] for k in ['rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit'] for x in v[k].values()),'held/Root/native absent')
        require(v['actualFilesOpenedByProduct'] is v['actualJdbcBackendConnected'] is False and v['actualBackendSqlOperations']==v['actualVmActions']==0,'no real DB/file/VM')
        require(v['productTestsReexecutedByPost']==0 and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no formal/replay transfer')
        require(v['sourcePhysicalInventory']['dev/codex/schubert/nk/api/security/LoginResult']['flags']==1537 and all(m['hasCode'] is False for m in v['sourcePhysicalInventory']['dev/codex/schubert/nk/api/security/LoginResult']['methods']),'exact interface methods have no Code')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('tests',0),('suites',0),('targetSourceUnits',0),('physicalClasses',{}),('metadataClasses',['unknown']),('unexecutedCodeClasses',['unknown']),('cases',[]),('singleSession',False),('crcMismatch',1),('totals',{}),('fullSourceUnits',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('manualCounterExclusions',['x']),('actualNetworkActions',1),('testOwnJavaMonotonicClockRead',True),('ownCurrentThreadInterruptFlagModifiedAndFinallyCleared',True),('ownThreadCount',1),('cryptoOrKeyOperationsInvoked',True),('forbiddenProductProbeHits',1),('actualFilesOpenedByProduct',True),('actualJdbcBackendConnected',True),('oldCoverageTransferred',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('publicSyntheticUuidFixture',False),('publicFixedUuidFixtureOnly',False),('physicalClasses',{**{k:v for k,v in p['physicalClasses'].items() if k!=next(iter(p['physicalClasses']))},'unknown':'0'*64}),('pureAuthImmutableValuesAndCatalogOnly',False)]:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false current post '+key)
    for label,change in [('metadata-interface-code',lambda v:v['sourcePhysicalInventory']['dev/codex/schubert/nk/api/security/LoginResult']['methods'][0].update(hasCode=True)),('metadata-interface-flags',lambda v:v['sourcePhysicalInventory']['dev/codex/schubert/nk/api/security/LoginResult'].update(flags=1536))]:
        bad=copy.deepcopy(p);change(bad)
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('invalid NoCode interface accepted '+label)
    input_hashes={}
    for binary,names in METHODS.items():
        path=original.TESTS[binary.rsplit('.',1)[1]];text=path.read_text()
        require(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+(\w+)\(',text)==names,'whole original method catalog')
        require(data.sha(path.read_bytes())==raw['begin']['testSourceHashes'][str(path)]==original.PINS[path.stem],'same source')
        input_hashes[str(path.relative_to(data.ROOT))]=data.sha(path.read_bytes())
    text=original.TESTS['AuthImmutableValueContractTest'].read_text()
    for token in ["\"P\".repeat(255)","\"あ\".repeat(85)","\"P\".repeat(256)","\"あ\".repeat(86)","\"LoginAccount[REDACTED]\"","new IssuedContext(null, CONTEXT","new IssuedContext(IDENTITY, null","new IssuedContext(IDENTITY, CONTEXT, null","new IssuedContext(IDENTITY, CONTEXT, AT, null)","\"issued context expiry must follow issue time\"","\"RevokedContext[REDACTED]\"","\"invalid logout result\"","\"2001:db8:0:0:0:0:0:1\"","\"login IP state has incorrect kind\"","\"login IP scope is invalid\"","\"login IP literal is invalid\"","\"login result owner differs\"","\"0000\", result.resultCode().wireValue()","\"0101\", denied.resultCode().wireValue()","\"0106\", locked.resultCode().wireValue()","new int[] {1, 900}","new int[] {0, 901}","\"login failure code is invalid\"","\"unlocked failure has no retry delay\"","\"login lock delay is outside 1..900\"","List.of(\"USER\", \"ADMIN\")","List.of(\"SUCCEEDED\", \"NO_ACCOUNT\", \"DISABLED\", \"PASSWORD_MISMATCH\", \"PREEXISTING_LOCK\")","List.of(\"LOGOUT\", \"DISABLED\", \"PASSWORD_RESET\", \"ADMIN\", \"EXPIRED\", \"REPLACED\")","\"authentication context is not valid\"","assertNull(value.getCause())","assertEquals(0, value.getSuppressed().length)"]:
        require(token in text,"independent literal value/profile/redaction/catalog oracle "+token)
    require(not any(x in text for x in ["DriverManager","getConnection(","preserveFatal(","attachSecondary(","Executors.","Instant.now","UUID.randomUUID","MessageDigest","Cipher."]), "no actual auth/DB/key/executor")
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],originalRawSha256=RAW,tests=12,suites=1,moduleSpecificOriginalPriorityContractsPreserved=True,independentModuleLocalThrowableGraphsOnly=False,pureAuthImmutableValuesAndCatalogOnly=True,junitFrameworkWorkerActualCount=None,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=12,originalTestSourceHashes=input_hashes,testPhysicalHashes=physical,testCrcIdentityClasses={r[1]:r[2] for r in crc},passiveTestCrcStage=stage,newSourcePrograms=9,newPhysicalClasses=11,metadataPhysicalClasses=1,partialSourcePrograms=0,newUniqueMethods=12,requiredRepeatedMethods=0,actualOwnedLoopbackFixtureNetwork=False,networkOperationCount=0,actualExternalNetworkActions=0,actualProductionServiceActions=0,originalProductTestsReexecuted=0,oldSourceTransferred=False,coverageExecUnion=False,actualDatabaseActions=0,actualVmActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
