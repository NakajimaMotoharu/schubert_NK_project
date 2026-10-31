"""Independent whole33 source/oracle join; distinguish injected cycle from actual Root recovery."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16776_public_permit_records_original_eight_pt as original
POST=('PG16778-public-permit-records-original-eight-post-v1','36dbe471c5a24e52443f79c739a4f16afc70a1f1a90d66f55f80287bc09488f8')
RAW=('PG16776-public-permit-records-original-eight-pt-v1','a4c752dbdd39d0188790d6bca3a8f3972be2bf72579e215789fd99b71370189b')
PREV=('PG16766-current2377-bootstrap-closing-registry-v1','766715c00a12e9a98cb962318b0cade732abfd457a5a2f800e35b1b41b2672ae')
PLAN=('PG16775-public-permit-records-fresh-review-binding-v1','4d07207f07d0fbd79308c42ee0ed62030aeaaff1fa66364d305a47b59ba3aed7')
OUT=data.BASE/'PG16780-public-permit-records-original-eight-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['publicRecordValuesOnly'] is True and plan['publicDigestOnly'] is True and plan['actualPermitIssueSignPublishOrRetire'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==8 and not expected&{(v['classname'],v['name']) for v in old['cases']},'33 fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==8 and set(actual)==expected,'all 33 actual original cases')
    oracle_groups={
      'PERMITREC001':['assertArrayEquals(bytes(INVALID), StartupPermitRecords.epoch(invalid()))','assertArrayEquals(bytes(GOLD), StartupPermitRecords.permit(value()))'],
      'PERMITREC002':['"x".repeat(8193)','nonascii[3] = (byte) 128','text + "unknown=x'],
      'PERMITREC003':['"ABCDEFAB-1111-1111-1111-111111111111"',"for (char member : List.of('b', 'c', 'd', 'e', 'f'))"],
      'PERMITREC004':['invalid().issued("a".repeat(64)).issued("b".repeat(64))','Optional.empty()'],
      'PERMITREC005':['MessageDigest.getInstance("SHA-256").digest(bytes(GOLD))','throw new NoSuchAlgorithmException("secret sentinel")','assertNull(failure.getCause())'],
      'PERMITREC006':['9999-12-31T23:59:59.999999Z','2026-09-27T00:00:00.000000001Z'],
      'PERMITREC007':['for (int i = 0; i < 5; i++)','for (int i = 0; i < 9; i++)','Arrays.fill(encoded, (byte) 0)'],
      'PERMITREC008':['Executors.newFixedThreadPool(4)','for (int i = 0; i < 32; i++)','workers.invokeAll(calls)']}
    require(all(all(token in texts['StartupPermitRecordsTest'] for token in tokens) for tokens in oracle_groups.values()),'independent full-byte/typed rows/identity/TX/event/time oracles')
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((0,119),(0,25),(0,4),(0,30))
    units={'dev/codex/schubert/nk/batch/file/StartupPermitRecords':totals}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=8,suites=1,newTestIds=0,cases=raw['cases'],targetSourceUnits=1,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[],totals=totals,strictFour100GateExit=0,targetUnitFour100=True,allMeasuredApplicableCountersCovered=True,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=True,publicDigestOnly=True,publicSyntheticUuidFixture=True,ownThreadCount=4,declaredOwnExecutorInstances=1,declaredOwnTaskCount=32,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,publicRecordValuesOnly=True,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=8,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=1,newPhysicalClasses=5,metadataPhysicalClasses=1,four100SourceProgramsMeasured=1,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
