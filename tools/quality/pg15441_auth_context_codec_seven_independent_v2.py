"""Independent whole AES7 source/run/closure/oracles; public synthetic material only."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
from trace_owner_join import canonical

POST=('PG15438-auth-context-codec-seven-post-v3','ccdcea8f8f9fe425963362bb15306d1b93bd2c8d0925aeeebf21a299836192b6')
RAW=('PG15435-auth-context-codec-seven-pt-v2','fad68cf7e30c38831e7928eb1a17b3effa2cb1326085cd6add557ec4e6e8be85')
REG=('PG15424-current1803-context-hash-registry-v1','8b2967c3e42ea8126d3b4c13805f9d6433e12ec8584349d2802379b699541f9f')
OUT=data.BASE/'PG15441-auth-context-codec-seven-independent-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15441-auth-context-codec-seven-independent-v2'
PREFIX='dev/codex/schubert/nk/api/security/'
ROWS={'AuthContextCodec':(104,11,1,34),'AuthContextIdentity':(16,2,1,8),'EncryptedAuthContext':(11,3,1,6),'AuthContextCryptoException':(4,2,1,0),'AuthContextCryptoException$Reason':(4,1,1,0)}
PINS={"AuthContextCodec":"6cbdc8b0bc006e036ac3e127685d06c19bbb3c1e05d854cb52c8620d6a6065d6","AuthContextIdentity":"b9dbed4233756c481cdb747d96f6de8843e9d910a4c18f51c30454d16130d7dd","EncryptedAuthContext":"d503847e6b1b1a3853033cbe82eb53678b529d616f36d1dfc0a354b3635954b7","AuthContextCryptoException":"a54b29289de7d08e01d6cbc814e9a815ae2162de559e02eebdb6e677a850066f"}
EXPECTED={'bug036CallerMonitorCannotBlockEncryptionDecryptionOrClose','independentEnvelopeAadAndDefensiveCopiesMatchExactly','currentPreviousAndEveryIdentityBindingFailClosedOnMismatch','envelopeMutationsAndAuthenticatedNonContextPlaintextAreRejected','lengthVersionKeyAndNullInvariantsIncludeBothEndpointsAndClose','jcaUnavailabilityIsTypedAndProvidersAreRestored','concurrentEncryptionHasDistinctNoncesAndCorrectRowBinding'}
TEST=PREFIX+'AuthContextCodecTest'
DOC='documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md'
NODE='/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node'
NODE_PIN='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'
JS="""const c=require('node:crypto');
const fields=['SCHUBERT-NK-AUTHCTX-v1','schubert.auth_sessions','c1000000-0000-0000-0000-000000000001','7','1','v1'];
const aad=Buffer.concat(fields.flatMap(s=>{const b=Buffer.from(s,'ascii'),n=Buffer.alloc(4);n.writeUInt32BE(b.length);return [n,b]}));
const key=Buffer.from(Array.from({length:32},(_,i)=>i)),nonce=Buffer.alloc(12,42),plain=Buffer.from('a'.repeat(64),'ascii');
const cipher=c.createCipheriv('aes-256-gcm',key,nonce);cipher.setAAD(aad);
const ciphertext=Buffer.concat([cipher.update(plain),cipher.final()]),tag=cipher.getAuthTag();
const envelope=Buffer.concat([Buffer.from('NKENC1','ascii'),Buffer.from([1,2]),Buffer.from('v1','ascii'),nonce,ciphertext,tag]);
const sha=b=>c.createHash('sha256').update(b).digest('hex');
console.log(JSON.stringify({node:process.version,openssl:process.versions.openssl,publicSyntheticFixture:true,aadHex:aad.toString('hex'),envelopeHex:envelope.toString('hex'),aadSha256:sha(aad),envelopeSha256:sha(envelope),plaintextLength:plain.length,ciphertextLength:ciphertext.length,tagLength:tag.length,envelopeLength:envelope.length}));"""
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15435-AUTH-CONTEXT-CODEC-CURRENT-WHOLE7','true fixed source/original exec')
    cases=[]
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'actual XML')
        root=ET.fromstring(b);require(root.get('name')==TEST.replace('/','.') and int(root.get('tests'))==7 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'original7 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'PASS only');cases.append((c.get('classname'),c.get('name')))
    require(len(cases)==len(set(cases))==7 and {n for c,n in cases}==EXPECTED and not set(cases)&{(c['classname'],c['name']) for c in reg['cases']},'whole7 distinct current original cases')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    test_path='src/schubert-nk-api/src/test/java/'+TEST+'.java';test=(data.ROOT/test_path).read_text()
    require(data.sha(test.encode())==hashes[test_path]=='10b4b75bc16afe0038e05e7c14abd516e1335f51929a25a674319d7afcdda26d' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==EXPECTED,'exact whole test')
    clauses=['@Isolated(','new byte[32]','value[i] = (byte) (i + offset)','Arrays.fill(bytes, (byte) 42)','output.writeInt(value.length)','Cipher.getInstance("AES/GCM/NoPadding")','cipher.updateAAD(independentAad(identity, version))','output.write("NKENC1".getBytes(StandardCharsets.US_ASCII))','output.writeByte(version.length())','output.write(encrypted)','assertArrayEquals(expected, actual.ciphertext())','assertArrayEquals(independentAad(IDENTITY, "v1"), IDENTITY.aad("v1"))','assertNull(failure.getCause())','failure.getSuppressed().length','finally {','Security.insertProviderAt(original[i], i + 1)','assertArrayEquals(original, Security.getProviders())','assertEquals(100, nonces.size())']
    require(all(v in test for v in clauses) and not any(v in test for v in ['@BeforeAll','ProcessBuilder','Files.','DriverManager','TemporaryInfrastructureException','System.getenv(']),'whole reviewed independent oracle/child-local-only contracts')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT)
    require(all(v in doc.decode() for v in ['### 11.2 AES-256-GCM','magic 6 bytes "NKENC1"','nonce 12 random bytes','authentication tag 16 bytes','Current keyでwrite、current/previousでread']),'approved envelope')
    physical={PREFIX+n for n in ROWS};require(set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory'])==physical and len(p['fullSourceUnits'])==4,'whole four Source five Code')
    closure={}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==pin and name not in reg['fullSourceUnits'],'new current unchanged Source')
            group={n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}
            require(group==({name,name+'$Reason'} if short=='AuthContextCryptoException' else {name}),'exact full Jar closure');closure[name]=sorted(group)
            for n in group:
                b=jar.read(n+'.class');decoded=code.decode(b,n+'.class')
                require(data.sha(b)==p['physicalClasses'][n] and decoded['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in decoded['methods']),'all actual Code, noNoCode false label')
                expected={k:dict(missed=0,covered=count) for k,count in zip(['LINE','METHOD','CLASS','BRANCH'],ROWS[n.removeprefix(PREFIX)])}
                require(p['executable'][n]['counters']==expected,'independent exact role counters')
    require(p['completeSourceUnitClosure']==closure,'whole Source grouping')
    full={}
    for name,group in closure.items():
        values={k:dict(missed=0,covered=sum(ROWS[n.removeprefix(PREFIX)][i] for n in group)) for i,k in enumerate(['LINE','METHOD','CLASS','BRANCH'])}
        full[name]=dict(physical=group,totals=values,four100=all(v['covered']>0 for v in values.values()),metadataOnly=False,branchNaturallyZero=values['BRANCH']['covered']==0,threeCounter100=True)
    require(wire(full)==wire(p['fullSourceUnits']),'aggregate complete Source role counters')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'fourbaseline/oneUNKNOWN not inferred')
    require(len(p['owners'])==5 and sum(r['canonicalOwner']=='WBS-P007-03' for r in p['owners'].values())==4,'actual owner partition')
    command=None
    for stage in p['stages']:
        slot=Path(stage['cwd']);require(slot==data.ROOT.parent/'pgpt-runs/PG379/pg15438-auth-context-codec-seven-post-v3','own passive slot')
        label='session-identity' if 'CoverageSessionIdentity' in stage['command'] else 'coverage-audit'
        require(stage['actualExit']==0 and stage['timedOut'] is False and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'genuine passive stage')
        if label=='coverage-audit':command=stage['command']
    def exact_names(cmd):
        require(cmd is not None and cmd[-5:]==sorted(physical) and len(set(cmd[-5:]))==5 and cmd.count('ComponentCoverageDiagnostic')==1 and cmd.index('ComponentCoverageDiagnostic')+3==len(cmd)-5,'exact reader five individual names, no prefix')
    exact_names(command);negative=[]
    for label,tail in [('prefix',[PREFIX[:-1]]),('missing',sorted(physical)[:-1]),('duplicate',sorted(physical)[:-1]+[sorted(physical)[0]])]:
        bad=command[:-5]+tail
        try:exact_names(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('invalid reader contract accepted')
    old_slot=data.ROOT.parent/'pgpt-runs/PG379/pg15436-auth-context-codec-seven-post-v1'
    failed=json.loads((old_slot/'coverage-audit-stage.safe.json').read_bytes())
    require(failed['actualExit']==1 and failed['timedOut'] is False and 'exact executable inventory' in (old_slot/'coverage-audit.stderr').read_text(),'old genuine reader failure retained')
    previous=read(('PG15420-context-hash-three-post-v1','4012b66d2bae7a216495e1b73a23ea8a89c2aa5eb86766f36308d6242ccfe15e'))
    require(previous['stages'][1]['command'][-1]==PREFIX+'ContextHash' and previous['stages'][1]['actualExit']==0,'YKT old exact one nonapplicable, no replay')
    shared=(data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v2.py').read_text()
    require('*sorted(EXECUTABLE)' in shared and data.sha(shared.encode())=='4e23c3fe151c8c42c535589f9c2f39533ea7dfa000e3b036a17aaae779f08bee','YKT shared exact names nonapplicable')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','owners','reportedEnvironment','totals']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'actual fixed source/run/counters')
        require(v['tests']==7 and v['suites']==1 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['allMeasuredApplicableCountersCovered'] is True and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'actual exception B0 category, no artificial100')
        require(v['cryptoOrKeyOperationsInvoked'] is v['publicSyntheticTestKeysUsed'] is v['ownFreshJvmProviderStateOnly'] is v['childLocalJcaRegistryRestorationTested'] is True and v['cryptoOperationKind']=='AES256GCM_PUBLIC_SYNTHETIC_TEST_KEYS_ONLY' and v['onlyReviewedPureValueSuites'] is False,'truthful synthetic crypto flags')
        require(all(v[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','actualFilesOpenedByProduct','rootMainInvoked']) and v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['effortPercent'] is None,'no live/secret/prior/formal/effort credit')
    contract(p)
    for key,value in [('source','OLD'),('cases',[]),('totals',{}),('physicalClasses',{}),('fullSourceUnits',{}),('owners',{}),('tests',8),('suites',2),('targetUnitFour100',True),('strictFour100GateExit',0),('allMeasuredApplicableCountersCovered',False),('singleSession',False),('crcMismatch',1),('metadataClasses',[PREFIX+'AuthContextCryptoException$Reason']),('manualCounterExclusions',['crypt']),('cryptoOrKeyOperationsInvoked',False),('publicSyntheticTestKeysUsed',False),('cryptoOperationKind','NO_KEYS'),('ownFreshJvmProviderStateOnly',False),('childLocalJcaRegistryRestorationTested',False),('onlyReviewedPureValueSuites',True),('actualSecretKeysLoaded',True),('actualCredentialValuesUsed',True),('actualAuthenticationOrSessionIssued',True),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('newAccepted',1),('productTestsReexecutedByPost',1),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false AES qualification')
    require(data.sha(Path(NODE).read_bytes())==NODE_PIN,'existing fixed Node binary')
    SLOT.mkdir();runner.SLOT=SLOT
    stage=runner.step('independent-node-aes-vector',[NODE,'-e',JS],SLOT,timeout=30)
    require(stage['actualExit']==0 and stage['timedOut'] is False,'independent public vector command')
    vector=json.loads((SLOT/'independent-node-aes-vector.stdout').read_text())
    fields=['SCHUBERT-NK-AUTHCTX-v1','schubert.auth_sessions','c1000000-0000-0000-0000-000000000001','7','1','v1']
    aad=b''.join(len(v.encode('ascii')).to_bytes(4,'big')+v.encode('ascii') for v in fields)
    envelope=bytes.fromhex(vector['envelopeHex'])
    require(vector['node']=='v24.19.0' and vector['openssl']=='3.5.7' and vector['publicSyntheticFixture'] is True and bytes.fromhex(vector['aadHex'])==aad and vector['aadSha256']==hashlib.sha256(aad).hexdigest(),'Node and independent Python canonical AAD')
    require(vector['plaintextLength']==vector['ciphertextLength']==64 and vector['tagLength']==16 and vector['envelopeLength']==len(envelope)==102 and envelope[:22]==b'NKENC1'+bytes([1,2])+b'v1'+bytes([42])*12 and vector['envelopeSha256']==hashlib.sha256(envelope).hexdigest(),'independent fixed public NKENC1 envelope')
    require(all(v in test for v in ['"SCHUBERT-NK-AUTHCTX-v1"','"schubert.auth_sessions"','"c1000000-0000-0000-0000-000000000001"','GCMParameterSpec(128, nonce)','"a".repeat(64)','new byte[12]','key(0)']),'fixed cross-language parameters match original independent JCE oracle')
    for v in [p,reg,previous]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=7,suites=1,newUniqueMethods=7,sourcePrograms=4,physicalClasses=5,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=0,totals=p['totals'],semanticNegativeVectors=len(negative),negativeLabels=negative,independentNodeOracle=vector,nodeCommandStage=stage,nodeBinarySha256=NODE_PIN,nodeOracleRelation='INDEPENDENT_PARAMETERS_MATCH_ORIGINAL_JCE_ORACLE_NOT_PRODUCT_CAPTURE',originalJceOracleAssertions=clauses,cryptoOrKeyOperationsInvoked=True,publicSyntheticTestKeysUsed=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,ownFreshJvmProviderStateOnly=True,baselineMainOwnerRows=4,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,authoritativeDesign=dict(path=DOC,gitRef='origin/main',sha256=data.sha(doc)),oldToolFailure=dict(entry='pg15436_auth_context_codec_seven_post.py',stage=failed),newToolExactClassNames=sorted(physical),relatedBug='BUG-2128',relatedYkt='YKT-1875',originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=7,semanticNegativeVectors=len(negative),independentAadSha256=vector['aadSha256'],independentEnvelopeSha256=vector['envelopeSha256'])))
if __name__=='__main__':main()
