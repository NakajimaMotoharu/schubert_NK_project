"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17120_original_completion_default_thirteen_pt as original
POST=('PG17122-original-completion-default-thirteen-post-v1','0d10875209b1f4aff31608faa307c751e4586199c3e39472f4cdf928af5b191a')
RAW=('PG17120-original-completion-default-thirteen-pt-v1','92c5e181d171b1f683856a25acd03e280c7c2e2ceff281e9111e8c5a6384f18c')
PREV=('PG17110-current2586-stop-pass-postgres-rows-registry-v1','e734570cc128072dfbe6f9b28aa30452cea34dab787c7c530f2a2cc2d2c91fa6')
PLAN=('PG17119-original-completion-default-review-v1','cbfc702a74b72ffb64a02992e77189dc80c86f333d8bcb5a450eb7799e612362')
OUT=data.BASE/'PG17124-original-completion-default-thirteen-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['memoryJournalQueryPortsOnly'] is False and plan['syntheticOriginalOwnerPortsOnly'] is True and plan['syntheticCompletionPublicationCallbacksInvoked'] is True and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==13 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==13 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"RLOOK852003":["MorningOriginalCompletionTest",["assertEquals(existing ? 0 : 1, f.publish)","assertEquals(Optional.of(DONE), f.stored)","\"completed-reference\"","f.alive.set(false)"]],"RLOOK852004":["MorningOriginalCompletionTest",["f.stored = Optional.of(DONE)","assertTrue(foreign.events.isEmpty())","new MorningNewRunAdmission.OriginalFiles() {}.referenceCompletedRun(","assertEquals(0, f.publish)"]],"RLOOK200002OWNER":["MorningOriginalCompletionTest",["thread.join()","assertInstanceOf(IOException.class, failure.get())","assertEquals(1, f.events.stream().filter(FIXTURE_REFERENCE_86A3D412::equals).count())","proof.referenceRun(null, observed)"]],"RLOOK200002FAIL":["MorningOriginalCompletionTest",["assertSame(kind == 0 ? f.io : kind == 1 ? f.runtime : f.fatal, actual)","f.expireAfterReference = true","assertThrows(IOException.class, () -> legacy.referenceRun(id, observed))"]],"ORIG455001":["MorningOriginalCompletionTest",["assertEquals(DONE, proof.complete(DONE))","FIXTURE_PUBLISH_69201707","assertEquals(1, f.publish)","assertThrows(IOException.class, proof::verify)"]],"COMP203003":["MorningOriginalCompletionTest",["assertEquals(3, f.events.size())","assertThrows(IOException.class, uncertain::verifyRetained)","legacy.verifyRetained()","assertEquals(1, legacyCalls.get())","assertTrue(foreign.events.isEmpty())"]],"ORIG455002":["MorningOriginalCompletionTest",["assertFalse(f.events.contains(FIXTURE_PENDING_12ADAC54))","assertEquals(0, f.publish)","DONE.endedAt().plusNanos(1000)","MaintenanceCompletion.Outcome.SUCCESS"]],"ORIG455003":["MorningOriginalCompletionTest",["assertThrows(IOException.class, proof::verify)","assertThrows(NullPointerException.class, () -> proof.complete(null))","assertTrue(f.events.isEmpty())","ACTIVATION.run().id()"]],"ORIG455004":["MorningOriginalCompletionTest",["assertEquals(phase.equals(FIXTURE_PENDING_12ADAC54) ? 0 : 1, f.publish)","if (!phase.equals(FIXTURE_PENDING_12ADAC54))","assertThrows(IOException.class, () -> proof.complete(DONE))"]],"ORIG455005":["MorningOriginalCompletionTest",["for (int rootFault = 1; rootFault <= 5; rootFault++)","assertSame(f.io, assertThrows(IOException.class, () -> proof.complete(DONE)))","assertEquals(rootFault <= 2 ? 0 : 1, f.publish)"]],"ORIG455006":["MorningOriginalCompletionTest",["f.wrongResult = !expiry","f.expireAfterPublish = expiry","assertThrows(IOException.class, proof::verify)","assertEquals(1, f.publish)"]],"ORIG455007":["MorningOriginalCompletionTest",["assertThrows(IOException.class, () -> old.complete(DONE))","assertThrows(IOException.class, () -> defaults.verifyCompleted(DONE))","scopedOriginalProof(null, f, state, f.alive, failure)","scopedOriginalProof(f::root, f, state, f.alive, null)"]],"ORIGINALPORT001":["UnsupportedOriginalProofTest",["assertEquals(0, resumes.get(), \"verification may not issue another resume\")","assertEquals(1, gates.get(), \"no post-verification owner gate after absent capability\")","assertEquals(\"owner inactive\", assertThrows(IOException.class, proof::verify).getMessage())","assertEquals(2, gates.get(), \"closed owner must be rejected before any verification IO\")"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((187,64),(49,19),(6,6),(23,27))
    units={original.NAME:counts((98,62),(25,17),(3,4),(15,27)),original.PREFIX+'MorningResumeAdmission':counts((89,2),(24,2),(3,2),(8,0))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=13,suites=2,newTestIds=0,cases=raw['cases'],targetSourceUnits=2,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[original.PREFIX+n+s for n in ['MorningNewRunAdmission','MorningResumeAdmission'] for s in ['$1','$2','$2$1']],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=True,ownThreadCount=4,declaredOwnPlatformThreadCount=1,declaredMaximumVirtualDrainWorkerCount=0,actualVirtualDrainWorkerCount=0,ownVirtualDrainWorkersInvoked=False,testOwnJavaMonotonicClockRead=False,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=False,declaredOwnExecutorInstances=3,declaredOwnTaskCount=3,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=True,syntheticCompletionPublicationCallbacksInvoked=True,callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==0 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit']
        require(len(cycle)==23 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in cycle.values()),'all cycle records absent')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==9 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=13,suites=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=2,newPhysicalClasses=26,metadataPhysicalClasses=14,targetSourceUnitsMeasured=2,targetPhysicalClassesMeasured=26,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=2,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
