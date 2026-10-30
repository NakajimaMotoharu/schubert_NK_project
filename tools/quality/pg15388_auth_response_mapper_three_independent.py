"""Independent UI234 wire golden bytes and whole Mapper3/source counters; no Product replay."""
import copy
import datetime
import hashlib
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15386-auth-response-mapper-three-post-v2','5aefc24bbc8bbd2ecb6a36bafe8ed439ee3208da641771c8e8787efe54d3b59b')
RAW=('PG15384-auth-response-mapper-three-pt-v1','f32bdb8fa5350ca001c9454587ba5cc3140500fb92d74672fe7b5b69e83ea492')
REG=('PG15374-current1795-time-login-registry-v1','d245e0fbad5b2b3436b4d2338e82318352ffd0e457190aaccd33fc98f1218f17')
OUT=data.BASE/'PG15388-auth-response-mapper-three-independent-v1'
NAME='dev/codex/schubert/nk/api/security/AuthenticationResponseMapper'
TEST=NAME+'Test'
DOC='documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md'
TOTALS={'LINE':dict(missed=0,covered=34),'METHOD':dict(missed=0,covered=6),'CLASS':dict(missed=0,covered=1),'BRANCH':dict(missed=0,covered=6)}
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15384-ORIGINAL-AUTH-RESPONSE3','genuine source/current session')
    expected={'loginSuccessMatchesIndependentUserAndAdminByteVectors','failuresLocksAndInfrastructureNeverExposeIdentity','logoutNullAndBoundaryResultsPreserveTheOriginalInstant'};actual=[]
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'actual whole XML')
        root=ET.fromstring(b);require(root.get('name')==TEST.replace('/','.') and int(root.get('tests'))==3 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole3 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==3 and {n for c,n in actual}==expected and not set(actual)&{(c['classname'],c['name']) for c in reg['cases']},'original new current3, never old-source transfer')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    path='src/schubert-nk-api/src/test/java/'+TEST+'.java';test=(data.ROOT/path).read_text()
    require(data.sha((data.ROOT/path).read_bytes())==hashes[path]=='d42472923a2399840df438ba00f9cf6e46619bc4fff1f567a8a46e99c98116ec' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==expected,'whole original Test declarations and byte pin')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);text=doc.decode()
    part=text.split('### 3.2')[1].split('## 4.')[0]
    fields=[(n,int(a),int(b)) for n,a,b in re.findall(r'^\| ([^|]+?) \| ([0-9]+) \| ([0-9]+) \|',part,re.M)]
    require(fields==[('Username',1,64),('Role',65,5),('認証context ID',70,64),('発行日時',134,17),('期限日時',151,17),('Retry after秒',168,6),('残り試行回数',174,3),('利用者message',177,256)],'independent authoritative one-based offset/length table')
    logout=text.split('### 4.2')[1].split('## 5.')[0]
    require([(n,int(a),int(b)) for n,a,b in re.findall(r'^\| ([^|]+?) \| ([0-9]+) \| ([0-9]+) \|',logout,re.M)]==[('Session失効日時',1,17),('Reserved',18,7)],'24-byte authoritative logout')
    require(all(v in test for v in ['new byte[432]','put(bytes, 167, "000000000")','put(expected, 0, "利用者")','put(expected, 64, role == Role.ADMIN ? "ADMIN" : "USER")','put(expected, 69, "a".repeat(64))','put(expected, 133, "20260908100203456")','put(expected, 150, "20260908180203456")','put(expected, 167, retry == 1 ? "000001" : "000900")','put(failure, 176,','assertArrayEquals(expected, actual.copyData())','assertEquals(0, actual.recordCount())','assertEquals(0, actual.recordLength())','mapper.login(null)','mapper.logout(null)','Executors.newFixedThreadPool(16)']),'independent whole byte/null/concurrent oracle, not production encode as expected')
    vectors=[]
    def login(label,changes):
        b=bytearray(b' '*432);b[167:176]=b'000000000'
        for field,value in changes.items():
            _,start,length=next(row for row in fields if row[0]==field);v=value.encode('utf8');require(len(v)<=length,'independent field bound');b[start-1:start-1+len(v)]=v
        vectors.append(dict(label=label,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
        return b
    for role in ['USER','ADMIN']:
        b=login('success-'+role,{'Username':'利用者','Role':role,'認証context ID':'a'*64,'発行日時':'20260908100203456','期限日時':'20260908180203456'})
        require(b[:9]=='利用者'.encode() and b[9:64]==b' '*55 and b[167:176]==b'000000000','UTF8 byte padding and zero digits')
    messages={'failure':'ユーザー名またはパスワードが正しくありません。','locked':'ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。','temporary':'現在処理できません。しばらくしてから再操作してください。'}
    for label,retry in [('failure',0),('locked',1),('locked',900),('temporary',0)]:
        require(messages[label] in test,'independent original message literal');b=login(label+'-'+str(retry),{'Retry after秒':str(retry).zfill(6),'利用者message':messages[label]});require(b[:167]==b' '*167,'error response has no identity')
    dates=['2026-09-08T01:02:03.456789+00:00','2026-09-08T01:02:03.456789+00:00','2026-09-08T01:02:03.999999+00:00','2026-09-08T01:02:04.000000+00:00','2026-09-08T01:02:04.000001+00:00']
    strings=['20260908100203456','20260908100203456','20260908100203999','20260908100204000','20260908100204000']
    for index,(source,expected_text) in enumerate(zip(dates,strings)):
        at=datetime.datetime.fromisoformat(source).astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        stamp=at.strftime('%Y%m%d%H%M%S')+str(at.microsecond//1000).zfill(3);require(stamp==expected_text and expected_text in test,'independent JST +9h and millis floor')
        b=(stamp+' '*7).encode('ascii');require(len(b)==24,'logout exact byte length');vectors.append(dict(label='logout-'+str(index),bytes=24,sha256=hashlib.sha256(b).hexdigest()))
    require(len(vectors)==11 and len({v['sha256'] for v in vectors})==9,'eleven golden expectations/nine distinct hashes, not new Test IDs')
    require(p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['physicalClasses'])==set(p['executable'])=={NAME} and NAME not in reg['fullSourceUnits'],'full new Mapper Source')
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        require({n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}=={NAME},'entire class closure')
        b=jar.read(NAME+'.class');require(data.sha(b)==p['physicalClasses'][NAME] and code.decode(b,NAME+'.class')['methods']==p['sourcePhysicalInventory'][NAME]['methods'],'all actual Code retained')
    require(p['executable'][NAME]['counters']==p['totals']==p['fullSourceUnits'][NAME]['totals']==TOTALS and p['missedLines']==[],'independent complete Source 34L6M1C6B missed0')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'baseline Main/UNKNOWN Test retained')
    require(len(p['owners'])==2 and p['owners']['src/schubert-nk-api/src/main/java/'+NAME+'.java']['canonicalOwner']=='WBS-P007-04','actual explicit baseline')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','profile']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'all exact current source/run/counter/owner semantics')
        require(v['tests']==3 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete nonempty four100 Mapper only')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is v['cryptoOrKeyOperationsInvoked'] is False and v['effortPercent'] is None,'no real login/crypto/IO/formal transfer')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',4),('suites',2),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME]),('manualCounterExclusions',['logout']),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('cryptoOrKeyOperationsInvoked',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false Mapper qualification accepted')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=3,suites=1,newUniqueMethods=3,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentUi234Fields=fields,independentWireGoldenVectors=vectors,expectedVectorCountNotTestMethods=True,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),sha256=data.sha(doc)),baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
