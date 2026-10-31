"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16926_original_start_client_seventeen_pt as original
POST=('PG16928-original-start-client-seventeen-post-v1','77e02e5b4e000f30d0ae98e2e6a2249642ae42fad6eea1ff244c19eb1f63e8ad')
RAW=('PG16926-original-start-client-seventeen-pt-v1','3accdf1a31ffd7d711e0bcc2464b9c43ab0c8974e4379479c3ee25278e9d5241')
PREV=('PG16914-current2476-memory-live-intent-fence-registry-v1','881b7f3d10d92ad54bfa23f3f407f4038edb3cbfd1eb85c43c07cb90337b9000')
PLAN=('PG16924-original-start-client-fresh-review-binding-v1','87bfad620e55943f7e4640bc0a4c50cf0883a65365e3c3a46c023989a4a01f5e')
OUT=data.BASE/'PG16930-original-start-client-seventeen-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['memoryBusinessPortsAndOneOwnedBenignChild'] is True and plan['syntheticRetirementCallbacksInvoked'] is True and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==17 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==17 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"MONITOR":["BackupUnitStartClientTest",["CallerMonitorProbe.requireIndependent(","attempt.status()"]],"CLOSEONLY":["BackupUnitStartClientTest",["assertEquals(1, closes.get())","assertEquals(0, retires.get())","close-only is not retirement"]],"CADDYFENCE":["BackupUnitStartClientTest",["assertSame(failure, assertThrows(failure.getClass(), broken::requireRetained))","assertSame(failure, assertThrows(failure.getClass(), broken::retire))"]],"CADDYROLE":["BackupUnitStartClientTest",["void caddy457002WorkerRolesCannotCloseServiceObservation()","assertThrows(IOException.class, attempt::preserveObservation)"]],"UNKNOWNCLOSE":["BackupUnitStartClientTest",["void rootownerfd002UnknownCloseKeepsIdentityAndNeverRetriesConsumedOwner()","assertSame(failure, assertThrows(failure.getClass(), attempt::preserveObservation))"]],"INTENTORDER":["BackupUnitStartClientTest",["no start after uncertain intent publication","assertEquals(BackupUnitStartClient.Status.UNKNOWN, uncertainStart.start().status())"]],"RETAINED":["BackupUnitStartClientTest",["assertEquals(1, sequence.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count())","no proof on unknown","no proof on nonzero"]],"INTERRUPT":["BackupUnitStartClientTest",["assertEquals(0, starts[0])","assertEquals(0, retires[0])","assertTrue(Thread.currentThread().isInterrupted())"]],"REENTRY":["BackupUnitStartClientTest",["assertEquals(before + 1, rootChecks[0])","assertEquals(1, failedRetires[0])"]],"FIXEDARGV":["BackupUnitStartClientTest",["\"/usr/bin/systemctl\"","\"--system\"","\"--no-pager\"","\"--no-ask-password\"","\"--no-block\"","\"start\"","\"schubert-nk-backup.service\"","assertEquals(1, process.counts.get(FIXTURE_WAIT_F3010736))"]],"PRESTART":["BackupUnitStartClientTest",["assertEquals(0, launched[0])","assertEquals(failureAt, checks[0])"]],"NONZERO":["BackupUnitStartClientTest",["assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_NONZERO, attempt.status())","assertEquals(0, process.destroyed)"]],"TIMEOUT":["BackupUnitStartClientTest",["assertTrue(process.alive)","assertEquals(0, process.output.closed)","assertEquals(2, process.counts.get(FIXTURE_WAIT_F3010736))"]],"UNKNOWN":["BackupUnitStartClientTest",["assertEquals(BackupUnitStartClient.Status.UNKNOWN, nullAttempt.awaitClient())","assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.awaitClient(), missing)"]],"POSTINTERRUPT":["BackupUnitStartClientTest",["assertEquals(0, beforeStdin.input.closed)","assertEquals(0, afterWait.output.closed)","assertEquals(BackupUnitStartClient.Status.UNKNOWN, poisoned.awaitClient())"]],"OWNEDTRUE":["BackupUnitStartClientTest",["new MaintenanceUnitStopClient.NativeStart().execute(List.of(\"/usr/bin/true\"))","assertTrue(harmless.waitFor(5, TimeUnit.SECONDS))","assertEquals(0, harmless.exitValue())","harmless.getOutputStream().close()","harmless.getInputStream().close()","harmless.getErrorStream().close()"]],"TERMINAL":["BackupUnitStartClientTest",["assertEquals(1, spawns[0])","assertEquals(1, child.counts.get(FIXTURE_WAIT_F3010736))"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((437,248),(97,49),(7,9),(226,78))
    units={original.NAME:counts((137,159),(32,34),(2,5),(51,53)),original.PREFIX+'RootStartupContext':counts((195,80),(48,13),(2,3),(139,25)),original.PREFIX+'MaintenanceUnitStopClient':counts((105,9),(17,2),(3,1),(36,0))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=17,suites=1,newTestIds=0,cases=raw['cases'],targetSourceUnits=3,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=sorted([original.NAME+'$1',original.NAME+'$MarkerLease',original.PREFIX+'MaintenanceUnitStopClient',original.PREFIX+'MaintenanceUnitStopClient$Attempt',original.PREFIX+'MaintenanceUnitStopClient$Status',original.PREFIX+'RootStartupContext$Io',original.PREFIX+'RootStartupContext$NativeIo']),totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=False,ownThreadCount=1,declaredOwnedBenignChildCount=1,ownedBenignChildPath=str(original.BENIGN_CHILD),ownedBenignChildSha256=original.BENIGN_CHILD_SHA,actualRootMemoryFixtureOnly=True,actualRootNativeObservations=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,memoryBusinessPortsAndOneOwnedBenignChild=True,callerResourcesClosedByProduct=True,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=True,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==0 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit']
        require(len(cycle)==23 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in cycle.values()),'all cycle records absent')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==4 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
        r=v['rootNativeIoProbeAudit'];require(len(r)==3 and all(not q['recordPresent'] and q['trueProbeHits']==0 for q in r.values()),'actual Root native observations absent despite memory Root context')
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
    for key in ['physicalClasses','executable','fullSourceUnits','rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit','passiveNativeBoundaryAbsence','rootNativeIoProbeAudit']:
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=17,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=1,newPhysicalClasses=7,metadataPhysicalClasses=11,targetSourceUnitsMeasured=3,targetPhysicalClassesMeasured=27,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=3,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
