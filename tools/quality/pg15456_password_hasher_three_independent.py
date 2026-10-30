"""Independent original PasswordHasher3/full Source with public synthetic PBKDF2 oracle."""
import copy
import hashlib
import json
import re
from pathlib import Path
import subprocess
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15454-password-hasher-three-post-v1','20b1787d8803c86bb0f3c65de60bbe74e063ad60156e860ae230ad86ba4fba91')
RAW=('PG15452-password-hasher-three-pt-v1','8ed0341660234dc97d19c757b8cfcfe2baa8130b33e88d8c86820bba00d9265c')
REG=('PG15442-current1810-auth-context-codec-registry-v1','e94941427a78ea47d0b82eabbcffd19400909efb16b939c3216a30cc6aed897c')
OUT=data.BASE/'PG15456-password-hasher-three-independent-v1'
NAME='dev/codex/schubert/nk/api/security/PasswordHasher';TEST=NAME+'Test'
TOTALS={k:dict(missed=0,covered=v) for k,v in [('LINE',19),('METHOD',5),('CLASS',1),('BRANCH',2)]}
EXPECTED={'fixedSaltIndependentPbkdf2VectorAndNfcMatch','encodeUsesFreshSaltAndFull256BytePassword','invalidStoredGenerationAndInputsAreBoundedAndConsumed'}
DOC='documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15452-PASSWORD-HASHER-CURRENT-WHOLE3','current true original source/session')
    cases=[]
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'original XML')
        root=ET.fromstring(b);require(root.get('name')==TEST.replace('/','.') and int(root.get('tests'))==3 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole3 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');cases.append((c.get('classname'),c.get('name')))
    require(len(cases)==len(set(cases))==3 and {n for c,n in cases}==EXPECTED and not set(cases)&{(c['classname'],c['name']) for c in reg['cases']},'new current three original cases')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    test_path='src/schubert-nk-api/src/test/java/'+TEST+'.java';test=(data.ROOT/test_path).read_text()
    require(data.sha(test.encode())==hashes[test_path]=='a44c27a8e9b3869fd01ef90dae2a28bfebc0f5f78b4bd0d417b12eb3b319daae' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==EXPECTED,'whole original source')
    clauses=['salt[i] = (byte) i','PBEKeySpec(value.toCharArray(), salt, 310_000, 256)','SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")','spec.clearPassword()','HexFormat.of().formatHex(salt)','HexFormat.of().formatHex(derived)','Arrays.copyOf(firstBytes, 16)','Arrays.copyOf(secondBytes, 16)','assertEquals(independentHash(value, Arrays.copyOf(firstBytes, 16)), first)','assertArrayEquals(new char[input.length], input)','assertNull(failure.getCause())','"stored password encoding is invalid or unsupported"']
    require(all(v in test for v in clauses) and not any(v in test for v in ['@BeforeAll','ProcessBuilder','Files.','DriverManager','TemporaryInfrastructureException','Security.removeProvider','System.getenv(']),'independent JCE oracle/negative/redaction/zeroize, no provider/IO/Graph')
    password=unicodedata.normalize('NFC','e\u0301'*12);salt=bytes(range(16))
    require(password=='é'*12 and len(password.encode('utf8'))==24 and len(('é'*128).encode('utf8'))==256,'independent NFC/UTF8 fixed fixtures')
    derived=hashlib.pbkdf2_hmac('sha256',password.encode('utf8'),salt,310000,32)
    encoded='{pbkdf2-v1}'+salt.hex()+derived.hex()
    require(len(derived)==32 and re.fullmatch(r'\{pbkdf2-v1}[0-9a-f]{96}',encoded) is not None and len(encoded.encode('ascii'))<255,'independent Python PBKDF2 parameter/vector/DB bound')
    require(hashlib.pbkdf2_hmac('sha256',('other'*3).encode(),salt,310000,32)!=derived and hashlib.pbkdf2_hmac('sha256',('e\u0301'*12).encode(),salt,310000,32)!=derived,'independent mismatch and NFC-required negatives')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT)
    require(all(v in doc.decode() for v in ['PBKDF2-HMAC-SHA256、salt 16 byte、310,000 iteration、derived key 256 bit、additional secret空','setEncodeHashAsBase64(false)','char[]','zero fill']),'approved parameter/erasure contract')
    path='src/schubert-nk-api/src/main/java/'+NAME+'.java';main=(data.ROOT/path).read_text()
    require(data.sha(main.encode())==hashes[path]=='af26da6781015b67cf36a6e35497c334dd1eadf05e00da38f1e2c43460d91baf' and all(v in main for v in ['Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8()','v1.setEncodeHashAsBase64(false)','new DelegatingPasswordEncoder("pbkdf2-v1", Map.of("pbkdf2-v1", v1))','policy.normalizeForLogin(password)']),'unchanged generation-pinned source')
    require(p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['physicalClasses'])==set(p['executable'])=={NAME} and NAME not in reg['fullSourceUnits'],'one full new Source')
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        require({n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}=={NAME},'whole Jar closure')
        b=jar.read(NAME+'.class');decoded=code.decode(b,NAME+'.class')
        require(data.sha(b)==p['physicalClasses'][NAME] and decoded['methods']==p['sourcePhysicalInventory'][NAME]['methods'] and {m['name'] for m in decoded['methods'] if m['hasCode']}=={'<init>','encode','matches','needsUpgrade','requireHash'},'all five actual Code methods')
    require(p['executable'][NAME]['counters']==p['totals']==p['fullSourceUnits'][NAME]['totals']==TOTALS,'actual independent19L5M1C2B allmiss0')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'baseline source/UNKNOWN Test, not engineering-owner inference')
    main_path='src/schubert-nk-api/src/main/java/'+NAME+'.java'
    require(len(p['owners'])==2 and p['owners'][main_path]['canonicalOwner']=='WBS-P007-01','actual owner roles')
    crypto=[(path,pin) for path,pin in raw['begin']['dependencyHashes'].items() if '/spring-security-crypto/' in path]
    require(len(crypto)==1 and crypto[0][1]=='6e8bb2337faccabd30626f917ed1d2bfa9dde982229b6b373b644d1a01635403' and all(data.sha(Path(path).read_bytes())==pin for path,pin in crypto),'fixed normal runtime, not stale M2')
    for stage in p['stages']:
        slot=Path(stage['cwd']);require(slot==data.ROOT.parent/'pgpt-runs/PG379/pg15454-password-hasher-three-post-v1','own passive tool slot')
        label='session-identity' if 'CoverageSessionIdentity' in stage['command'] else 'coverage-audit'
        require(stage['actualExit']==0 and stage['timedOut'] is False and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'actual original passive receipt hashes')
        if label=='coverage-audit':require(stage['command'][-1]==NAME,'exact single class reader name')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','reportedEnvironment']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'actual exact source/run/owner/counters')
        require(v['tests']==3 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[] and v['naturalZeroBranch'] is False and v['branchPercent']==100,'actual all four100, naturalB0 false')
        require(v['allMeasuredApplicableCountersCovered'] is True and v['fullSourceUnits'][NAME]['four100'] is True,'all applicable closed')
        require(v['cryptoOrKeyOperationsInvoked'] is v['publicSyntheticTestPasswordsUsed'] is v['ownFreshJvmProviderStateOnly'] is True and v['cryptoOperationKind']=='PBKDF2_HMACSHA256_PUBLIC_SYNTHETIC_PASSWORD_AND_SALT' and v['childLocalJcaRegistryRestorationTested'] is False and v['onlyReviewedPureValueSuites'] is False,'truthful synthetic crypto, no provider mutation')
        require(all(v[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','actualFilesOpenedByProduct','rootMainInvoked']) and v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['effortPercent'] is None,'no actual secrets/auth/IO/old/formal/effort')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',4),('suites',2),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME]),('manualCounterExclusions',['encode']),('naturalZeroBranch',True),('branchPercent',0),('allMeasuredApplicableCountersCovered',False),('cryptoOrKeyOperationsInvoked',False),('publicSyntheticTestPasswordsUsed',False),('cryptoOperationKind','NO_CRYPTO'),('onlyReviewedPureValueSuites',True),('ownFreshJvmProviderStateOnly',False),('childLocalJcaRegistryRestorationTested',True),('actualSecretKeysLoaded',True),('actualCredentialValuesUsed',True),('actualAuthenticationOrSessionIssued',True),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false PBKDF2 proof')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=3,suites=1,newUniqueMethods=3,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,publicIndependentPbkdf2Vector=dict(normalizedPublicUnicodeCodePoint='U+00E9 repeated12',saltHex=salt.hex(),iterations=310000,derivedBytes=32,encoded=encoded,oracle='PYTHON_HASHLIB_NOT_PRODUCTION; ORIGINAL_JCE_EXPECTED_ASSERTION_MATCHES_PRODUCT',unicodeDatabase=unicodedata.unidata_version),originalJceAssertionClauses=clauses,fixedSpringCryptoRuntime=crypto,cryptoOrKeyOperationsInvoked=True,publicSyntheticTestPasswordsUsed=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,ownFreshJvmProviderStateOnly=True,baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,authoritativeDesign=dict(path=DOC,gitRef='origin/main',sha256=data.sha(doc)),originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=3,semanticNegativeVectors=len(labels),publicIndependentEncodedVector=encoded)))
if __name__=='__main__':main()
