"""Independent whole7 terminal literal projections and full nineteen-physical denominator, no real SQL."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17180_morning_terminal_observation_seven_pt as original
POST=('PG17182-morning-terminal-observation-seven-post-v1','39cae7f6d2f1cc4376f468d97c1f26a8b6439bd786883afe368a14d1a4e94957')
RAW=('PG17180-morning-terminal-observation-seven-pt-v1','d29d794fdae3d044c1999345ce68944437d9b10e5544ec8e980e6642d00d435a')
PREV=('PG17166-current2609-morning-launch-owner-registry-v1','597a383e5895c727c3bd3b1a014eeb4fd5bc03db4d9c21a2066b2cc95ee79253')
PLAN=('PG17179-morning-terminal-observation-review-v1','a1fbb15035a323e0e8a9ae19b86824f10c8e05d5bf5a92e19811087a506f0a6b')
OUT=data.BASE/'PG17184-morning-terminal-observation-seven-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_TARGET_METHOD_AND_WHOLE_ORIGINAL_TEST_REVIEW_ALL_SOURCE_BYTES_BOUND_NOT_WHOLE_PG_ACCEPTANCE' and plan['priorProductResultsTransferred'] is False and plan['memoryJournalQueryPortsOnly'] is False and plan['memoryRootScopeAndCleanupCompletionValuesOnly'] is False and plan['declaredFakeExclusiveLockOnly'] is False and plan['memoryTerminalObservationValuesOnly'] is True and plan['syntheticResultSetGettersOnly'] is True and plan['wholeMorningDatabaseSessionRuntimeReviewComplete'] is False and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==7 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==7 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"EXP1749001":["MorningExpiryObservationInvariantTest",["assertEquals(END, fresh.ended())","assertEquals(2, fresh.result().target())","assertEquals(200, fresh.audit().estimatedBytes())","assertSame(receipt, fresh.receipt())","assertEquals(\"ExpiryObservation[actual=<redacted>]\", fresh.toString())"]],"EXP1749002":["MorningExpiryObservationInvariantTest",["begins, START.minusSeconds(1), SUCCESS, audit(), receipt","begins, END, SUCCESS, audit(), ExpiryReceiptFixture.backupReceipt(0)","audit(\"WARNING\", 2, 2, 0, 200, END)","audit(FIXTURE_SUCCESS_10855C7F, 2, 2, 0, 201, END)"]],"EXP1749003":["MorningExpiryObservationInvariantTest",["begins, END, SKIP, audit(), receipt","begins, START, SUCCESS, audit(), receipt","begins, START, SKIP, audit(\"WARNING\", 2, 2, 0, 200, END)","begins, START, SKIP, audit(), ExpiryReceiptFixture.receipt(10)"]],"EXP1749004":["MorningExpiryObservationInvariantTest",["new MorningDatabaseSession.ExpiryBegins(null, Optional.empty())","new MorningDatabaseSession.ExpiryBegins(attempt(false), null)","new MorningDatabaseSession.ExpiryObservation(begins, END, SUCCESS, audit(), null)","begins, END.plusNanos(1), SUCCESS, audit(), receipt"]],"ISSCOMP001":["BackupTerminalObservationTest",["m.put(\"id\", 1L)","m.put(FIXTURE_BYTE_COUNT_6D76E237, 26L)","assertEquals(26, actual.result().bytes())","assertFalse(actual.toString().contains(RUN.id().toString()))","assertEquals(0, s.result().target())"]],"ISSCOMP002":["BackupTerminalObservationTest",["Map.entry(\"id\", 2L)","Map.entry(\"step\", \"BACKUP_CONFIG\")","Map.entry(FIXTURE_ERROR_CODE_B886CCEF, \"UNKNOWN\")","var unknown = new IllegalArgumentException(\"private driver failure\")","() -> BackupStepRepository.readTerminal(null, DB, END)"]],"ISSCOMP003":["BackupTerminalObservationTest",["mutable.clear()","assertEquals(List.of(d, c), observed.current())","assertThrows(UnsupportedOperationException.class, () -> observed.current().clear())","new MorningDatabaseSession.BackupObservation(List.of(sd, sc), List.of(d, c)).prior()","List.of(wrongEnd, wrongEndConfig), List.of(d, c)"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((935,116),(106,10),(8,5),(517,108))
    units={original.NAME:counts((840,61),(99,5),(8,3),(449,76)),original.PREFIX+'BackupStepRepository':counts((95,55),(7,5),(0,2),(68,32))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=7,suites=2,newTestIds=0,cases=raw['cases'],targetSourceUnits=2,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=sorted(original.NAME+s for s in ['','$1','$Access','$BackupBegins','$DatabaseObservation','$RoleObservation','$Schema','$Session']),totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=True,ownThreadCount=0,declaredOwnPlatformThreadCount=0,declaredMaximumVirtualDrainWorkerCount=0,actualVirtualDrainWorkerCount=0,ownVirtualDrainWorkersInvoked=False,testOwnJavaMonotonicClockRead=False,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=False,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=True,syntheticJdbcApiCallsInvoked=True,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,memoryTerminalObservationValuesOnly=True,syntheticResultSetGettersOnly=True,wholeMorningDatabaseSessionRuntimeReviewComplete=False,callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==0 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit']
        require(len(cycle)==23 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in cycle.values()),'all cycle records absent')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==10 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
        native=v['passiveNativeBoundaryAbsence'];require('rows' in native and len(native['rows'])==6 and all(row[3]=='0' for row in native['rows']) and v['forbiddenProductProbeHits']==0,'held/native probes absent')
    helper=p['originalUnusedHelperProbeAudit'];require(helper=={},'compiled original helpers not executed')
    contract(p);labels=[]
    for key,value in fields.items():
        bad=copy.deepcopy(p)
        if type(value) is bool:bad[key]=not value
        elif type(value) is int:bad[key]=value+1
        elif isinstance(value,str):bad[key]='BAD'
        elif value is None:bad[key]=100
        elif isinstance(value,list):bad[key]=['BAD']
        else:bad[key]={}
        require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false claim accepted '+key)
    for key in ['physicalClasses','executable','fullSourceUnits','rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit','passiveNativeBoundaryAbsence']:
        bad=copy.deepcopy(p);bad[key]={}
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('erased physical or boundary metadata accepted')
    design={}
    for number in ['341','342','343']:
        paths=list((data.ROOT/'documents/300_SS').glob('*/'+number+'_*.md'));require(len(paths)==1,'unique approved SS')
        relative=str(paths[0].relative_to(data.ROOT));blob=paths[0].read_bytes();require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS bytes');design[relative]=data.sha(blob)
    for path,pin in original.FIXTURES.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'independent fixed golden file bytes')
    for row in [p,old,plan]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=7,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=2,newPhysicalClasses=19,metadataPhysicalClasses=6,targetSourceUnitsMeasured=2,targetPhysicalClassesMeasured=19,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=2,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
