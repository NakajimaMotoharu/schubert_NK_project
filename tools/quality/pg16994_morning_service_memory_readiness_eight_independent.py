"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16990_morning_service_memory_readiness_eight_pt as original
POST=('PG16992-morning-service-memory-readiness-eight-post-v1','838115a0ed2723b98629b3bbbac3efb35b543b1031fa13354b01abe43c718ab7')
RAW=('PG16990-morning-service-memory-readiness-eight-pt-v1','6a64ddcfb4b0021b44fe8ae82d727e50dfe3656969bea91928897cf2484067b8')
PREV=('PG16980-current2517-root-generation-counterexample-registry-v1','b40926fc863ff327d1d4eefc1683d5240bf9256ec098dd46c49db94b31a5f68f')
PLAN=('PG16989-morning-service-memory-readiness-review-v1','8831c42b8cc66f775b36cc7cf48d4227a9206398ce149ee7fdb73e9fc41b293b')
OUT=data.BASE/'PG16994-morning-service-memory-readiness-eight-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['rootMemoryPortsOnly'] is True and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==8 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==8 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"READY1413001":["MorningServiceReadinessTest",["f.rawHighBitStatus = true","assertEquals(1, f.requests)","assertEquals(0, f.sockets)"]],"EXECGEN309003":["MorningServiceReadinessTest",[".replace(\") R \", \") Z \")","assertFalse(assertDoesNotThrow(observer::ready))","assertEquals(2, f.requests)","assertFalse(root.serviceGenerationExited(morning, child))"]],"READY428001":["MorningServiceReadinessTest",["assertEquals(3, f.guards)","assertEquals(2, f.statusReads)","assertEquals(2, f.sockets)","f.after = Set.of(\"other\")"]],"READY428002":["MorningServiceReadinessTest",["\"CapInh\"","\"CapPrm\"","\"CapEff\"","\"CapBnd\"","\"CapAmb\"","MAIN + \"\\\\0\" + MAIN + \"\\\\0\""]],"READY428003":["MorningServiceReadinessTest",["new MorningServiceReadiness.Response(503, \"{\\\\\\\"status\\\\\\\":\\\\\\\"UP\\\\\\\"}\")","new MorningServiceReadiness.Response(301, GOLDEN)","GOLDEN.replace(\"\\\\\\\"025\\\\\\\"\", \"\\\\\\\"023\\\\\\\"\")"]],"READY428004":["MorningServiceReadinessTest",["for (int call = 1; call <= 8; call++)","for (int call = 1; call <= 3; call++)","assertThrows(NullPointerException.class, f.observer()::ready)"]],"READY428005":["MorningServiceReadinessTest",["\"0000000000000000FFFF00000100007F:1F9B\"","\"0100007F:1F9B\"","\"0A\"","Arrays.copyOf(row, 9)","Set.of(\"12346\")"]],"READY428006":["MorningServiceReadinessTest",["for (String key : INFO.keySet())","missing.remove(key)","List.of(\"\", \"\\\\\\\"\", \"x\".repeat(129))"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((179,240),(53,26),(3,5),(127,138))
    units={original.NAME:counts((116,159),(42,19),(2,3),(100,64)),original.PREFIX+'MorningServiceReadiness':counts((63,81),(11,7),(1,2),(27,74))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=8,suites=1,newTestIds=0,cases=raw['cases'],targetSourceUnits=2,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),metadataKinds={n:('COMPILER_SYNTHETIC_STANDARD_FILTER' if n in original.GENERATED_METADATA else 'NO_CODE') for n in original.METADATA},generatedCompilerMetadata=sorted(original.GENERATED_METADATA),unexecutedCodeClasses=sorted([original.NAME+'$Io',original.NAME+'$NativeIo',original.PREFIX+'MorningServiceReadiness$NativeIo']),totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=False,ownThreadCount=0,declaredOwnedBenignChildCount=0,actualRootMemoryFixtureOnly=True,actualRootNativeObservations=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,rootMemoryPortsOnly=True,readinessMemoryPortsOnly=True,actualNetworkActions=0,callerResourcesClosedByProduct=True,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
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
        r=v['readinessNativeIoProbeAudit'];require(len(r)==1 and all(not q['recordPresent'] and q['trueProbeHits']==0 for q in r.values()),'actual readiness NativeIo never executed')
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
    for key in ['physicalClasses','executable','fullSourceUnits','rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit','passiveNativeBoundaryAbsence','rootNativeIoProbeAudit','readinessNativeIoProbeAudit']:
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=8,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=1,newPhysicalClasses=6,metadataPhysicalClasses=6,targetSourceUnitsMeasured=2,targetPhysicalClassesMeasured=14,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=2,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
