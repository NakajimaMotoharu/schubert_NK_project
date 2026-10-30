"""Independent full UI wire and public AES-GCM oracle for whole Web log codec original nine."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15550_public_weblog_codec_nine_pt as original
import pg15552_public_weblog_codec_nine_post as post

PIN='d7a0edc39323273aa32fc315bd9d2195bd431a2fee90b309e85254d02ba52192'
OUT=data.BASE/'PG15555-public-weblog-codec-nine-independent-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15555-public-weblog-codec-nine-independent-v2'
P=original.PREFIX
CLOSURES={P+n:[P+n] for n in original.MAIN_PINS}
NAMES=set().union(*[set(v) for v in CLOSURES.values()])
NODE='/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node'
NODE_PIN='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'
JS="""const c=require('node:crypto');
const mid='00000000-0000-0000-0000-000000000012',cid='00000000-0000-0000-0000-000000000015';
const fields=[Buffer.from('web-log-outbox'),Buffer.from('schubert_web_session.web_log_outbox'),Buffer.from(mid.replaceAll('-',''),'hex'),Buffer.from(cid.replaceAll('-',''),'hex'),Buffer.from([1]),Buffer.from('v2'),Buffer.from('WLGEVT01'),Buffer.from('001')];
const aad=Buffer.concat(fields.flatMap(b=>{const n=Buffer.alloc(4);n.writeUInt32BE(b.length);return [n,b]}));
const wire=Buffer.alloc(2336,32),put=(offset,value)=>Buffer.from(value,'ascii').copy(wire,offset);
[[0,'SCHBNK01001WLGEVT01001EI'],[24,mid],[60,cid],[96,'20260905060000000'],[177,'0256002080000000000000000002336'],[256,'20260905060000000'],[273,'REQUEST'],[289,'INFO'],[297,'HTTP_COMPLETED'],[361,'Synthetic HTTP request completed'],[873,'00000000-0000-0000-0000-000000000099'],[909,'GET'],[917,'/login'],[1173,'200'],[1176,'12'],[1185,'127.0.0.1'],[1299,'{"projection":"PENDING"}']].forEach(([o,v])=>put(o,v));
const key=Buffer.from(Array.from({length:32},(_,i)=>i)),nonce=Buffer.from(Array.from({length:12},(_,i)=>64+i));
const cipher=c.createCipheriv('aes-256-gcm',key,nonce);cipher.setAAD(aad);
const ciphertext=Buffer.concat([cipher.update(wire),cipher.final()]),tag=cipher.getAuthTag();
const envelope=Buffer.concat([Buffer.from('NKENC1'),Buffer.from([1,2]),Buffer.from('v2'),nonce,ciphertext,tag]);
const sha=b=>c.createHash('sha256').update(b).digest('hex');
console.log(JSON.stringify({node:process.version,openssl:process.versions.openssl,publicSyntheticFixture:true,aadHex:aad.toString('hex'),envelopeHex:envelope.toString('hex'),aadSha256:sha(aad),wireSha256:sha(wire),envelopeSha256:sha(envelope),plaintextLength:wire.length,tagLength:tag.length,envelopeLength:envelope.length}));"""
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
    require(totals==p['totals']=={'LINE':{'covered':164,'missed':0},'METHOD':{'covered':19,'missed':0},'CLASS':{'covered':3,'missed':0},'BRANCH':{'covered':60,'missed':0}},'same exec measured counters')
    for name,ns in CLOSURES.items():
        u=p['fullSourceUnits'][name];values={k:{r:sum(p['executable'][n]['counters'][k][r] for n in ns) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(u['physical']==sorted(ns) and u['totals']==values and u['four100'] is all(v['missed']==0 and v['covered']>0 for v in values.values()) and u['branchNaturallyZero'] is False,'independent per Source categories')
    require(p['targetUnitFour100'] is True and p['strictFour100GateExit']==0 and sum(u['four100'] for u in p['fullSourceUnits'].values())==3,'three four100/one gap')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is True and p['cryptoOperationKind']=='AES256GCM_PUBLIC_SYNTHETIC_WEBLOG_KEYS_ONLY','truthful public synthetic crypto')
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
    raw=data.read_checked(data.BASE/'PG15550-public-weblog-codec-nine-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15540-current1861-public-media-revoke-registry-v1/manifest.json','36f3acc9cbebd081fe711c5fa3151e96365899205bf0cfedbd7f5b06ca9a9277')
    require(not set(CLOSURES)&set(old['fullSourceUnits']) and {P+n for n in original.HELPER_PINS}<=set(old['fullSourceUnits']),'new targets/prior helpers partition')
    helpers={P+n:old['fullSourceUnits'][P+n] for n in original.HELPER_PINS}
    require(set(helpers)=={P+'logging/WebLogPayloadException'} and helpers[P+'logging/WebLogPayloadException']['postSha256']=='8db3113828fad40efde6ca9f6b8b349b204349fe274774027405412e4e28bab8','old logging exception retained')
    texts={k:path.read_text() for k,path in original.TESTS.items()};test=texts['WebLogPayloadCodecTest']
    require(all(not re.search(r'\b'+name+r'\s*\(',test) for name in ['createConnection','createContext','getConnection','startServer']),'only original memory scope')
    expected=set()
    for key,path in original.TESTS.items():
        names=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',texts[key]);require(len(names)==original.COUNTS[key],'whole original discovery')
        package=re.search(r'package ([A-Za-z0-9_.]+);',texts[key]).group(1);expected.update((package+'.'+key,n) for n in names)
    require(expected=={(c['classname'],c['name']) for c in p['cases']},'every original method exactly once')
    clauses=['"web-log-outbox"','"schubert_web_session.web_log_outbox"','"WLGEVT01"','"001"','new byte[] {1}','data.writeInt(field.length)','Cipher.getInstance("AES/GCM/NoPadding")','new GCMParameterSpec(128, NONCE)','assertArrayEquals(expected, encrypted.ciphertext())','assertEquals(100, nonces.size())','Security.removeProvider("SunJCE")','Security.insertProviderAt(provider, position)','assertNull(exception.getCause())']
    require(all(v in test for v in clauses),'independent JCA/fixed public vector/own JCA restore')
    positions={0:'SCHBNK01001WLGEVT01001EI',24:'00000000-0000-0000-0000-000000000012',60:'00000000-0000-0000-0000-000000000015',96:'20260905060000000',177:'0256002080000000000000000002336',256:'20260905060000000',273:'REQUEST',289:'INFO',297:'HTTP_COMPLETED',361:'Synthetic HTTP request completed',873:'00000000-0000-0000-0000-000000000099',909:'GET',917:'/login',1173:'200',1176:'12',1185:'127.0.0.1',1299:'{"projection":"PENDING"}'}
    golden=bytearray(b' '*2336)
    for off,value in positions.items():golden[off:off+len(value)]=value.encode('ascii')
    require(len(golden)==2336 and golden[113:177]==b' '*64 and golden[208:212]==b' '*4 and golden[-13:]==b' '*13,'independent full wire closed event frame')
    require(all(v in test for v in ['new byte[2_336]','ascii(wire, 177, "0256002080000000000000000002336")','ascii(wire, 256 + 105, "Synthetic HTTP request completed")','ascii(wire, 256 + 653, "GET")','ascii(wire, 256 + 661, "/login")','ascii(wire, 256 + 1043, "{\\"projection\\":\\"PENDING\\"}")','sequence(32, 0)','sequence(12, 64)']),'original independent byte positions')
    docs=['documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md','documents/200_UI/230_インターフェース/235_メディア・ログ電文仕様.md','documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md']
    documents={v:(data.ROOT/v).read_bytes() for v in docs}
    require(all(content==subprocess.check_output(['git','show','origin/main:'+v],cwd=data.ROOT) for v,content in documents.items()),'approved main design bytes')
    require(all(v in documents[docs[0]].decode() for v in ['magic 6 bytes "NKENC1"','nonce 12 random bytes','authentication tag 16 bytes','length-prefixed']),'approved envelope/AAD')
    require(all(v in documents[docs[1]].decode() for v in [chr(96)+'WLGEVT01'+chr(96)+' data（2,080 byte）','| Log type | 18 | 16 |','| Message | 106 | 512 |','| HTTP method | 654 | 8 |','| Path | 662 | 256 |','| HTTP status | 918 | 3 |','| Details | 1,044 | 1,024 |','| Reserved | 2,068 | 13 |']),'independent approved log field offsets')
    negative=[]
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('cases','cases',[]),('totals','totals',{}),('physical','physicalClasses',{}),('source-units','fullSourceUnits',{}),('tests','tests',10),('suites','suites',2),('four','targetUnitFour100',False),('strict','strictFour100GateExit',1),('session','singleSession',False),('crc','crcMismatch',1),('metadata','metadataClasses',['unknown']),('excluded','manualCounterExclusions',['unknown']),('crypto','cryptoOrKeyOperationsInvoked',False),('synthetic','publicSyntheticTestKeysUsed',False),('jca-restore','childLocalJcaRegistryRestorationTested',False),('secret','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('old-transfer','oldCoverageTransferred',True),('file','actualFilesOpenedByProduct',True),('root','rootMainInvoked',True),('accepted','newAccepted',1),('post-replay','productTestsReexecutedByPost',1),('effort','effortPercent',100)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError('false current qualification '+label)
    require(data.sha(Path(NODE).read_bytes())==NODE_PIN,'fixed independent Node')
    oracle_old=data.ROOT.parent/'pgpt-runs/PG379/pg15554-public-weblog-codec-nine-independent-v1'
    oracle_label='independent-node-public-weblog-vector'
    old_entry=data.ROOT/'tools/quality/pg15554_public_weblog_codec_nine_independent.py'
    require(data.sha(old_entry.read_bytes())=='a875576532151d9706242c9d612e459f894f261bb40f749bd03bc06c24ece71e','frozen original oracle entry')
    stage=json.loads((oracle_old/(oracle_label+'-exit.safe.json')).read_bytes())
    def oracle_contract(v,label):
        require(label=='independent-node-public-weblog-vector' and v['actualExit']==0 and v['timedOut'] is False and v['command']==[NODE,'-e',JS] and v['cwd']==str(oracle_old),'original exact oracle identity/terminal')
        require(v['stdoutSha256']==data.sha((oracle_old/(label+'.stdout')).read_bytes()) and v['stderrSha256']==data.sha((oracle_old/(label+'.stderr')).read_bytes()),'original oracle streams')
    oracle_contract(stage,oracle_label);oracle_negative=[]
    for label,key,value in [('label',None,'old-revoke'),('command','command',[NODE,'--version']),('stream','stdoutSha256','0'*64)]:
        bad=copy.deepcopy(stage)
        if key is not None:bad[key]=value
        try:oracle_contract(bad,value if key is None else oracle_label)
        except ValueError:oracle_negative.append(label)
        else:raise AssertionError('false oracle recovery '+label)
    SLOT.mkdir()
    require(stage['actualExit']==0 and not stage['timedOut'],'Node oracle actual terminal')
    vector=json.loads((oracle_old/(oracle_label+'.stdout')).read_text())
    fields=[b'web-log-outbox',b'schubert_web_session.web_log_outbox',uuid.UUID(positions[24]).bytes,uuid.UUID(positions[60]).bytes,bytes([1]),b'v2',b'WLGEVT01',b'001']
    aad=b''.join(len(v).to_bytes(4,'big')+v for v in fields);envelope=bytes.fromhex(vector['envelopeHex'])
    require([len(v) for v in fields]==[14,35,16,16,1,2,8,3] and len(aad)==127,'independent eight AAD lengths')
    require(vector['node']=='v24.19.0' and vector['openssl']=='3.5.7' and vector['publicSyntheticFixture'] is True and bytes.fromhex(vector['aadHex'])==aad and vector['aadSha256']==hashlib.sha256(aad).hexdigest(),'independent Node/Python AAD')
    require(vector['wireSha256']==hashlib.sha256(golden).hexdigest() and vector['plaintextLength']==2336 and vector['tagLength']==16 and vector['envelopeLength']==len(envelope)==2374 and envelope[:22]==b'NKENC1'+bytes([1,2])+b'v2'+bytes(range(64,76)) and vector['envelopeSha256']==hashlib.sha256(envelope).hexdigest(),'independent full fixed wire/GCM envelope')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=9,suites=1,sourcePrograms=3,physicalClasses=3,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,baselineMainOwnerRows=3,unknownTestOwnerRows=1,semanticNegativeVectors=len(negative),negativeLabels=negative,independentWirePositions=positions,independentWireSha256=hashlib.sha256(golden).hexdigest(),independentNodeOracle=vector,nodeBinarySha256=NODE_PIN,nodeCommandStage=stage,nodeOracleReexecuted=False,nodeOracleOriginalEntrySha256=data.sha(old_entry.read_bytes()),nodeOracleExitReceiptSha256=data.sha((oracle_old/(oracle_label+'-exit.safe.json')).read_bytes()),nodeOracleRecoveryNegativeVectors=len(oracle_negative),nodeOracleRecoveryNegativeLabels=oracle_negative,nodeOracleRelation='PUBLIC_PARAMETERS_MATCH_ORIGINAL_INDEPENDENT_JCE_NOT_PRODUCT_CAPTURE',approvedDesignHashes={v:data.sha(b) for v,b in documents.items()},previousHelperSourceUnits=helpers,previousHelpersNotReaccepted=True,cryptoOrKeyOperationsInvoked=True,publicSyntheticTestKeysUsed=True,cryptoOperationKind=p['cryptoOperationKind'],childLocalJcaRegistryRestorationTested=True,ownFreshJvmProviderStateOnly=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualPrivateFilesOpened=False,onlySyntheticJmsProxyMessages=False,jmsFactoryObjectsConstructed=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,relatedBug='BUG-2136',relatedYkt='YKT-1883'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=9,semanticNegativeVectors=len(negative),aadSha256=vector['aadSha256'],envelopeSha256=vector['envelopeSha256'])))
if __name__=='__main__':main()
