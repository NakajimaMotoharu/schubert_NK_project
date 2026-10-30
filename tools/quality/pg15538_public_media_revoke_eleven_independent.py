"""Independent UI offset and public AES-GCM oracle for original media4/revocation7."""
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
import pg15535_public_media_revoke_eleven_pt_v2 as original
import pg15536_public_media_revoke_eleven_post as post
import pg9666_pagination_static as runner

PIN='bb9ddfe2a43c3259772bb835e3a3a438c93342822686d8f85b10a70bc2244ebf'
OUT=data.BASE/'PG15538-public-media-revoke-eleven-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15538-public-media-revoke-eleven-independent-v1'
P=original.PREFIX
CLOSURES={P+n:[P+n,*[P+n+'$'+v for v in (['Binding','Result'] if n=='media/MediaResponseDecoder' else [])]] for n in original.MAIN_PINS}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
NODE='/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node'
NODE_PIN='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'
JS="""const c=require('node:crypto');
const time=Buffer.alloc(12);time.writeBigInt64BE(1788825600n);time.writeUInt32BE(123456000,8);
const fields=[Buffer.from('web-revoke'),Buffer.from('schubert_web_session.pending_context_revocations'),Buffer.from('00112233445566778899aabbccddeeff','hex'),time,Buffer.from([1]),Buffer.from('v2')];
const aad=Buffer.concat(fields.flatMap(b=>{const n=Buffer.alloc(4);n.writeUInt32BE(b.length);return [n,b]}));
const key=Buffer.from(Array.from({length:32},(_,i)=>i)),nonce=Buffer.from(Array.from({length:12},(_,i)=>160+i)),plain=Buffer.from('0123456789abcdef'.repeat(4));
const cipher=c.createCipheriv('aes-256-gcm',key,nonce);cipher.setAAD(aad);
const ciphertext=Buffer.concat([cipher.update(plain),cipher.final()]),tag=cipher.getAuthTag();
const envelope=Buffer.concat([Buffer.from('NKENC1'),Buffer.from([1,2]),Buffer.from('v2'),nonce,ciphertext,tag]);
const sha=b=>c.createHash('sha256').update(b).digest('hex');
console.log(JSON.stringify({node:process.version,openssl:process.versions.openssl,publicSyntheticFixture:true,aadHex:aad.toString('hex'),envelopeHex:envelope.toString('hex'),aadSha256:sha(aad),envelopeSha256:sha(envelope),plaintextLength:plain.length,tagLength:tag.length,envelopeLength:envelope.length}));"""
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/run')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(11,2,11,2) and all(p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','newTestIds','crcMismatch']),'exact pass')
    require(len({(c['classname'],c['name']) for c in p['cases']})==11 and all(c['result']=='PASS' for c in p['cases']),'unique/pass')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one exec')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==NAMES,'all four target Source/sixCode; no helper transfer')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'Code/filter')
    require(all(any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']) for n in NAMES),'actual Code')
    totals={k:{r:sum(p['executable'][n]['counters'][k][r] for n in NAMES) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={'LINE':{'covered':228,'missed':10},'METHOD':{'covered':29,'missed':1},'CLASS':{'covered':6,'missed':0},'BRANCH':{'covered':82,'missed':3}},'same exec measured counters')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==sorted(ns) and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is False,'independent per Source categories')
    require(p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and sum(u['four100'] for u in p['fullSourceUnits'].values())==3,'three four100/one gap')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is True and p['cryptoOperationKind']=='AES256GCM_PUBLIC_SYNTHETIC_KEYS_AND_PUBLIC_CONTEXT_CONSTANTTIME_COMPARISON','truthful public synthetic crypto')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is p['actualFilesOpenedByProduct'] is p['actualPrivateFilesOpened'] is p['jmsFactoryObjectsConstructed'] is p['onlySyntheticJmsProxyMessages'] is p['jmsDestinationValueObjectsConstructed'] is False,'no live/private/JMS actions')
    require(p['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is False,'no broker')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']),'held/native absences')
    require(p['rootMainInvoked'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['effortPercent'] is None and p['productTestsReexecutedByPost']==0,'no old/formal/effort transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','actualBrowserActions','actualBoundSockets']),'no external effects')
    require(len(p['owners'])==6 and sum(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and r['canonicalOwner']==r['canonicalCostOwner'] for r in p['owners'].values())==4 and sum(r['ownershipStatus']=='UNKNOWN' and r['canonicalOwner'] is r['canonicalCostOwner'] is None for r in p['owners'].values())==2,'actual ownership')
    require(all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'genuine stages')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15535-public-media-revoke-eleven-pt-v2/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15524-current1850-synthetic-jms-guard-registry-v1/manifest.json','56979288ade5f3ab2f215677d826e0fcc706bbd72dcb24b760c03907a3ae2913')
    require(not set(CLOSURES)&set(old['fullSourceUnits']) and {P+n for n in original.HELPER_PINS}<=set(old['fullSourceUnits']),'new targets/prior helpers partition')
    helpers={P+n:old['fullSourceUnits'][P+n] for n in original.HELPER_PINS}
    require(helpers[P+'media/MediaDeliveryException']['postSha256']=='c055a0579f557b763f666efd914ca8220ea57a9f0ef38fcbe45f0578351f4190' and helpers[P+'revocation/RevocationPayloadException']['postSha256']=='f76681c7ca0e418926087390ccefe7b82bf5197722e7c38c0571773ea6badadb','old exception qualification retained')
    require(not (data.BASE/'PG15534-public-media-revoke-eleven-pt-v1').exists() and not (data.ROOT.parent/'pgpt-runs/PG379/pg15534-public-media-revoke-eleven-pt-v1').exists(),'old preflight before any Product execution')
    texts={k:path.read_text() for k,path in original.TESTS.items()};media=texts['MediaResponseDecoderTest'];rev=texts['RevocationPayloadCodecTest']
    require(all(not re.search(r'\b'+name+r'\s*\(',t) for t in texts.values() for name in ['createConnection','createContext','getConnection','startServer','decodeVerified']),'only original memory scope')
    expected=set()
    for key,path in original.TESTS.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',texts[key]);require(len(names)==original.COUNTS[key],'whole original discovery')
        package=re.search(r'package ([A-Za-z0-9_.]+);',texts[key]).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every original method exactly once')
    clauses=['\"web-revoke\"','\"schubert_web_session.pending_context_revocations\"','data.writeLong(1788825600L)','data.writeInt(123456000)','new byte[] {1}','data.writeInt(field.length)','Cipher.getInstance(\"AES/GCM/NoPadding\")','new GCMParameterSpec(128, NONCE)','assertArrayEquals(golden, value.ciphertext())','assertEquals(100, nonces.size())','Security.removeProvider(\"SunJCE\")','Security.insertProviderAt(provider, position)','assertNull(failure.getCause())','failure.getSuppressed().length']
    require(all(v in rev for v in clauses) and all(v in rev for v in ['00112233-4455-6677-8899-aabbccddeeff','2026-09-08T00:00:00.123456Z','\"0123456789abcdef\".repeat(4)','a0a1a2a3a4a5a6a7a8a9aaab']),'independent JCA/fixed public vector/own JCA restore')
    offsets={0:64,64:512,576:256,832:12,844:64,908:64,972:1,973:51}
    require(sum(offsets.values())==1024 and all(o+l==next_o for (o,l),next_o in zip(offsets.items(),list(offsets)[1:])),'independent MEDIA1024 contiguous offsets')
    require(all(v in media for v in ['put(data, 64, path)','put(data, 576, name)','put(data, 832, String.format(Locale.ROOT, \"%012d\", size))','put(data, 844, HASH)','put(data, 908, mime)','put(data, 972, mode)','put(data, 1024, \"Opening\")','put(data, 1280, \"OPENING\")','put(data, 1296, \"opening.mp4\")','put(body, 177, \"0256\")','put(body, 208, code)','assertArrayEquals(before, body)']),'original independent byte positions')
    docs=['documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md','documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md','documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(b==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,b in documents.items()),'approved remote main design bytes')
    require(all(v in documents[docs[0]].decode() for v in ['magic 6 bytes \"NKENC1\"','nonce 12 random bytes','authentication tag 16 bytes','length-prefixed']),'approved envelope/AAD')
    require(all(v in documents[docs[1]].decode() for v in ['| Storage relative path | 65 | 512 |','| File name | 577 | 256 |','| File byte長 | 833 | 12 |','| SHA-256 | 845 | 64 |','| MIME type | 909 | 64 |','| Content disposition | 973 | 1 |','| Title | 1,025 | 256 |','| Category | 1,281 | 16 |','| Display path | 1,297 | 512 |']),'approved independent media byte offsets')
    negative=[]
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('source-units','fullSourceUnits',{}),('tests','tests',12),('suites','suites',3),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic','publicSyntheticTestKeysUsed',False),('jca-restore','childLocalJcaRegistryRestorationTested',False),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old-transfer','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError('false current qualification '+label)
    require(data.sha(Path(NODE).read_bytes())==NODE_PIN,'fixed independent Node')
    SLOT.mkdir();runner.SLOT=SLOT;stage=runner.step('independent-node-public-revoke-vector',[NODE,'-e',JS],SLOT,timeout=30)
    require(stage['actualExit']==0 and not stage['timedOut'],'Node oracle actual terminal')
    vector=json.loads((SLOT/'independent-node-public-revoke-vector.stdout').read_text())
    fields=[b'web-revoke',b'schubert_web_session.pending_context_revocations',uuid.UUID('00112233-4455-6677-8899-aabbccddeeff').bytes,struct.pack('>qI',1788825600,123456000),bytes([1]),b'v2']
    aad=b''.join(struct.pack('>I',len(v))+v for v in fields);envelope=bytes.fromhex(vector['envelopeHex'])
    require(vector['node']=='v24.19.0' and vector['openssl']=='3.5.7' and vector['publicSyntheticFixture'] is True and bytes.fromhex(vector['aadHex'])==aad and vector['aadSha256']==hashlib.sha256(aad).hexdigest(),'independent Node/Python binary AAD')
    require(vector['plaintextLength']==64 and vector['tagLength']==16 and vector['envelopeLength']==len(envelope)==102 and envelope[:22]==b'NKENC1'+bytes([1,2])+b'v2'+bytes(range(160,172)) and vector['envelopeSha256']==hashlib.sha256(envelope).hexdigest(),'public fixed envelope')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=11,suites=2,sourcePrograms=4,physicalClasses=6,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=1,baselineMainOwnerRows=4,unknownTestOwnerRows=2,semanticNegativeVectors=len(negative),negativeLabels=negative,independentMediaOffsetLengths=offsets,independentNodeOracle=vector,nodeBinarySha256=NODE_PIN,nodeCommandStage=stage,nodeOracleRelation='PUBLIC_PARAMETERS_MATCH_ORIGINAL_INDEPENDENT_JCE_NOT_PRODUCT_CAPTURE',approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},previousHelperSourceUnits=helpers,previousHelpersNotReaccepted=True,cryptoOrKeyOperationsInvoked=True,publicSyntheticTestKeysUsed=True,cryptoOperationKind=p['cryptoOperationKind'],childLocalJcaRegistryRestorationTested=True,ownFreshJvmProviderStateOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,onlySyntheticJmsProxyMessages=False,jmsFactoryObjectsConstructed=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,relatedBug='BUG-2135',relatedYkt='YKT-1882'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=11,semanticNegativeVectors=len(negative),aadSha256=vector['aadSha256'],envelopeSha256=vector['envelopeSha256'])))
if __name__=='__main__':main()
