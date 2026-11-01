"""Independent original20 buffer/ACL literals, three bootstrap alias Main, genuine random fixture disclosure."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg17216_bootstrap_credential_values_twenty_pt as original
POST=('PG17218-bootstrap-credential-values-twenty-post-v1','558a9b4aceeae4b3541be0cadfe7586e71db7d08ff2fa55470094b4ef0872dbd')
RAW=('PG17216-bootstrap-credential-values-twenty-pt-v1','57c0aeeab750d8a6018dfea56c83cf2f82e4d620fbde731bdee1fef79674e8c3')
PREV=('PG17206-current2619-artemis-startup-proxy-registry-v1','c6fa121334eb414f05ea14046a99695b66d0d4368dd4830784329c602090b531')
PLAN=('PG17215-bootstrap-credential-values-review-v1','1927ca63534fcc82d78a3fe85f86f4e4ddea5e4f39f4ccfc49d377f052015f94')
OUT=data.BASE/'PG17220-bootstrap-credential-values-twenty-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reviewKind']=='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW' and plan['priorProductResultsTransferred'] is False and plan['memoryJournalQueryPortsOnly'] is False and plan['memoryRootScopeAndCleanupCompletionValuesOnly'] is False and plan['declaredFakeExclusiveLockOnly'] is False and plan['inMemoryCredentialBufferAndAclValuesOnly'] is True and plan['testOwnSecureRandomFixtureBytesGenerated'] is True and plan['realRuntimeCredentialOrKeyLoaded'] is False and plan['syntheticRetirementCallbacksInvoked'] is False and plan['actualGetentOrSystemctlInvoked'] is False and plan['actualProcRead'] is False,'fresh whole review and independent module declaration')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update((path.as_posix().split('/src/test/java/',1)[1][:-5].replace('/','.'),m) for m in methods)
    require(len(expected)==20 and not expected&{(v['classname'],v['name']) for v in old['cases']},'seven fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==20 and set(actual)==expected,'all seven actual original cases')
    oracle_groups={"DB193":["InspectorDbCredentialTest",["List.of(\"A\", \" ASCII \",","\"x\".repeat(65536)","List.of(\"\", \"\\n\", \"\\r\\n\")","assertArrayEquals(value.toCharArray(), actual)"]],"DB194":["InspectorDbCredentialTest",["new byte[65537]","new byte[] {(byte) 0xc0, (byte) 0xaf}","List.of(\"\\n\", \"\\r\\n\", \"\\ufeffx\",","assertArrayEquals(new byte[bytes.length], bytes)"]],"DB195":["InspectorDbCredentialTest",["assertNotSame(first, second)","assertArrayEquals(new char[] {65, 66, 67}, second)","assertEquals(\"InspectorDbCredential[REDACTED]\", material.toString())","assertNull(failure.getCause())"]],"DB196":["InspectorDbCredentialTest",["Executors.newFixedThreadPool(12)","for (int i = 0; i < 100; i++)","var closing = pool.submit(material::close)","closing.get(5, TimeUnit.SECONDS)","assertThrows(IllegalStateException.class, material::copyPassword)"]],"AES105":["InspectorAesCredentialTest",["List.of(\"v\", \"Abcdef0123456789\", \"v1-._test\", \"9\")","assertArrayEquals(expected, copy)","assertArrayEquals(new byte[input.length], input)"]],"AES106":["InspectorAesCredentialTest",["new int[] {0, 1, 7, 53, 70, 1000}","for (int position = 0; position < 7; position++)","Arrays.copyOf(base, base.length - 1)","bom[0] = (byte) 0xef"]],"AES107":["InspectorAesCredentialTest",["\"abcdefghijklmnopq\"","\"あ\",","\"é\")) bad(envelope(version, key))","input[8] = (byte) 0xff"]],"AES108":["InspectorAesCredentialTest",["new int[] {0, 1, 30, 31, 33, 34, 64}","assertEquals(0, index % 4)","alphabet.charAt(index + 1)","bad(unpadded)"]],"AES109":["InspectorAesCredentialTest",["Arrays.fill(input, (byte) 'Z')","assertNotSame(first, second)","assertArrayEquals(expected, second); // caller owns it"]],"AES110":["InspectorAesCredentialTest",["assertFalse(material.toString().contains(encoded))","assertEquals(\"inspector AES credential is closed\", error.getMessage())","\"InspectorAesCredential[version=v1, key=<redacted>, closed=true]\""]],"AES111":["InspectorAesCredentialTest",["synchronized (material)","pool.submit(material::copyKey).get(5, TimeUnit.SECONDS)","var start = new CountDownLatch(1)","start.countDown()","material.close()"]],"AES112":["InspectorAesCredentialTest",["InspectorAesCredential.consume(null)","input[10] = '?'","assertFalse(error.toString().contains(encoded))","assertEquals(0, error.getSuppressed().length)"]],"ACL113":["InspectorCredentialAccessTest",["new long[] {1, UID, 0xffff_fffeL}","new long[] {54, 55, 69}","new int[] {1, 2, Integer.MAX_VALUE}"]],"ACL114":["InspectorCredentialAccessTest",["access.requireAesFile(0100400, uid, 1, 54, true, new byte[0])","access.requireDirectory(040500, uid, 1, true, new byte[0])","invalid(() -> access.requireDirectory(040500, uid, 1, false, new byte[0]))"]],"ACL115":["InspectorCredentialAccessTest",["for (int bit = 0; bit < 32; bit++)","0100440 ^ difference","040550 ^ difference"]],"ACL116":["InspectorCredentialAccessTest",["new long[] {Long.MIN_VALUE, -1, 0, 0xffff_ffffL, Long.MAX_VALUE}","new long[] {Long.MIN_VALUE, -1, 0, 53, 70, Long.MAX_VALUE}"]],"ACL117":["InspectorCredentialAccessTest",["for (int bit = 0; bit < original.length * 8; bit++)","changed[bit / 8] ^= (byte) (1 << (bit % 8))","extraUser[44] = 8","System.arraycopy(original, 4, swapped, 12, 8)"]],"ACL118":["InspectorCredentialAccessTest",["policy.requireAesFile(0100440, 0, 1, 54, true, null)","assertArrayEquals(before, acl)","Arrays.fill(acl, (byte) 0)","invalid(() -> check(directory, new byte[44]))"]],"ACL119":["InspectorCredentialAccessTest",["for (int i = 1; i <= 100; i++)","golden(uid + 1, true)","check(false, golden(UID, false))"]],"ACL120":["InspectorCredentialAccessTest",["byte[] wrong = golden(1001, false)","new int[] {22, 38}","assertArrayEquals(before, wrong)","assertEquals(0, error.getSuppressed().length)"]]}
    for label,(owner,tokens) in oracle_groups.items():
        require(all(token in texts[owner] for token in tokens),'independent original control/identity/role/close oracle '+label)
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((3,111),(1,21),(0,3),(6,78))
    units={original.NAME:counts((0,37),(0,6),(0,1),(0,28)),original.PREFIX+'InspectorAesCredential':counts((0,44),(0,8),(0,1),(0,22)),original.PREFIX+'InspectorCredentialAccess':counts((3,30),(1,7),(0,1),(6,28))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=20,suites=3,newTestIds=0,cases=raw['cases'],targetSourceUnits=3,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=True,publicDigestOnly=False,publicSyntheticUuidFixture=False,ownThreadCount=None,declaredOwnPlatformThreadCount=36,declaredMaximumVirtualDrainWorkerCount=0,actualVirtualDrainWorkerCount=0,ownVirtualDrainWorkersInvoked=False,testOwnJavaMonotonicClockRead=False,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=False,declaredOwnExecutorInstances=3,declaredOwnTaskCount=502,syntheticJdbcPortsOnly=False,syntheticJdbcApiCallsInvoked=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=True,testOwnSecureRandomFixtureBytesGenerated=True,realRuntimeCredentialOrKeyLoaded=False,callerResourcesClosedByProduct=False,actualGetentOrSystemctlInvoked=False,actualProcRead=False,actualHookRegistrationOrRemovalInvoked=False,actualNativeHookOrProviderOperation=False,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=False,syntheticArchiveCallbacksInvoked=False,syntheticRetirementCallbacksInvoked=False,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==2 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==0,'two four100 and no natural-zero Source')
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewBindingSha256=PLAN[1],tests=20,suites=3,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=3,newPhysicalClasses=3,metadataPhysicalClasses=0,targetSourceUnitsMeasured=3,targetPhysicalClassesMeasured=3,existingSourceProofMustBeRetained=True,four100SourceProgramsMeasured=2,naturalZeroBranchSourceProgramsMeasured=0,partialSourceProgramsMeasured=1,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
