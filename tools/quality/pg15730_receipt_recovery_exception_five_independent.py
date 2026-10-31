"""Independent memory-failure recovery arithmetic and bounded exception values; no crypto or DB."""
import copy
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15726_receipt_recovery_exception_five_pt as original
import pg15728_receipt_recovery_exception_five_post as post
PIN='11c9220756ed22e23d11756e707d33607c0dd2f9c392b258228c76cccebdcad6'
OUT=data.BASE/'PG15730-receipt-recovery-exception-five-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in group) for n,group in original.CLOSURES.items()}
PHYSICAL=set().union(*map(set,CLOSURES.values()))
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/raw')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(5,2,5,2),'actual whole5/two')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualExit','failures','errors','skipped','reruns','newTestIds','newAccepted','crcMismatch','actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted']),'true zero roles')
    require(len({(c['classname'],c['name']) for c in p['cases']})==5 and all(c['result']=='PASS' for c in p['cases']),'all unique passes')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one original session')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==PHYSICAL,'whole outer/Reason denominator')
    require(p['metadataClasses']==[] and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True and all(any(m['hasCode'] for m in v['methods']) for v in p['sourcePhysicalInventory'].values()),'two genuine Code classes')
    totals={k:{r:sum(v['counters'][k][r] for v in p['executable'].values()) for r in ['covered','missed']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(covered=c,missed=0) for k,c in [('LINE',11),('METHOD',4),('CLASS',2),('BRANCH',0)]},'independent all applicable counters')
    u=p['fullSourceUnits'][P+'idempotency/ResponseSnapshotException']
    require(u['physical']==CLOSURES[P+'idempotency/ResponseSnapshotException'] and u['totals']==totals and u['branchNaturallyZero'] is u['threeCounter100'] is True and u['four100'] is False,'natural B0 with LMC100, not fake fourth100')
    require(p['naturalZeroBranch'] is p['allMeasuredApplicableCountersCovered'] is True and p['branchPercent'] is None and p['strictFour100GateExit']==1 and p['targetUnitFour100'] is False,'N/A branch explicit')
    require(p['onlyReviewedMemoryRecoveryAndValueSuites'] is p['ownedWorkerMemoryOnly'] is p['previousHelpersNotReaccepted'] is True and p['questionReceiptFactoryCreateInvoked'] is False and wire(p['helperPreviousSourceProofs'])==wire(expected_helpers),'old three full proof/counter preserved without replacement')
    require(p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY' and all(p[k] is False for k in ['cryptoOrKeyOperationsInvoked','publicSyntheticTestKeysUsed','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualJdbcBackendConnected','actualJdbcProxyObjectsConstructed','actualBrokerOrListenerStarted','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused']),'no live/crypto/old transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualBrowserActions','actualBoundSockets','actualJmsConnectionsCreated','actualJmsContextsCreated','forbiddenProductProbeHits','productTestsReexecutedByPost']) and p['effortPercent'] is None,'no target actions')
    require(len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(v[3]=='0' for v in p['passiveNativeBoundaryAbsence']['rows']) and all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual passive terminal')
    require(len(p['owners'])==6 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==4 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==2,'four Main owner rows, two UNKNOWN Tests')
def main():
    global raw,expected_helpers
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15726-receipt-recovery-exception-five-pt-v1/manifest.json',post.RAW)
    old=data.read_checked(data.BASE/'PG15716-current2004-caddy-values-registry-v1/manifest.json','303896c2bf9a0738a00a8c3af8a23d23387dd7d31c1852593009fd609a45ba5d')
    expected_helpers={P+n:old['fullSourceUnits'][P+n] for n in original.SUPPORT_PINS}
    require(len(expected_helpers)==3 and all(v['four100'] is True for v in expected_helpers.values()) and not set(CLOSURES)&set(old['fullSourceUnits']),'only one new Source, old helpers full-qualified')
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    expected=set()
    for name,path in original.TESTS.items():
        text=path.read_text();package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);methods=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text)
        require(len(methods)==original.COUNTS[name] and not any(v in text for v in ['Files.','ProcessBuilder','FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException','new SecureRandom','QuestionReceiptIdGenerator.create(','DriverManager','getConnection(','HttpClient']),'whole safe original bodies')
        expected.update((package+'.'+name,v) for v in methods)
    require(expected=={(c['classname'],c['name']) for c in p['cases']} and not expected&{(c['classname'],c['name']) for c in old['cases']},'all five new original cases')
    t=original.TESTS['QuestionReceiptRecoveryTest'].read_text();e=original.TESTS['ExceptionValueContractTest'].read_text()
    alphabet='0123456789ABCDEFGHJKMNPQRSTVWXYZ';tail=''.join(alphabet[n%32] for n in range(14,40))
    require(len(alphabet)==len(set(alphabet))==32 and tail=='EFGHJKMNPQRSTVWXYZ01234567' and tail in t,'independent supplied-position vector')
    require(all(v in t for v in ['position < 26','position + 1','position + 27','-1, 32, Integer.MIN_VALUE, Integer.MAX_VALUE','PARTIAL_FAILURE_DRAW = 13','LAST_FAILURE_DRAW = 25','assertEquals(14, draws.get())','assertEquals(40, draws.get())','assertEquals(52, draws.get())','assertEquals(0, failure.getSuppressed().length)','newSingleThreadExecutor()','get(5, TimeUnit.SECONDS)','ZERO_VECTOR = "00000000000000000000000000"','LAST_VECTOR = "ZZZZZZZZZZZZZZZZZZZZZZZZZZ"']),'26 positions/four invalid/tail/error/owned worker literal matrix')
    states={'MESSAGE_ID_REUSE':'23000','OPERATION_TOKEN_REUSE':'23000','FINGERPRINT_KEY_UNAVAILABLE':'55000','STATE_CORRUPT':'XX000','TRANSACTION_REQUIRED':'25000'}
    require(all(re.search('"'+name+r'"\s*,\s*"'+value+'"',e) for name,value in states.items()) and all(v in e for v in ['assertNull(plain.getCause())','assertSame(cause, caused.getCause())','new ResponseSnapshotException(null, "bounded")','new ResponseSnapshotException(null, "bounded", null)']),'independent five SQLSTATEs and shallow exception/null contract')
    design='documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md';design_bytes=(data.ROOT/design).read_bytes()
    require(design_bytes==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT) and '| '+chr(96)+'receipt_id'+chr(96)+' | char(26)' in design_bytes.decode() and '^[0-9A-HJKMNP-TV-Z]{26}$' in design_bytes.decode(),'approved receipt26 alphabet/UK, no DB operation')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('tests','tests',6),('suites','suites',3),('physical','physicalClasses',{}),('units','fullSourceUnits',{}),('executable','executable',{}),('totals','totals',{}),('metadata','metadataClasses',['X']),('exclude','manualCounterExclusions',['X']),('filter','officialGeneratedFiltersUnchanged',False),('crc','crcMismatch',1),('single','singleSession',False),('session','sessionIdentity','OLD'),('natural','naturalZeroBranch',False),('branch-percent','branchPercent',100),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('helpers','helperPreviousSourceProofs',{}),('factory','questionReceiptFactoryCreateInvoked',True),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('auth','actualAuthenticationOrSessionIssued',True),('jdbc','actualJdbcMethodsInvoked',1),('root','rootMainInvoked',True),('formal','formalUpdated',True),('union','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-zero','newAccepted',False),('effort','effortPercent',100),('owners','owners',{})]
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false recovery/value qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=5,suites=2,sourcePrograms=1,newSourcePrograms=1,physicalClasses=2,executablePhysicalClasses=2,metadataPhysicalClasses=0,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=0,baselineMainOwnerRows=4,unknownTestOwnerRows=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentRecoveryTail=tail,independentFailureDraws=list(range(26)),independentInvalidIndices=[-1,32,-2147483648,2147483647],independentSqlStates=states,previousHelperProofs=expected_helpers,previousHelpersNotReaccepted=True,approvedDesignHashes={design:data.sha(design_bytes)},cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,questionReceiptFactoryCreateInvoked=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=5,semanticNegativeVectors=len(labels),sourcePrograms=1,naturalBranchNA=True)))
if __name__=='__main__':main()
