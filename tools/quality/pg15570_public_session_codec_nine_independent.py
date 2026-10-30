"""Independent public JSON/row AAD/GCM oracle for original session codec nine, not real session issuance."""
import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15566_public_session_codec_nine_pt as original
import pg15568_public_session_codec_nine_post as post
import pg9666_pagination_static as runner

PIN='305f59711ae025aa6d038ac54c9617f55b7736693c87c22e5d898e48bb83840f'
OUT=data.BASE/'PG15570-public-session-codec-nine-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15570-public-session-codec-nine-independent-v1'
P=original.PREFIX
CLOSURES={P+n:[P+n] for n in original.MAIN_PINS}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
NODE='/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node'
NODE_PIN='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'
JS="""const c=require('node:crypto');
const time=Buffer.alloc(12);time.writeBigInt64BE(1788825600n);time.writeUInt32BE(123456000,8);
const fields=[Buffer.from('web-session'),Buffer.from('schubert_web_session.web_http_sessions'),Buffer.from('00112233445566778899aabbccddeeff','hex'),Buffer.from('a'.repeat(64)),time,Buffer.from([1]),Buffer.from('v2')];
const aad=Buffer.concat(fields.flatMap(b=>{const n=Buffer.alloc(4);n.writeUInt32BE(b.length);return [n,b]}));
const key=Buffer.from(Array.from({length:32},(_,i)=>i)),nonce=Buffer.from(Array.from({length:12},(_,i)=>160+i)),sha=b=>c.createHash('sha256').update(b).digest('hex');
const vectors=[false,true].map(authenticated=>{
  const obj={formatVersion:2};
  if(authenticated) Object.assign(obj,{username:'reader',role:'ADMIN',authenticationContext:'b'.repeat(64),loginAt:'2026-09-08T00:00:00Z'});
  Object.assign(obj,{csrfToken:'c'.repeat(64),savedRequest:'/logs?q=日本語',operationTokens:[{purpose:'QSBREQ01',token:'00000000-0000-0000-0000-000000000001',issuedAt:'2026-09-08T00:00:00Z'}]});
  const plain=Buffer.from(JSON.stringify(obj),'utf8'),cipher=c.createCipheriv('aes-256-gcm',key,nonce);cipher.setAAD(aad);
  const ciphertext=Buffer.concat([cipher.update(plain),cipher.final()]),tag=cipher.getAuthTag();
  const envelope=Buffer.concat([Buffer.from('NKENC1'),Buffer.from([1,2]),Buffer.from('v2'),nonce,ciphertext,tag]);
  return {authenticated,plaintextLength:plain.length,plaintextSha256:sha(plain),tagLength:tag.length,envelopeLength:envelope.length,envelopeHex:envelope.toString('hex'),envelopeSha256:sha(envelope)};
});
console.log(JSON.stringify({node:process.version,openssl:process.versions.openssl,publicSyntheticFixture:true,aadHex:aad.toString('hex'),aadSha256:sha(aad),vectors}));"""
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(9,1,9,1) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'exact pass')
    require(len({(c['classname'],c['name']) for c in p['cases']})==9 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'all four target Source/sixCode; no helper transfer')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'Code/filter')
    require(all(any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']) for n in NAMES),'actual Code')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={'LINE':{'covered':142,'missed':0},'METHOD':{'covered':17,'missed':0},'CLASS':{'covered':3,'missed':0},'BRANCH':{'covered':58,'missed':0}},'same exec measured counters')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==sorted(ns) and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is False,'independent per Source categories')
    require(p['targetUnitFour100'] is True and p['strictFour100GateExit']==0 and sum(u['four100'] for u in p['fullSourceUnits'].values())==3,'three four100/one gap')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is True and p['cryptoOperationKind']=='AES256GCM_PUBLIC_SYNTHETIC_SESSION_KEYS_ONLY','truthful public synthetic crypto')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is p['onlySyntheticJmsProxyMessages'] is p['jmsDestinationValueObjectsConstructed'] is False,'no live/private/JMS actions')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'no broker')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absences')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no old/formal/effort transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==4 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==3 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==1,'actual ownership')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'genuine stages')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15566-public-session-codec-nine-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15556-current1870-public-weblog-codec-registry-v1/manifest.json','366596b4fb25238559e0f771eaf9760bc96a1fc85e70b8375d361da57a1182a3')
    require(not set(CLOSURES)&set(old['fullSourceUnits']) and {P+n for n in original.HELPER_PINS}<=set(old['fullSourceUnits']),'new targets/prior helpers partition')
    helpers={P+n:old['fullSourceUnits'][P+n] for n in original.HELPER_PINS}
    require(set(helpers)=={P+'session/SessionPayloadException',P+'session/SessionAttributeCodec'} and helpers[P+'session/SessionPayloadException']['postSha256']=='fc2d07048ae0912650e42454f5ebd24dd74eba80c16f91968cba25161edddc31' and helpers[P+'session/SessionAttributeCodec']['postSha256']=='34fb74f75134d89f6aa2ed573277d396c0b20ced06bbd1ae8fce418aff94f734','old exception/JSON qualification retained')
    texts={k:path.read_text() for k,path in original.TESTS.items()};test=texts['SessionPayloadCodecTest']
    helper=original.ROOT/'session/SessionAttributeCodecTest.java';helper_text=helper.read_text()
    require(data.sha(helper.read_bytes())=='54c9a088ec519b70dd19ed4a6f88c2640c0fb5b410f12e16e554e2d0f9170b02' and any(Path(k).name==helper.name and h==data.sha(helper.read_bytes()) for k,h in raw['begin']['testSourceHashes'].items()),'whole original fixture helper really compiled')
    require(all(c['classname']=='dev.codex.schubert.nk.web.session.SessionPayloadCodecTest' for c in p['cases']) and p['originalHelperTestSuiteReexecuted'] is False and p['syntheticSessionAttributesSerialized'] is True,'selected9 only/not helper7')
    require(all(not re.search(r'\b'+name+r'\s*\(',test) for name in ['createConnection','createContext','getConnection','startServer']),'only memory scope')
    expected=set()
    for key,path in original.TESTS.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',texts[key]);require(len(names)==original.COUNTS[key],'whole original discovery')
        package=re.search(r'package ([A-Za-z0-9_.]+);',texts[key]).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every original method exactly once')
    clauses=['bytes("web-session")','bytes("schubert_web_session.web_http_sessions")','data.writeLong(1788825600L)','data.writeInt(123456000)','new byte[] {1}','data.writeInt(field.length)','Cipher.getInstance("AES/GCM/NoPadding")','new GCMParameterSpec(128, NONCE)','assertArrayEquals(expected, encrypted.ciphertext())','assertEquals(100, nonces.size())','Security.removeProvider("SunJCE")','Security.insertProviderAt(provider, position)','assertNull(error.getCause())']
    require(all(v in test for v in clauses),'independent JCA/fixed public vector/own JCA restore')
    require(all(v in test for v in ['00112233-4455-6677-8899-aabbccddeeff','2026-09-08T00:00:00.123456Z','"a".repeat(64)','a0a1a2a3a4a5a6a7a8a9aaab','plain(authenticated)','"/logs?q=日本語"','16384','16436','tokv206IndependentLegacyPlaintextStillDecryptsUnderEitherKey']),'original complete parameter/boundary/legacy oracle')
    require(all(v in helper_text for v in ['StringBuilder("{\\"formatVersion\\":2")','QUESTION_SUBMIT_PURPOSE = "QSBREQ01"','static final String CONTEXT = "b".repeat(64)','static final String CSRF = "c".repeat(64)','s.append(",\\"operationTokens\\":[")','+ quote(TIME)','tokenJson(i)']),'independent literal helper JSON fields')
    docs=['documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(content==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,content in documents.items()),'approved main design bytes')
    require(all(v in documents[docs[0]].decode() for v in ['magic 6 bytes "NKENC1"','nonce 12 random bytes','authentication tag 16 bytes','length-prefixed']),'approved envelope/AAD')
    negative=[]
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('source-units','fullSourceUnits',{}),('tests','tests',10),('suites','suites',2),('four','targetUnitFour100',False),('strict','strictFour100GateExit',1),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic','publicSyntheticTestKeysUsed',False),('jca-restore','childLocalJcaRegistryRestorationTested',False),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old-transfer','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError('false current qualification '+label)
    require(data.sha(Path(NODE).read_bytes())==NODE_PIN,'fixed independent Node')
    SLOT.mkdir();runner.SLOT=SLOT;stage=runner.step('independent-node-public-session-vector',[NODE,'-e',JS],SLOT,timeout=30)
    require(stage['actualExit']==0 and not stage['timedOut'],'Node oracle actual terminal')
    vector=json.loads((SLOT/'independent-node-public-session-vector.stdout').read_text())
    fields=[b'web-session',b'schubert_web_session.web_http_sessions',uuid.UUID('00112233-4455-6677-8899-aabbccddeeff').bytes,b'a'*64,struct.pack('>qI',1788825600,123456000),bytes([1]),b'v2']
    aad=b''.join(struct.pack('>I',len(v))+v for v in fields)
    require(len(fields)==7 and vector['node']=='v24.19.0' and vector['openssl']=='3.5.7' and vector['publicSyntheticFixture'] is True and bytes.fromhex(vector['aadHex'])==aad and vector['aadSha256']==hashlib.sha256(aad).hexdigest(),'independent Node/Python seven binary AAD fields')
    require([v['authenticated'] for v in vector['vectors']]==[False,True],'both original JSON profiles')
    for v in vector['vectors']:
        obj=dict(formatVersion=2)
        if v['authenticated']:obj.update(username='reader',role='ADMIN',authenticationContext='b'*64,loginAt='2026-09-08T00:00:00Z')
        obj.update(csrfToken='c'*64,savedRequest='/logs?q=日本語',operationTokens=[dict(purpose='QSBREQ01',token='00000000-0000-0000-0000-000000000001',issuedAt='2026-09-08T00:00:00Z')])
        plain=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8');envelope=bytes.fromhex(v['envelopeHex'])
        require(v['plaintextSha256']==hashlib.sha256(plain).hexdigest() and v['plaintextLength']==len(plain) and v['tagLength']==16 and v['envelopeLength']==len(envelope)==len(plain)+38 and envelope[:22]==b'NKENC1'+bytes([1,2])+b'v2'+bytes(range(160,172)) and v['envelopeSha256']==hashlib.sha256(envelope).hexdigest(),'independent public JSON/GCM envelope')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=9,suites=1,sourcePrograms=3,physicalClasses=3,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,baselineMainOwnerRows=3,unknownTestOwnerRows=1,semanticNegativeVectors=len(negative),negativeLabels=negative,originalHelperTestMethodsReexecuted=0,originalWholeHelperSourceSha256=data.sha(helper.read_bytes()),syntheticSessionAttributesSerialized=True,independentNodeOracle=vector,nodeBinarySha256=NODE_PIN,nodeCommandStage=stage,nodeOracleRelation='PUBLIC_PARAMETERS_MATCH_ORIGINAL_INDEPENDENT_JCE_NOT_PRODUCT_CAPTURE',approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},previousHelperSourceUnits=helpers,previousHelpersNotReaccepted=True,cryptoOrKeyOperationsInvoked=True,publicSyntheticTestKeysUsed=True,cryptoOperationKind=p['cryptoOperationKind'],childLocalJcaRegistryRestorationTested=True,ownFreshJvmProviderStateOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,onlySyntheticJmsProxyMessages=False,jmsFactoryObjectsConstructed=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=9,semanticNegativeVectors=len(negative),aadSha256=vector['aadSha256'],envelopeSha256=[v['envelopeSha256'] for v in vector['vectors']])))
if __name__=='__main__':main()
