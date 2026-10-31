"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17104_stop_pass_postgres_rows_eleven_pt as original
POST=('PG17106-stop-pass-postgres-rows-eleven-post-v1','9100afdb99d43b8d3359a8840c30fc981f9aa0d14ad78c771b4a4854ebe96b77')
RAW=('PG17104-stop-pass-postgres-rows-eleven-pt-v1','9bc8c7cadfc8d8d88fdd0be484b75222683f58b92e5ce996a16ac0a8a5823d27')
PREV=('PG17094-current2575-broker-cycle-query-registry-v1','77c898f3394948f03a994af4724920366b50b921b7f6e99096d6be2957e7b172')
PLAN=('PG17103-stop-pass-postgres-rows-review-v1','98d54d5bb68375856afa0f971d5a4f9ec829e0146103f0ae1ff1e7bc22d85d12')
OUT=data.BASE/'PG17108-stop-pass-postgres-rows-eleven-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['memoryJournalQueryPortsOnly'] is False and plan['pureStopPassCallbacksAndPostgresRecordFormatterOnly'] is True and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==11 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==11 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"MPASS001":["MorningStopPassTest",["assertEquals(ORDER, stopped)","assertEquals(ORDER, observed)","assertEquals(18, gates.get())","assertEquals(\"all-eight-fresh\", order.getLast())"]],"MPASS002":["MorningStopPassTest",["var failure = new IOException(\"policy unavailable\")","throw failure","return fail(\"no stop on failed preflight\")"]],"MPASS003":["MorningStopPassTest",["assertEquals(failed.ordinal() + 1, stopped.size())","assertEquals(failed.ordinal(), observed.size())","MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO"]],"MPASS004":["MorningStopPassTest",["assertEquals(\"not terminal\", refusal.getMessage())","assertEquals(List.of(MaintenanceUnit.CADDY, MaintenanceUnit.WEB), stopped)"]],"MPASS005":["MorningStopPassTest",["assertEquals(0, observed.get())","assertEquals(2, awaited.get())","assertEquals(8, observed.get())"]],"MPASS006":["MorningStopPassTest",["assertTrue(firstAwait.await(2, TimeUnit.SECONDS))","assertFalse(result.isDone(), \"UNKNOWN must not return to an M-owning caller\")","release.countDown()","assertTrue(result.get(2, TimeUnit.SECONDS))"]],"MPASS007":["MorningStopPassTest",["assertFalse(Thread.currentThread().isInterrupted())","assertEquals(1, awaited.get())","assertTrue(Thread.currentThread().isInterrupted())","Thread.interrupted()"]],"MPASS008":["MorningStopPassTest",["() -> new MorningStopPass(null, null, null)","() -> MorningStopPass.create(null, null)","() -> MorningStopPass.create(context, api)","assertNull(refusal.getCause())"]],"MPASS009":["MorningStopPassTest",["fail(\"nonzero is not a Unit stop\")","fail(\"nonzero is not full success\")","assertEquals(1, awaited.get())","assertNull(refusal.getCause())"]],"MPASS010":["MorningStopPassTest",["assertEquals(Thread.State.TIMED_WAITING, state)","thread.get().interrupt()","assertTrue(result.get(5, TimeUnit.SECONDS))","assertTrue(awaited.get() >= 1)","assertEquals(ORDER, observed)"]],"PGROWS001":["PostgresObservationRowsTest",["for (int rank = 1; rank <= 999; rank++)","schema_rows=1000","assertEquals(1001, tooMany.release().schemaRows().size())","assertEquals(1000, normal.release().schemaRows().size())","var gap = observation(List.of(schema(), sql(2)))","assertEquals(2, gap.release().schemaRows().get(1).installedRank())"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((283,164),(22,14),(3,2),(107,45))
    units={original.NAME:counts((25,34),(12,6),(3,1),(3,11)),'dev/codex/schubert/nk/batch/file/MorningGateEvidence':counts((258,130),(10,8),(0,1),(104,34))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=11,suites=2,newTestIds=0,cases=raw['cases'],targetSourceUnits=2,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[original.NAME+s for s in ['$1','$1$1','$2']],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=True,ownThreadCount=2,declaredOwnExecutorInstances=2,declaredOwnTaskCount=2,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=True,testOwnJavaMonotonicClockRead=True,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,memoryJournalQueryPortsOnly=False,pureStopPassCallbacksAndPostgresRecordFormatterOnly=True,callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,testPublicGoldenResourcesRead=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==0 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit']
        require(len(cycle)==23 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in cycle.values()),'all cycle records absent')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==7 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
        native=v['passiveNativeBoundaryAbsence'];require('rows' in native and len(native['rows'])==6 and all(row[3]=='0' for row in native['rows']) and v['forbiddenProductProbeHits']==0,'held/native probes absent')
    helper=p['originalUnusedHelperProbeAudit'];require(helper and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in helper.values()),'compiled original helpers not executed')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=4,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=1,newPhysicalClasses=8,metadataPhysicalClasses=4,targetSourceUnitsMeasured=2,targetPhysicalClassesMeasured=9,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=2,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
