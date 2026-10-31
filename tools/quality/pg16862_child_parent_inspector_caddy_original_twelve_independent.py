"""Independent original Broker/Caddy seven, full twelve-class denominator and literal observation oracle."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16858_child_parent_inspector_caddy_original_twelve_pt as original
POST=('PG16860-child-parent-inspector-caddy-original-twelve-post-v1','e123dc5841bcb11dbadc3f877013c38a1bb98c6d9279843cc5ff2549236d71cc')
RAW=('PG16858-child-parent-inspector-caddy-original-twelve-pt-v1','4486e6243658308df4b1a4ff4f5b4e797636cee2aa1518939e06a0c3cdf82835')
PREV=('PG16846-current2422-child-broker-caddy-registry-v1','953d9299af7bb5233dcd1f5b8b83bb7bdc83e4156191144da96777bd330243b3')
PLAN=('PG16857-child-parent-inspector-caddy-fresh-review-binding-v1','76a3cf90afc85cae35c808b96db7156f948a0613b2c97c80d24ed967016cf9b8')
OUT=data.BASE/'PG16862-child-parent-inspector-caddy-original-twelve-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['injectedDaemonObservationOnly'] is True and plan['originalNssFixtureOnly'] is True and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==12 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==12 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={
      'CINSPECT001':('ChildMaintenanceInspectorTest',['assertEquals(44, result.child().pid())','assertEquals(43, result.wrapper().pid())','assertEquals(12346, result.child().startTicks())','assertEquals(12345, result.wrapper().startTicks())']),
      'CINSPECT002':('ChildMaintenanceInspectorTest',['assertSame(','assertEquals(0, error.getSuppressed().length)','assertNull(error.getCause())']),
      'CINSPECT005':('ChildMaintenanceInspectorTest',['List.of("pidOne", "ownUid", "terminalInterrupt")','assertEquals(fault.equals("terminalInterrupt"), Thread.currentThread().isInterrupted())']),
      'MANAGER4404-003':('ChildMaintenanceParentTest',['fixture.swappedOrder = swapped','assertEquals(2, fixture.units)','assertEquals(2, fixture.owned.size())']),
      'MANAGER4404-004':('ChildMaintenanceParentTest',['fixture.orderDrift = true','assertThrows(','assertEquals(2, fixture.units)']),
      'CPARENT-GROUPS':('ChildMaintenanceParentTest',['List.of("", "0", "7", "0 7")','missing.missingGroups = true','"0 0", "-1"']),
      'CPARENT-BOTH':('ChildMaintenanceParentTest',['context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.MORNING, owner())','context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.CLEANUP, owner())','assertEquals(4, fixture.owned.size())']),
      'CPARENT-FAILURE':('ChildMaintenanceParentTest',['Optional.empty()','assertSame(','assertNull(error.getCause())']),
      'CPARENT005':('ChildMaintenanceParentTest',['List.of("substate", "terminalInterrupt")','assertEquals(fault.equals("terminalInterrupt"), Thread.currentThread().isInterrupted())']),
      'CADDY-ID001':('FixedCaddyIdentityTest',['assertEquals(997L, actual.uid())','assertEquals(993L, actual.gid())','assertEquals("993", actual.groupArgument())']),
      'CADDY-ID002':('FixedCaddyIdentityTest',['assertEquals(1, fixture.commands.size())','assertEquals(2, fixture.commands.size())','assertEquals(0, error.getSuppressed().length)']),
      'CADDY-ID003':('FixedCaddyIdentityTest',['assertSame(marker, assertThrows(marker.getClass(), subject::resolveCaddy))','assertEquals(1, calls.get())','assertEquals("fixed NSS query", absent.getMessage())'])}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent literal oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((288,261),(69,32),(5,8),(225,169))
    units={original.PREFIX+'ChildStartupContext':counts((146,187),(33,20),(3,4),(125,119)),original.PREFIX+'FixedServiceIdentity':counts((61,48),(22,9),(1,2),(31,33)),original.PREFIX+'MaintenanceOwnerFrame':counts((81,26),(14,3),(1,2),(69,17))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=12,suites=3,newTestIds=0,cases=raw['cases'],targetSourceUnits=3,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=sorted(original.PREFIX+n for n in ['ChildStartupContext$Inputs','ChildStartupContext$Io','ChildStartupContext$NativeIo','FixedServiceIdentity$NativeQuery','MaintenanceOwnerFrame$Guard']),totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=True,ownThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,injectedDaemonObservationOnly=True,originalNssFixtureOnly=True,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==0 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit']
        require(len(cycle)==23 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in cycle.values()),'all cycle records absent')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==5 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
        native=v['passiveNativeBoundaryAbsence'];require('rows' in native and len(native['rows'])==6 and all(row[3]=='0' for row in native['rows']) and v['forbiddenProductProbeHits']==0,'held/native probes absent')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=12,suites=3,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=0,newPhysicalClasses=0,metadataPhysicalClasses=4,targetSourceUnitsMeasured=3,targetPhysicalClassesMeasured=17,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=3,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
