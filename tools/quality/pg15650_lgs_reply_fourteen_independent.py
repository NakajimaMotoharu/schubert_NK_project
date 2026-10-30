"""Independent UI byte offsets/LOG and QSB fixed wire vectors, genuine full Source metadata."""
import copy
import hashlib
import json
import re
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15646_lgs_reply_fourteen_pt as original
import pg15648_lgs_reply_fourteen_post as post

PIN='0580200b2aed01476d1e95274c7ac6be29708ea822542a56f6bcf4a4978df705'
OUT=data.BASE/'PG15650-lgs-reply-fourteen-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in values) for n,values in original.CLOSURES.items()}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(14,2,14,2) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'genuine nine')
    require(len({(c['classname'],c['name']) for c in p['cases']})==14 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'whole four Source/seven Code')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no exclusion')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(missed=0,covered=v) for k,v in [('LINE',79),('METHOD',15),('CLASS',3),('BRANCH',38)]},'independent exact sums')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==ns and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is (values['BRANCH']==dict(missed=0,covered=0)) and u['threeCounter100'] is True,'actual per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and p['allMeasuredApplicableCountersCovered'] is True and sum(u['four100'] for u in p['fullSourceUnits'].values())==1,'two branchless not fake four100')
    require(p['cryptoOrKeyOperationsInvoked'] is True and p['cryptoOperationKind']=='MESSAGEDIGEST_ISEQUAL_PUBLIC_SYNTHETIC_CONTEXT_TEXT_ONLY' and p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is False and p['ownedJcaProviderOrderRestored'] is None,'truthful SHA comparison only')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is False,'no live/private IO')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False and p['onlySyntheticJmsProxyMessages'] is p['jmsDestinationValueObjectsConstructed'] is True,'no broker/only proxy and destination values')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absence')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no transfer/acceptance')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==5 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==3 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==2,'actual owners')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual stage terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15646-lgs-reply-fourteen-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15637-current1936-protected-facades-registry-v2/manifest.json','9fa92ea73d1b63854242560dcc2902a71f09fb4041bf8263fa9470ddd0c6c972')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'new four Source, no old helper reacceptance')
    texts={k:path.read_text() for k,path in original.TESTS.items()};expected=set()
    for key,text in texts.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text);require(len(names)==original.COUNTS[key],'whole original counts')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every whole original once')
    lgs=texts['LogSearchWireClientTest'];reply=texts['JmsReplyDecoderTest']
    docs=['documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md','documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md','documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(value==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,value in documents.items()),'approved main bytes')
    require(all(v in documents[docs[1]].decode() for v in ['LGSREQ01','data（656 byte）','LGSRSP01','data（48 byte）','record（2,088 byte、最大100件）']),'independent approved size/count')
    section=documents[docs[1]].decode().split('### 11.1',1)[1].split('### 11.2',1)[0]
    rows=re.findall(r'^\| ([^|]+) \| ([\d,]+) \| ([\d,]+) \|',section,re.M)
    offsets=[(int(start.replace(',',''))-1,int(width.replace(',',''))) for _,start,width in rows]
    require(offsets==[(0,256),(256,16),(272,64),(336,256),(592,8),(600,17),(617,17),(634,6),(640,3),(643,13)] and sum(v for _,v in offsets)==656,'all10 LGS request offsets independent UI')
    require(256+656==912 and 256+48+2088*100==209104 and all(v in lgs for v in ['656, 0, 0','48, 2088','new int[] {0, 1, 100}','new int[] {0, 255, 303, 209105}','Arrays.fill(b, 113, 177','input().data()','List.of(new SpeakerRecord','number(expected, 890, 6, 1)','number(expected, 896, 3, 100)','64, observed.size()','assertArrayEquals(original, caller)']),'original max/boundary/added auth-record vectors retained')
    require(all(v in reply for v in ['new byte[280]','Arrays.copyOf(responseWire(), 320)','ascii(expected, 11, "QSBRSP01")',"expected[23] = 'A'",'new char[] {\'S\', \'I\'}','1_000_001L','BODY_LENGTH_FIELD, -1L','BODY_FIELD, null','new ActiveMQTemporaryQueue()','nk.sync.reply.web::nk.sync.reply.web.q','nk.sync.reply.web::unapproved.q','::unapproved.q','JMSXDeliveryCount','DeliveryMode.NON_PERSISTENT','providerBody[0] = 9','returned[1] = 9']),'independent provider/body/route/property/clone matrix')
    def write(body,offset,value):
        value=value.encode('ascii');body[offset:offset+len(value)]=value
    request_id='00000000-0000-0000-0000-000000000001';response_id='00000000-0000-0000-0000-000000000002'
    body=bytearray(b' '*280)
    pairs=[(0,'SCHBNK01'),(8,'001'),(11,'LOGRSP01'),(19,'001'),(22,'S'),(23,'S'),(24,response_id),(60,request_id),(96,'20260903120000000'),(113,'a'*64),(177,'0256'),(181,'000024'),(187,'000000'),(193,'000000'),(199,'000000280'),(208,'0000')]
    for offset,value in pairs:write(body,offset,value)
    require(len(body)==280 and body[212:]==b' '*68 and int(body[199:208])==len(body) and body[24:60]!=body[60:96],'independent exact LOG fixed vector')
    qsb=body[:256]+bytearray(b' '*64)
    for offset,value in [(11,'QSBRSP01'),(23,'A'),(181,'000064'),(199,'000000320'),(256,'0'*26),(282,'000000000001'),(294,'20260903120000000')]:write(qsb,offset,value)
    require(len(qsb)==320 and int(qsb[199:208])==320 and qsb[22:24]==b'SA' and qsb[311:]==b' '*9,'independent exact registered QSB async reply')
    require('registry-valid QSB S/A' in documents[docs[2]].decode() and 'JMSCorrelationID' in documents[docs[0]].decode(),'approved QSB and identity contract')
    wire_vectors={'LOGRSP01':dict(length=len(body),sha256=hashlib.sha256(body).hexdigest()),'QSBRSP01':dict(length=len(qsb),sha256=hashlib.sha256(qsb).hexdigest())}
    helpers={name:old['fullSourceUnits'][P+'messaging/'+name] for name in ['ProtectedReadWireClient','ProtectedReadWireException','JmsRequestReplyClient','ReplyCorrelationRegistry']}
    require(all(u['post'] in ['PG14314-web-business-wire-whole-twelve-post-v1','PG14318-web-memory-coordinator-whole-seventeen-post-v1','PG14788-web-messaging-exception-three-post-v1'] for u in helpers.values()),'existing helpers unchanged/not accepted by target')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('sources','fullSourceUnits',{}),('tests','tests',15),('suites','suites',3),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic-key','publicSyntheticTestKeysUsed',True),('jca','childLocalJcaRegistryRestorationTested',True),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    require(all(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True) for _,key,value in vectors),'each negative differs from genuine value')
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=14,suites=2,sourcePrograms=3,physicalClasses=3,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=2,incompleteSourcePrograms=0,baselineMainOwnerRows=3,unknownTestOwnerRows=2,semanticNegativeVectors=len(labels),negativeLabels=labels,independentLgsRequestOffsets=offsets,independentReplyVectors=wire_vectors,nondegenerateNegativeVectors=len(vectors),previousHelperProofs=helpers,onlySyntheticJmsProxyMessages=True,jmsDestinationValueObjectsConstructed=True,pythonVersion=sys.version,approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],publicSyntheticTestKeysUsed=False,childLocalJcaRegistryRestorationTested=False,ownFreshJvmProviderStateOnly=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,previousHelpersNotReaccepted=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=14,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()
