"""Independent approved Login/probe byte fields and synthetic local authentication contracts."""
import copy
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15742_mq_login_memory_fourteen_pt as original
import pg15744_mq_login_memory_fourteen_post as post
PIN='8778a987b1616cd6ab2b6d998202e0ebefb54762f62a32a13b5c9785a2aa77d9'
OUT=data.BASE/'PG15746-mq-login-memory-fourteen-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in group) for n,group in original.CLOSURES.items()}
PHYSICAL=set().union(*map(set,CLOSURES.values()))
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/raw')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(14,3,14,3),'actual whole5/two')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualExit','failures','errors','skipped','reruns','newTestIds','newAccepted','crcMismatch','actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted']),'true zero roles')
    require(len({(c['classname'],c['name']) for c in p['cases']})==14 and all(c['result']=='PASS' for c in p['cases']),'all unique passes')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one original session')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==PHYSICAL,'whole outer/Reason denominator')
    require(p['metadataClasses']==[] and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True and all(any(m['hasCode'] for m in v['methods']) for v in p['sourcePhysicalInventory'].values()),'two genuine Code classes')
    totals={k:{r:sum(v['counters'][k][r] for v in p['executable'].values()) for r in ['covered','missed']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(covered=c,missed=0) for k,c in [('LINE',176),('METHOD',24),('CLASS',5),('BRANCH',76)]},'independent all applicable counters')
    require(all(type(v) is int for row in p['executable'].values() for counter in row['counters'].values() for v in counter.values()),'typed physical counters')
    for name,names in CLOSURES.items():
        u=p['fullSourceUnits'][name];expected={k:{r:sum(p['executable'][n]['counters'][k][r] for n in names) for r in ['missed','covered']} for k in totals}
        require(u['physical']==names and u['totals']==expected and u['four100'] is u['threeCounter100'] is True and u['branchNaturallyZero'] is False and all(v['missed']==0 and v['covered']>0 for v in expected.values()),'four whole sources all actual four100')
    require(p['naturalZeroBranch'] is False and p['allMeasuredApplicableCountersCovered'] is True and p['branchPercent']==100 and p['strictFour100GateExit']==0 and p['targetUnitFour100'] is True,'actual complete four counters')
    require(p['onlySyntheticLoginMemoryContracts'] is p['publicSyntheticFixtureCredentialsUsed'] is p['syntheticLocalSpringAuthenticationObjectsCreated'] is p['numericIpLiteralParsingOnly'] is p['previousHelpersNotReaccepted'] is True and p['syntheticCredentialsRenderedOrPersisted'] is p['valueBearingWireSaved'] is p['actualDnsRequestsIssued'] is False,'public synthetic memory objects not actual credential/session authority')
    require(p['actualAuthenticationOrSessionIssuedDomain']=='DEPLOYED_API_OR_HTTP_SESSION_AUTHORITY_NOT_SYNTHETIC_SPRING_OBJECTS' and p['actualCredentialValuesUsedDomain']=='DEPLOYED_OR_USER_SECRET_VALUES_NOT_PUBLIC_TEST_FIXTURES' and all(type(p[k]) is int and p[k]==0 for k in ['actualHttpSessionsIssued','actualApiAuthenticationGrantsIssued','actualJmsMessagesSentToBroker']),'actual authority zero distinct from local Spring projection')
    require(wire(p['helperPreviousSourceProofs'])==wire(expected_helpers),'all five prior helper proofs unchanged')
    require(p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY' and all(p[k] is False for k in ['cryptoOrKeyOperationsInvoked','publicSyntheticTestKeysUsed','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualJdbcBackendConnected','actualJdbcProxyObjectsConstructed','actualBrokerOrListenerStarted','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused']),'no live/crypto/old transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualBrowserActions','actualBoundSockets','actualJmsConnectionsCreated','actualJmsContextsCreated','forbiddenProductProbeHits','productTestsReexecutedByPost']) and p['effortPercent'] is None,'no target actions')
    require(len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(v[3]=='0' for v in p['passiveNativeBoundaryAbsence']['rows']) and all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual passive terminal')
    require(len(p['owners'])==12 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==9 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==3,'four Main owner rows, two UNKNOWN Tests')
def main():
    global raw,expected_helpers
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15742-mq-login-memory-fourteen-pt-v1/manifest.json',post.RAW)
    old=data.read_checked(data.BASE/'PG15732-current2009-recovery-values-registry-v1/manifest.json','66b317c50586b44e39d8a7b7e0f175184d151554c7e7d2c9bfb0d3650e6c7bfa')
    expected_helpers={P+n:old['fullSourceUnits'][P+n] for n in original.SUPPORT_PINS}
    require(len(expected_helpers)==5 and all(v['four100'] is True or v['branchNaturallyZero'] is True for v in expected_helpers.values()) and not set(CLOSURES)&set(old['fullSourceUnits']),'only one new Source, old helpers full-qualified')
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    expected=set()
    for name,path in original.TESTS.items():
        text=path.read_text();package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);methods=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text)
        require(len(methods)==original.COUNTS[name] and not any(v in text for v in ['Files.','ProcessBuilder','FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException','new SecureRandom','QuestionReceiptIdGenerator.create(','DriverManager','getConnection(','HttpClient']),'whole safe original bodies')
        expected.update((package+'.'+name,v) for v in methods)
    require(expected=={(c['classname'],c['name']) for c in p['cases']} and not expected&{(c['classname'],c['name']) for c in old['cases']},'all five new original cases')
    texts={name:path.read_text() for name,path in original.TESTS.items()}
    client=texts['MqLoginClientTest'];probe=texts['MqLoginContextProbeTest'];provider=texts['MqAuthenticationProviderTest']
    golden=client[client.index('  private static byte[] request('):client.index('  private static final class FaultClock')]
    require(not any(v in golden for v in ['HeaderCodec','PayloadCodec','PayloadTypeCatalog','MqLoginClient','MqAuthenticationProvider','JmsRequestReplyClient']),'golden body independent of Product methods')
    for value in ['256, username','320, password','576, address','325, context','389, "20260908090000123"','406, "20260908170000123"','put(body, 208, code)','0256%06d000000000000%09d']:
        require(value in golden,'literal independent wire offset '+value)
    require(all(v in client for v in ['Duration.ofNanos(1)','Thread.interrupted()','assertEquals(0, client.pendingCount())','sends.get()','newFixedThreadPool(8)','index < 100','get(10, TimeUnit.SECONDS)','assertArrayEquals(new byte[640]','assertArrayEquals(new char[password.length]']),'input/null/fault/erasure and finite concurrent calls')
    require(all(v in probe for v in ['new int[] {0, 1, 10}','265 + 272 * count','put(body, 187, "000272")','0102','MALFORMED' if 'MALFORMED' in probe else 'corruptInvalid','assertArrayEquals(new byte[256]','Thread.interrupted()']),'probe record/count/context/invalid/erasure')
    require(all(v in provider for v in ['web065ReplayRequiresCurrentContextBeforeGrant','web066FailureAndNullTypesNeverBecomeAuthentication','assertEquals(45, longest.length())','new int[] {-1, 901}','DerivedToken.class','ROLE_ADMIN','assertNull(input.getCredentials())','assertEquals(200, fixture.ids.get())','fixture.closed()']),'local role/error/exact type/replay/current probe and buffer ownership')
    documents_list=['documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md','documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md']
    documents={name:(data.ROOT/name).read_bytes() for name in documents_list}
    require(all(content==subprocess.check_output(['git','show','origin/main:'+name],cwd=data.ROOT) for name,content in documents.items()),'approved exact UI bytes')
    header_proof=data.read_checked(data.BASE/'PG15634-protected-facades-twenty-four-independent-v1-independent-v1/manifest.json','2d2e1f2b4c800cb9f8083208c6a7c62a10d831622106e620f85eddb77344ce04')
    offsets=[[0,8],[8,3],[11,8],[19,3],[22,1],[23,1],[24,36],[60,36],[96,17],[113,64],[177,4],[181,6],[187,6],[193,6],[199,9],[208,4],[212,44]]
    require(header_proof['actualExit']==0 and header_proof['independentHeaderOffsets']==offsets and header_proof['approvedDesignHashes'][documents_list[0]]==data.sha(documents[documents_list[0]]) and offsets[-1][0]+offsets[-1][1]==256,'previous independent SS232 oracle reused, not old Product execution')
    ui=documents[documents_list[1]].decode();request_doc=ui.split('### 3.1 ')[1].split('### 3.2 ')[0];reply_doc=ui.split('### 3.2 ')[1].split('## 4. ')[0]
    request_fields=[('Username',1,64),('Password',65,256),('Client address',321,45),('Reserved',366,19)]
    reply_fields=[('Username',1,64),('Role',65,5),('認証context ID',70,64),('発行日時',134,17),('期限日時',151,17),('Retry after秒',168,6),('残り試行回数',174,3),('利用者message',177,256)]
    require(all('| '+name+' | '+str(start)+' | '+str(width)+' |' in doc for fields,doc in [(request_fields,request_doc),(reply_fields,reply_doc)] for name,start,width in fields),'approved exact data field widths/relative offsets')
    require(256+sum(v[2] for v in request_fields)==640 and 256+sum(v[2] for v in reply_fields)==688 and all(v in ui for v in ['data（9 byte）','record（272 byte、最大10件）']),'independent total lengths and GAM maximum')
    spec_path=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2997_Loginメモリ原十四_単体テスト仕様.md';spec=spec_path.read_text()
    def spec_contract(value):require('Client address45＋Reserved19' in value and '値長は45まで' in value and 'password256/IP64' not in value,'spec field45 not allocation64')
    spec_contract(spec)
    try:spec_contract(spec.replace('Client address45＋Reserved19','Client address64'))
    except ValueError:spec_negative=1
    else:raise ValueError('old width confusion accepted')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('tests','tests',15),('suites','suites',4),('physical','physicalClasses',{}),('units','fullSourceUnits',{}),('executable','executable',{}),('totals','totals',{}),('metadata','metadataClasses',['X']),('exclude','manualCounterExclusions',['X']),('filter','officialGeneratedFiltersUnchanged',False),('crc','crcMismatch',1),('single','singleSession',False),('session','sessionIdentity','OLD'),('natural','naturalZeroBranch',True),('branch-percent','branchPercent',None),('four','targetUnitFour100',False),('strict','strictFour100GateExit',1),('helpers','helperPreviousSourceProofs',{}),('real-session','actualHttpSessionsIssued',1),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('auth','actualAuthenticationOrSessionIssued',True),('jdbc','actualJdbcMethodsInvoked',1),('root','rootMainInvoked',True),('formal','formalUpdated',True),('union','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-zero','newAccepted',False),('effort','effortPercent',100),('owners','owners',{}),('synthetic-fixture','publicSyntheticFixtureCredentialsUsed',False),('spring-projection','syntheticLocalSpringAuthenticationObjectsCreated',False),('actual-grant','actualApiAuthenticationGrantsIssued',1),('fixture-persisted','syntheticCredentialsRenderedOrPersisted',True),('raw-wire','valueBearingWireSaved',True)]
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false recovery/value qualification '+label)
    bad=copy.deepcopy(p);next(iter(bad['executable'].values()))['counters']['LINE']['missed']=False
    try:assess(bad)
    except ValueError:labels.append('typed-counter')
    else:raise ValueError('boolean coverage counter accepted')
    verify(header_proof['invocation'])
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=14,suites=3,sourcePrograms=4,newSourcePrograms=4,physicalClasses=5,executablePhysicalClasses=5,metadataPhysicalClasses=0,four100SourcePrograms=4,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,baselineMainOwnerRows=9,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,specNegativeVectors=spec_negative,specSha256=data.sha(spec.encode()),independentHeaderOffsets=offsets,independentLoginRequestFields=request_fields,independentLoginResponseFields=reply_fields,previousHeaderOracleReference=['PG15634-protected-facades-twenty-four-independent-v1-independent-v1','2d2e1f2b4c800cb9f8083208c6a7c62a10d831622106e620f85eddb77344ce04'],goldenHelperBodySha256=data.sha(golden.encode()),goldenHelperUsesProduction=False,previousHelperProofs=expected_helpers,previousHelpersNotReaccepted=True,approvedDesignHashes={name:data.sha(content) for name,content in documents.items()},onlySyntheticLoginMemoryContracts=True,publicSyntheticFixtureCredentialsUsed=True,syntheticLocalSpringAuthenticationObjectsCreated=True,actualHttpSessionsIssued=0,actualApiAuthenticationGrantsIssued=0,actualJmsMessagesSentToBroker=0,actualDnsRequestsIssued=False,syntheticCredentialsRenderedOrPersisted=False,valueBearingWireSaved=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=14,semanticNegativeVectors=len(labels),sourcePrograms=4,four100Sources=4,specNegatives=spec_negative)))
if __name__=='__main__':main()
