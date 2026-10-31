"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17070_morning_gate_evidence_seventeen_pt as original
POST=('PG17072-morning-gate-evidence-seventeen-post-v1','080633073174ea957e1272a1f5d92ff04e56fc60f929dbc5cf59259f6d16455a')
RAW=('PG17070-morning-gate-evidence-seventeen-pt-v1','cd1421e5d011cde71301fa3170e3525f22c0e4f566c26732b01ca1191f45cd85')
PREV=('PG17060-current2547-no-prior-broker-registry-v1','ef523fa81539f44dd15dcf0ac3df1f50acce34183615ad21ed9514e15f534a87')
PLAN=('PG17069-morning-gate-evidence-review-v1','5076b514948a6cc9be2a04ed7c4b19ad968bfc5295b890a633e14dc2b741554b')
OUT=data.BASE/'PG17074-morning-gate-evidence-seventeen-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['memoryJournalQueryPortsOnly'] is True and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
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
    oracle_groups={"ISSPG001":["MorningGateEvidenceTest",["SCHEMA|1|001|53514c|563030315f5f66697273742e73716c|-170000001|1","assertArrayEquals(expected.getBytes(StandardCharsets.US_ASCII), actual)","actual[0] = 'X'"]],"ISSREL001":["MorningGateEvidenceTest",["// Independently transcribed SS rows","for (byte value : field[2].getBytes(StandardCharsets.UTF_8))","facts(\"X\".repeat(32768), artifacts())"]],"ISSPG002":["MorningGateEvidenceTest",["for (int field = 0; field < 8; field++)","EPOCH.issued(\"a\".repeat(64))","MorningGateEvidence.postgres(EPOCH, MORNING, MORNING, database())"]],"ISSREL002":["MorningGateEvidenceTest",["missingArtifact.remove(\"VERSION\")","selected.put(\"unexpected\", \"1\")","badPath.put(wrong, \"b\".repeat(64))"]],"ISSPG003":["MorningGateEvidenceTest",["List.of(ROWS.get(1), ROWS.get(0))","nilRun ? new UUID(0, 0) : EPOCH.activation().run().id()","MorningGateEvidence.postgres(wrong, MORNING, BROKER, database())"]],"ISSBROKER002":["MorningGateEvidenceBrokerTest",["assertEquals(19715, expected.length)","assertArrayEquals(expected, encode(fixture(), JOURNAL))","actual[0] = 'X'"]],"ISSBROKER003":["MorningGateEvidenceBrokerTest",["if (slot == 0) broker.remove(\"name\")","if (slot == 1) topology.remove(FIXTURE_NK_EXPIRY_41CB6B4A)","fields.remove(topologySlot ? \"durable\" : \"maxSizeBytes\")"]],"ISSBROKER004":["MorningGateEvidenceBrokerTest",["if (slot == 0) roles.remove(FIXTURE_MOPS_5CCB9DD9)","5000, 0, ArtemisQueuePressureClient.Pressure.CRITICAL","assertThrows(NullPointerException.class, () -> encode(null, JOURNAL))"]],"ISSSTOP005":["MorningStopEvidenceTest",["for (boolean nativeInterval : List.of(false, true))","assertArrayEquals(expected, actual)","actual[0] = 0","old.recheck()"]],"ISSSTOP006":["MorningStopEvidenceTest",["epoch(boot).issued(\"a\".repeat(64))","assertEquals(\"BrokerJournalAnchor[redacted]\", anchor.toString())","MorningGateEvidence.stop(null, \"1\".repeat(32), \"2\".repeat(32), initial, old)"]],"ISSSTOP007":["MorningStopEvidenceTest",["e3a86812641c1394772a2e492a72624fb2c504b8b033358558e8ee6d79a74a5e","assertNotEquals(original, reordered)","original.replace(\"1790780400000000\", \"1790780400000001\")","original.replace(\"{\\\"MESSAGE\\\"\", \"{\\\"__SEQNUM\\\":\\\"9\\\",\\\"MESSAGE\\\"\")"]],"ISSUERGATE002":["MorningUnitTerminalsTest",["assertSame(parent, actual.parent())","assertEquals(seen, actual.units().stream().map(row -> row.manager().unit()).toList())","assertThrows(UnsupportedOperationException.class, () -> actual.units().clear())"]],"MTERMS001":["MorningUnitTerminalsTest",["void mterms001AllEightOrderedAndFresh()","MaintenanceUnit.CADDY","MaintenanceUnit.ARTEMIS","seen);"]],"MTERMS002":["MorningUnitTerminalsTest",["assertEquals(busy.ordinal() + 1, seen.size())","assertEquals(busy, seen.getLast())","assertNull(refusal.getCause())"]],"MTERMS003":["MorningUnitTerminalsTest",["assertEquals(0, refusal.getSuppressed().length)","var unknown = new IllegalStateException(\"unknown programming error\")","throw unknown","throw io"]],"MTERMS004":["MorningUnitTerminalsTest",["assertEquals(before, fixture.reads)","context.capture(RootStartupContext.Service.API)","() -> MorningUnitTerminals.requireQuiescent(context, api)"]],"MTERMS005":["MorningUnitTerminalsTest",["Thread.currentThread().interrupt()","Thread.interrupted()","assertEquals(Arrays.asList(MaintenanceUnit.values()), seen)","assertTrue(Thread.currentThread().isInterrupted())"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((121,492),(8,38),(0,6),(62,188))
    units={original.NAME:counts((74,314),(2,16),(0,1),(25,113)),original.PREFIX+'MorningUnitTerminals':counts((4,31),(3,8),(0,2),(0,14)),original.PREFIX+'BrokerJournalEvidence':counts((43,147),(3,14),(0,3),(37,61))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=17,suites=4,newTestIds=0,cases=raw['cases'],targetSourceUnits=3,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=True,publicDigestOnly=True,publicSyntheticUuidFixture=True,ownThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,memoryJournalQueryPortsOnly=True,callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,testPublicGoldenResourcesRead=True,publicRandomUuidValueOnly=True,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=True,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=4,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=2,newPhysicalClasses=5,metadataPhysicalClasses=2,targetSourceUnitsMeasured=3,targetPhysicalClassesMeasured=8,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=3,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
