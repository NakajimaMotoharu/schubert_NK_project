"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17006_inspector_static_environment_six_pt as original
POST=('PG17008-inspector-static-environment-six-post-v1','25c269a0a0bda655e2e937d570fe8f5f149c159a922013356eac80ef621c17eb')
RAW=('PG17006-inspector-static-environment-six-pt-v1','ada9935b69ff7e7462af30a75f087c45f72b66bb7d9c36c4bdb952e7baa346f3')
PREV=('PG16996-current2525-morning-service-readiness-registry-v1','a8b22c3233bb63a34f4c945ddfbfb6cddddaee16f3c1f17d2ef3a354482b97fa')
PLAN=('PG17005-inspector-static-environment-review-v1','977d93c302deb80009c9d96a6d1129aaf4482673b519e67ec292a877f74cae8f')
OUT=data.BASE/'PG17010-inspector-static-environment-six-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['testPublicSourceRead'] is True and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==6 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==6 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"CFG001":["InspectorStaticEnvironmentTest",["assertEquals(GOLDEN, rendered)","accept(config(url, names))","reject(bytes(template))"]],"CFG002":["InspectorStaticEnvironmentTest",["GOLDEN + GOLDEN","for (int value = 0; value <= 255; value++)","if ((value >= 32 && value < 127) || value == golden[at]) continue"]],"CFG003":["InspectorStaticEnvironmentTest",["List.of(\"0\", \"00\", \"01\", \"65536\"","\"jdbc:postgresql://127.0.0.1:65535/\"","\"192.0.2.1\"","URL + \"?password=not-a-real-secret\""]],"CFG004":["InspectorStaticEnvironmentTest",["assertEquals(65519, prefix.length())","assertEquals(65535, at65535.length())","assertEquals(65536, at65536.length())","reject(config(URL, at65536 + \"X\"))","accept(config(URL, \"v1,V1\"))"]],"CFG005":["InspectorStaticEnvironmentTest",["assertThrows(NullPointerException.class, () -> InspectorStaticEnvironment.requireValid(null))","List.of(0, 65848, 65849)","assertEquals(65848, InspectorStaticEnvironment.MAXIMUM_BYTES)","assertEquals(\"inspector static environment is invalid\", failure.getMessage())","assertNull(failure.getCause())","assertEquals(0, failure.getSuppressed().length)","assertArrayEquals(before, value)"]],"CFG006":["InspectorStaticEnvironmentTest",["Executors.newFixedThreadPool(8)","for (int i = 0; i < 64; i++)","future.get(5, TimeUnit.SECONDS)","assertEquals(64, finished)"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((0,16),(0,3),(0,1),(0,16))
    units={original.NAME:totals}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=6,suites=1,newTestIds=0,cases=raw['cases'],targetSourceUnits=1,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[],totals=totals,strictFour100GateExit=0,targetUnitFour100=True,allMeasuredApplicableCountersCovered=True,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=False,ownThreadCount=8,declaredOwnExecutorInstances=1,declaredOwnTaskCount=64,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,pureStaticEnvironmentValuesOnly=True,testPublicSourceRead=True,publicSourceReadHashes={original.PUBLIC_TEMPLATE:original.PUBLIC_TEMPLATE_SHA},callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==1 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit']
        require(len(cycle)==23 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in cycle.values()),'all cycle records absent')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==5 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
        native=v['passiveNativeBoundaryAbsence'];require('rows' in native and len(native['rows'])==6 and all(row[3]=='0' for row in native['rows']) and v['forbiddenProductProbeHits']==0,'held/native probes absent')
    helper=p['originalUnusedHelperProbeAudit'];require(helper=={},'compiled original helpers not executed')
    command=raw['stages'][1]['command'];require(command.count('-Dnk.pt.repository='+str(data.ROOT))==1 and len([v for v in command if v.startswith('-Dnk.pt.repository=')])==1,'one exact public repository property')
    require(data.sha((data.ROOT/original.PUBLIC_TEMPLATE).read_bytes())==original.PUBLIC_TEMPLATE_SHA==plan['reviewedPublicSourceReads'][original.PUBLIC_TEMPLATE],'independent fixed public template byte hash')
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
    for number in ['311','343']:
        paths=list((data.ROOT/'documents/300_SS').glob('*/'+number+'_*.md'));require(len(paths)==1,'unique approved SS')
        relative=str(paths[0].relative_to(data.ROOT));blob=paths[0].read_bytes();require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS bytes');design[relative]=data.sha(blob)
    for path,pin in original.FIXTURES.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'independent fixed golden file bytes')
    for row in [p,old,plan]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=6,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=1,newPhysicalClasses=1,metadataPhysicalClasses=0,targetSourceUnitsMeasured=1,targetPhysicalClassesMeasured=1,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=1,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
