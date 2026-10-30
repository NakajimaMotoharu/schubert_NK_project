"""Independent approved byte-offset vectors and full facade Source counters; no product execution."""
import copy
import hashlib
import json
import re
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15630_protected_facades_twenty_four_pt as original
import pg15632_protected_facades_twenty_four_post as post

PIN='ae77f8127ca5d1afacdace5b986aef4f1519d7c33e83fecbae551c8109566b64'
OUT=data.BASE/'PG15634-protected-facades-twenty-four-independent-v1-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in values) for n,values in original.CLOSURES.items()}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(24,3,24,3) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'genuine nine')
    require(len({(c['classname'],c['name']) for c in p['cases']})==24 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'whole four Source/seven Code')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no exclusion')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(missed=0,covered=v) for k,v in [('LINE',24),('METHOD',10),('CLASS',4),('BRANCH',0)]},'independent exact sums')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==ns and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is (values['BRANCH']==dict(missed=0,covered=0)) and u['threeCounter100'] is True,'actual per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and p['allMeasuredApplicableCountersCovered'] is True and sum(u['four100'] for u in p['fullSourceUnits'].values())==0,'two branchless not fake four100')
    require(p['cryptoOrKeyOperationsInvoked'] is True and p['cryptoOperationKind']=='MESSAGEDIGEST_ISEQUAL_PUBLIC_SYNTHETIC_CONTEXT_TEXT_ONLY' and p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is False and p['ownedJcaProviderOrderRestored'] is None,'truthful SHA comparison only')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is p['onlySyntheticJmsProxyMessages'] is False,'no live/private IO')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'no broker')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absence')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no transfer/acceptance')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==6 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==3 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==3,'actual owners')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'actual stage terminal')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15630-protected-facades-twenty-four-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15620-current1912-dlq-web-health-registry-v1/manifest.json','60495269d8b2f1ef5e0096b18a30f22806dcd145c755624c27ad75455f4859ce')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'new four Source, no old helper reacceptance')
    texts={k:path.read_text() for k,path in original.TESTS.items()};expected=set()
    for key,text in texts.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text);require(len(names)==original.COUNTS[key],'whole original counts')
        package=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every whole original once')
    documents_list=['documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md','documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md','documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md']
    documents={v:(data.ROOT/v).read_bytes() for v in documents_list}
    require(all(value==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,value in documents.items()),'approved main UI bytes')
    section=documents[documents_list[0]].decode().split('## 3.',1)[1].split('## 4.',1)[0]
    rows=re.findall(r'^\| (\d+) \| ([^|]+) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \|',section,re.M)
    expected_offsets=[(0,8),(8,3),(11,8),(19,3),(22,1),(23,1),(24,36),(60,36),(96,17),(113,64),(177,4),(181,6),(187,6),(193,6),(199,9),(208,4),(212,44)]
    offsets=[(int(start.replace(',',''))-1,int(width.replace(',',''))) for _,_,start,_,width in rows]
    require(offsets==expected_offsets and sum(width for _,width in offsets)==256 and all(int(end.replace(',',''))==int(start.replace(',',''))+int(width.replace(',',''))-1 for _,_,start,end,width in rows),'independent UI232 full17 header offset/length')
    for text in texts.values():
        require(all(v in text for v in ['0, 8, "SCHBNK01"','8, 3, "001"','19, 3, "001"','22, 1, code.isEmpty() ? "Q" : "S"','23, 1, "S"','60, 36,','96, 17,','113, 64,','177, 4, 256','181, 6, data','187, 6, record','193, 6, count','199, 9,','208, 4, code','for (var future : futures) future.get();'] if v!='for (var future : futures) future.get();'),'original independent header literal fields')
        require(all(v in text for v in ['"0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001"','assertSame(','new byte[b.length]'] if v!='new byte[b.length]'),'closed errors and exact ordinary error identity')
    scenario=texts['ScenarioWireClientTest'];animation=texts['AnimationWireClientTest'];music=texts['MusicWireClientTest']
    require('private static final int[] DATA = {9, 9, 48, 9, 88, 1728}' in scenario and 'private static final int[] RECORD = {272, 152, 5584, 72, 800, 4800}' in scenario and 'private static final int[] MAX = {10, 500, 100, 50, 500, 200}' in scenario,'independent scenario literal sizes')
    require(all(v in animation for v in ['0 : 928','new int[] {0, 1, 50}','new int[] {0, 15, 999}','new int[] {0, 255, 263, 46665}','64, observed.size()']) and all(v in music for v in ['? 72 : type.equals(MUSIC_SECTION_KIND) ? 136 : 1312','? 20 : type.equals(MUSIC_SECTION_KIND) ? 100 : 200','new int[] {0, 255, 263, 262673}','64, observed.size()']),'independent media counts/record bounds')
    require(all(v in scenario for v in ['new int[] {1, 201, 10000}','n * 4800L','assertEquals(100, seen.size())','Thread.interrupted()','assertEquals(1, sends.get())','assertArrayEquals(expected, original)']),'no retry/owned interruption restore/large-result value not file')
    require(all(v in documents[documents_list[2]].decode() for v in ['record（928 byte、最大50件）','record（1,312 byte、最大200件）','record（72 byte、最大20件）','record（136 byte、最大100件）']) and all(v in documents[documents_list[1]].decode() for v in ['record（5,584 byte、最大100件）','record（4,800 byte）']),'approved media/scenario size clauses')
    def put(body,start,width,value):
        value=value.encode('utf-8');require(len(value)<=width,'independent byte width');body[start:start+width]=value+b' '*(width-len(value))
    def number(body,start,width,value):put(body,start,width,str(value).zfill(width))
    vectors={}
    for layout,length in [('GAMREQ01',0),('SPKREQ01',12),('SRCREQ01',672),('RTEREQ01',12),('SCFREQ01',14),('SCNREQ01',12),('ANMREQ01',0),('ANLREQ01',16),('MCTREQ01',0),('MCSREQ01',64),('MTRREQ01',192)]:
        body=bytearray(b' '*(256+length));identifier='00000000-0000-0000-0000-000000000001'
        for start,width,value in [(0,8,'SCHBNK01'),(8,3,'001'),(11,8,layout),(19,3,'001'),(22,1,'Q'),(23,1,'S'),(24,36,identifier),(60,36,identifier),(96,17,'20260909090000123' if layout[:3] in ['GAM','SPK','SRC','RTE','SCF','SCN'] else '20260920090000000'),(113,64,'a'*64)]:put(body,start,width,value)
        for start,width,value in [(177,4,256),(181,6,length),(187,6,0),(193,6,0),(199,9,len(body))]:number(body,start,width,value)
        if layout[:3] in ['SPK','RTE','SCF']:put(body,256,12,'NUKITASHI1')
        if layout=='SCFREQ01':number(body,268,2,1)
        if layout=='SCNREQ01':number(body,256,12,1)
        if layout=='SRCREQ01':
            for start,width,value in [(256,256,'keyword'),(512,12,'NUKITASHI1'),(524,128,'speaker'),(652,256,'chapter')]:put(body,start,width,value)
            number(body,919,6,1);number(body,925,3,100)
        if layout=='ANLREQ01':put(body,256,16,'MAIN')
        if layout[:3] in ['MCS','MTR']:put(body,256,64,'曲')
        if layout=='MTRREQ01':put(body,320,128,'ゲーム')
        require(len(body)==256+length and body[208:256]==b' '*48 and body[24:60]==body[60:96] and body[113:177]==b'a'*64,'independent header field postconditions')
        vectors[layout]=dict(length=len(body),sha256=hashlib.sha256(body).hexdigest())
    helpers={name:old['fullSourceUnits'][P+'messaging/'+name] for name in ['ProtectedReadWireClient','ProtectedReadWireException','ScenarioWireException','JmsRequestReplyClient','ReplyCorrelationRegistry','PendingReply','JmsRequestReplyException']}
    require(all(u['post'] in ['PG14314-web-business-wire-whole-twelve-post-v1','PG14318-web-memory-coordinator-whole-seventeen-post-v1','PG14788-web-messaging-exception-three-post-v1'] for u in helpers.values()),'unchanged actual helper proofs, not new target counters')
    vectors_to_reject=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('sources','fullSourceUnits',{}),('tests','tests',25),('suites','suites',4),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic-key','publicSyntheticTestKeysUsed',True),('jca','childLocalJcaRegistryRestorationTested',True),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    require(all(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True) for _,key,value in vectors_to_reject),'every negative truly differs')
    labels=[]
    for label,key,value in vectors_to_reject:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=24,suites=3,sourcePrograms=3,physicalClasses=4,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=3,incompleteSourcePrograms=0,baselineMainOwnerRows=3,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,independentHeaderOffsets=offsets,independentRequestVectors=vectors,previousHelperProofs=helpers,nondegenerateNegativeVectors=len(vectors_to_reject),pythonVersion=sys.version,approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],publicSyntheticTestKeysUsed=False,childLocalJcaRegistryRestorationTested=False,ownFreshJvmProviderStateOnly=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,previousHelpersNotReaccepted=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=24,semanticNegativeVectors=len(labels))))
if __name__=='__main__':main()
