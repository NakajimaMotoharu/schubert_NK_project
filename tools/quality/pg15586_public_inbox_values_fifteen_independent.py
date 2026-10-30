"""Independent Python LP/NFC/HMAC/frame and full14Source metadata proof for original Inbox15."""
import copy
import hashlib
import json
import re
import struct
import subprocess
import hmac
import ssl
import sys
import unicodedata
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15582_public_inbox_values_fifteen_pt as original
import pg15584_public_inbox_values_fifteen_post as post

PIN='2a3c1dd5f8929a0ee1fffddc37072fb96c5f7fdf2f4a5cf3f7fd2ce524dbad42'
OUT=data.BASE/'PG15586-public-inbox-values-fifteen-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15586-public-inbox-values-fifteen-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted([P+n,*([P+n+'$Reason'] if n=='idempotency/InboxException' else [])]) for n in original.MAIN_PINS}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(15,4,15,4) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'exact pass')
    require(len({(c['classname'],c['name']) for c in p['cases']})==15 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'all four target Source/sixCode; no helper transfer')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'Code/filter')
    require(all(any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']) for n in NAMES),'actual Code')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={'LINE':{'covered':243,'missed':36},'METHOD':{'covered':52,'missed':7},'CLASS':{'covered':15,'missed':0},'BRANCH':{'covered':104,'missed':9}},'same exec measured counters')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==sorted(ns) and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is (values['BRANCH']==dict(missed=0,covered=0)),'independent per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and sum(u['four100'] for u in p['fullSourceUnits'].values())==9,'three four100/one gap')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is True and p['cryptoOperationKind']=='HMACSHA256_PUBLIC_SYNTHETIC_TEST_KEYS_ONLY','truthful public synthetic crypto')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is p['onlySyntheticJmsProxyMessages'] is p['jmsDestinationValueObjectsConstructed'] is False,'no live/private/JMS actions')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'no broker')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absences')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no old/formal/effort transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==18 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==14 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==4,'actual ownership')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'genuine stages')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15582-public-inbox-values-fifteen-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15572-current1879-public-session-codec-registry-v1/manifest.json','00dabafe1bbb8737a0ea9dc908f98e16c46a2743100d21164020f841082ef4d5')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'all14 new target Source disjoint')
    texts={k:path.read_text() for k,path in original.TESTS.items()}
    require(all(not re.search(r'\b'+name+r'\s*\(',t) for t in texts.values() for name in ['createConnection','createContext','getConnection','startServer']),'only values/owned memory/no DB')
    require(p['ownedJcaProviderOrderRestored'] is True,'same owned JVM provider order restored')
    expected=set()
    for key,path in original.TESTS.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',texts[key]);require(len(names)==original.COUNTS[key],'whole original discovery')
        package=re.search(r'package ([A-Za-z0-9_.]+);',texts[key]).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every original method exactly once')
    fingerprint=texts['OperationFingerprintTest'];buffer=texts['SecretBufferTest'];scope=texts['QuestionQueryScopeFrameTest'];models=texts['InboxModelTest']
    def lp(text):
        value=unicodedata.normalize('NFC',text).encode('utf-8');return struct.pack('>I',len(value))+value
    def canonical(owner,layout,version,target,fields):
        result=b'SCHUBERT-NK-OP1'+b''.join(lp(v) for v in [owner,layout,version,target])+struct.pack('>I',len(fields))
        for name,kind,value in fields:result+=lp(name)+lp(kind)+(struct.pack('>I',0xffffffff) if value is None else struct.pack('>I',len(value))+value)
        return result
    golden=canonical('7','QSTREQ01','001','QUESTION:7',[('title','X1',None),('body','X1',b'')])
    block=re.search(r'GOLDEN_CANONICAL\s*=\s*(.*?);',fingerprint,re.S).group(1)
    literal=''.join(re.findall(r'"([0-9a-f]+)"',block))
    golden_hmac=hmac.new(bytes(range(32)),golden,hashlib.sha256).hexdigest()
    require(golden.hex()==literal and golden_hmac=='605896204af0c777ef2911589343b4e4a50cd7aa87560662a5f634249240be81' and golden_hmac in fingerprint,'independent SS324 canonical/HMAC fixed golden')
    require(canonical('u\u0308ser','QSTREQ01','001','cafe\u0301',[('value','X1','e\u0301'.encode())])==canonical('\u00fcser','QSTREQ01','001','caf\u00e9',[('value','X1','e\u0301'.encode())]),'independent NFC text equivalence')
    require(canonical('7','QSTREQ01','001','QUESTION:7',[('v','X1',None)])!=canonical('7','QSTREQ01','001','QUESTION:7',[('v','X1',b'')]),'independent null/empty separation')
    wipe_canonical=canonical('ANONYMOUS','LGNREQ01','001','LOGIN:synthetic',[('password','X1',bytes([1,2,3])),('absent','X1',None),('empty','X1',b'')])
    wipe_hmac=hmac.new(bytes(32),wipe_canonical,hashlib.sha256).hexdigest()
    require(all(v in buffer for v in ['new byte[8192]','new int[] {0, 8191, 8192, 8193, 1_050_000}','new byte[1_050_001]','new byte[] {1, 2, 3}','out.writeInt(-1)','out.writeInt(0)','mac.doFinal(buffer.toByteArray())','assertArrayEquals(new byte[original.length], original)','assertArrayEquals(new byte[expanded.length], expanded)']),'independent bounded memory/ownership oracle')
    frames={role:(bytes.fromhex('4e4b5152593100')+bytes([tag])+b' '*256) for role,tag in [('USER',85),('ADMIN',65)]}
    require(all(len(v)==264 for v in frames.values()) and all(v in scope for v in ['4e4b515259310055','4e4b515259310041','assertNotSame(old, inspected)','new int[] {0, 6, 7, 8, 263}','"NTSRSP01", "NTDRSP01", "USRRSP01"','QUESTION_LIST_RESPONSE_LAYOUT, "002"']),'independent SSC157 role frame/closed inspection routes')
    sql_states={'MESSAGE_ID_REUSE':'23000','OPERATION_TOKEN_REUSE':'23000','FINGERPRINT_KEY_UNAVAILABLE':'55000','STATE_CORRUPT':'XX000','TRANSACTION_REQUIRED':'25000'}
    require(all('assertException(InboxException.Reason.'+k+', "'+v+'")' in models for k,v in sql_states.items()),'five bounded SQLSTATE values, not actual SQL')
    require(all(v in models for v in ['999_999_999_999L','1_000_000_000_000L','OptionalLong.of(0)','InboxExecutionStatus.IN_PROGRESS','InboxResultReferenceType.AUTH_SESSION']),'independent N12/reference/outcome null boundary matrix')
    docs=['documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md','documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(content==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,content in documents.items()),'approved main design bytes')
    require(all(v in documents[docs[0]].decode() for v in ['SCHUBERT-NK-OP1','NFC後UTF-8','0xFFFFFFFF','U32(field count)','LP(canonical field bytes)']) and all(v in documents[docs[1]].decode() for v in ['NKQRY1','4e4b5152593100']),'independent approved canonical/frame format')
    negative=[]
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('source-units','fullSourceUnits',{}),('tests','tests',16),('suites','suites',5),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic','publicSyntheticTestKeysUsed',False),('jca-restore','childLocalJcaRegistryRestorationTested',False),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old-transfer','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError('false current qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=15,suites=4,sourcePrograms=14,physicalClasses=15,four100SourcePrograms=9,naturallyBranchZeroSourcePrograms=3,incompleteSourcePrograms=2,baselineMainOwnerRows=14,unknownTestOwnerRows=4,semanticNegativeVectors=len(negative),negativeLabels=negative,independentCanonicalHex=golden.hex(),independentHmacHex=golden_hmac,independentWipeHmacHex=wipe_hmac,independentFrameHashes={k:data.sha(v) for k,v in frames.items()},independentSqlStates=sql_states,pythonVersion=sys.version,pythonOpenSslVersion=ssl.OPENSSL_VERSION,approvedDesignHashes={v:data.sha(content) for v,content in documents.items()},ownedJcaProviderOrderRestored=True,cryptoOrKeyOperationsInvoked=True,publicSyntheticTestKeysUsed=True,cryptoOperationKind=p['cryptoOperationKind'],childLocalJcaRegistryRestorationTested=True,ownFreshJvmProviderStateOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,onlySyntheticJmsProxyMessages=False,jmsFactoryObjectsConstructed=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,previousHelpersNotReaccepted=True,roleReferenceOnly=True,onlySelfOwnedPublicBuffersInspected=True,actualHeapDumpActions=0,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=15,semanticNegativeVectors=len(negative),hmac=golden_hmac)))
if __name__=='__main__':main()
