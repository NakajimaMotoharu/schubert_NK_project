"""Independent whole33 source/oracle join; distinguish injected cycle from actual Root recovery."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16793_public_root_proof_original_four_pt_v2 as original
POST=('PG16794-public-root-proof-original-four-post-v1','bb7583444c93217cb38d76f63c36858e8a51f8d3f15ab420b60761eb157d5207')
RAW=('PG16793-public-root-proof-original-four-pt-v2','f16d4dc5f4f659055627c8fed7c667ad02b7014fd4b00fe2678e9aa44d32831c')
PREV=('PG16785-current2385-public-permit-records-registry-v3','10ea750ad9969cf9180508cee21b5db01cd4690839b0f8d1084323231ef4fbd2')
PLAN=('PG16791-public-root-proof-fresh-review-binding-v2','d5b91e536e3dfa0e84f6eb4943b4f327d3e93ee9870b261d7f7ab1a5011f363d')
OUT=data.BASE/'PG16796-public-root-proof-original-four-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['publicCorrelationValuesOnly'] is True and plan['actualRootAuthorityOrLaunchInvoked'] is False and plan['unselectedOriginalHelperTestsExecuted'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==4 and not expected&{(v['classname'],v['name']) for v in old['cases']},'33 fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==4 and set(actual)==expected,'all 33 actual original cases')
    oracle_groups={
      'ROOTPROOF001':['assertArrayEquals(expected.getBytes(StandardCharsets.US_ASCII), frame.encode())','assertEquals(17, frame.fields().size())','assertFalse(frame.fields().containsKey("proof_fd"))'],
      'ROOTPROOF002':['for (int absent = 0; absent < 6; absent++)','new StartupAdmissionFile.Admission(127, 123, 456)','actual, A, ID, observed, "0".repeat(64)'],
      'ROOTPROOF005':['for (int field = 0; field < 3; field++)','actual, A, ID, wrong, "e".repeat(64)'],
      'ROOTTICKET001':['replace("service=API", "service=WEB")','replace("pid=300", "pid=301")','replace("start_ticks=200", "start_ticks=201")','RootStartupPending.verifySelf(launch, null)']}
    require(all(all(token in texts['RootServiceProofTest'] for token in tokens) for tokens in oracle_groups.values()),'independent full-byte/typed rows/identity/TX/event/time oracles')
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((169,46),(26,2),(1,2),(46,27))
    units={'dev/codex/schubert/nk/batch/file/RootServiceLauncher':counts((96,35),(12,1),(0,1),(23,14)),'dev/codex/schubert/nk/batch/file/RootStartupPending':counts((73,11),(14,1),(1,1),(23,13))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=4,suites=1,newTestIds=0,cases=raw['cases'],targetSourceUnits=2,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=['dev/codex/schubert/nk/batch/file/RootStartupPending$1'],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=False,publicDigestOnly=False,publicSyntheticUuidFixture=True,ownThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,publicCorrelationValuesOnly=True,actualRootAuthorityOrLaunchInvoked=False,unselectedOriginalHelperTestsExecuted=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
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
    require(p['metadataKinds']=={n:('COMPILER_SYNTHETIC_STANDARD_FILTER' if n in original.GENERATED_METADATA else 'NO_CODE') for n in original.METADATA} and p['generatedCompilerMetadata']==sorted(original.GENERATED_METADATA),'generated Code with official zero counters is not NoCode')
    for n,row in p['sourcePhysicalInventory'].items():
        if n in original.GENERATED_METADATA:require(row['flags']==4128 and row['methods']==[dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True,codeLength=40)],'exact compiler enum map structure')
        elif n in original.METADATA:require(row['flags']==1536 and not any(m['hasCode'] for m in row['methods']),'genuine NoCode interfaces')
    require(len(p['unusedNativeFixtureAudit'])==3 and all(not v['recordPresent'] and v['trueProbeHits']==0 for v in p['unusedNativeFixtureAudit'].values()),'all unused native fixture definitions unexecuted')
    file_call=lambda value:re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',value) is not None
    lexical=[('Files.readString(path)',True),('java.nio.file.Files.readString(path)',True),('ServiceConfigFiles.Service.values()',False),('StartupLaunchFilesTest.epoch()',False)]
    require(all(file_call(t) is e for t,e in lexical) and not file_call(texts['RootServiceProofTest']) and 'Files.' in texts['RootServiceProofTest'],'four word-boundary vectors and exact original false-match')
    parent_tests=[
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupPermitRecordsTest.java',
      'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/BootstrapClosingBoundaryTest.java']
    for path in parent_tests:require('Files.' not in (data.ROOT/path).read_text(),'finite parent nonapplicable false-match')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=4,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,wordBoundaryGuardVectors=4,unusedNativeFixtureDefinitionsVerified=3,finiteParentGuardsNotApplicable=parent_tests,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=2,newPhysicalClasses=9,metadataPhysicalClasses=6,generatedCompilerMetadataCount=1,four100SourceProgramsMeasured=0,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=2,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
