"""Independent original proxy3 literals and full two-physical closure, no broker or runtime union."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17200_artemis_startup_proxy_three_pt as original
POST=('PG17202-artemis-startup-proxy-three-post-v1','1220d92449ba73e6ce1e62aa542ab436e1c09e84fd09b936eeac14839699149d')
RAW=('PG17200-artemis-startup-proxy-three-pt-v1','a14460820fe46d6c88acd6290bd1d728903d386c3804a5ef6dcccb916d4b15e2')
PREV=('PG17186-current2616-morning-terminal-observation-registry-v1','1002c01948b4af7ff64030c999c31df682775f2461c194d052d4904186ed18d4')
PLAN=('PG17199-artemis-startup-proxy-review-v1','bf7c77a01d5fbc10ceda58bf2e4f15cd5c6f5fb399fbb445ce7120d962590c9e')
OUT=data.BASE/'PG17204-artemis-startup-proxy-three-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['memoryJournalQueryPortsOnly'] is False and plan['memoryRootScopeAndCleanupCompletionValuesOnly'] is False and plan['declaredFakeExclusiveLockOnly'] is False and plan['syntheticArtemisSessionProxyAndMapOnly'] is True and plan['defaultClientFirstAddressQueryRejectsInOwnProxy'] is True and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==3 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==3 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"OPSMQ029":["ArtemisStartupObservationTest",["assertEquals(List.of(0, 1, 2, 3, 4, 5), calls)","values.clear()","assertEquals(6, observed.size())","assertThrows(UnsupportedOperationException.class, () -> observed.clear())","\"unexpected borrowed session call: addressQuery\""]],"OPSMQ030":["ArtemisStartupObservationTest",["for (int failedStep = 0; failedStep < 6; failedStep++)","assertEquals(\"synthetic private broker reply\", failure.getMessage())","assertNull(failure.getCause())","assertEquals(failedStep + 1, calls.size())","for (int index = 0; index <= failedStep; index++) assertEquals(index, calls.get(index))"]],"OPSMQ031":["ArtemisStartupObservationTest",["Map.<String, ArtemisQueuePressureClient.Pressure>of()","missing(),","excess(),","nullElement()","assertSame(fatal, observed)","assertEquals(1, fatalCalls.get())","new ArtemisStartupObservation(valid, valid, valid, valid, valid, null)"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((37,34),(10,7),(1,1),(1,9))
    units={original.NAME:totals}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=3,suites=1,newTestIds=0,cases=raw['cases'],targetSourceUnits=1,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[original.NAME+'$Evidence'],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=False,ownThreadCount=0,declaredOwnPlatformThreadCount=0,declaredMaximumVirtualDrainWorkerCount=0,actualVirtualDrainWorkerCount=0,ownVirtualDrainWorkersInvoked=False,testOwnJavaMonotonicClockRead=False,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=False,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,syntheticArtemisSessionProxyAndMapOnly=True,defaultClientFirstAddressQueryRejectsInOwnProxy=True,callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=3,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=0,targetSourceUnitsMeasured=1,targetPhysicalClassesMeasured=2,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=1,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
