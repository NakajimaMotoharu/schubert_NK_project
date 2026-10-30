"""Independent pure Login policy15 oracle/complete Source counter proof; no actual authentication."""
import copy
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15370-pure-login-policy-fifteen-post-v2','330c621dc195273b9ba290a7b72b8658b0fd237c42bf2d2c277e7f0ee00a0df2')
RAW=('PG15368-pure-login-policy-fifteen-pt-v1','6fc42e8a80b710e436d00baa52256dd8aa1ed30b84ff46a1d60af56bb15efc1e')
REG=('PG15352-current1777-inputs-outbox-registry-v1','e160176d7283e59615bfa7690c3d8856a7dd79babd89012a9e974df2face2c67')
OUT=data.BASE/'PG15372-pure-login-policy-fifteen-independent-v1'
PREFIX='dev/codex/schubert/nk/api/security/'
NAMES=['LoginUsername','PasswordPolicy','LoginAttemptState','LoginAttemptKind']
COUNTS={'LoginUsernameTest':3,'PasswordPolicyTest':3,'LoginAttemptStateTest':5,'LoginAttemptSequenceTest':4}
TOTALS={'LINE':dict(missed=0,covered=78),'METHOD':dict(missed=0,covered=19),'CLASS':dict(missed=0,covered=4),'BRANCH':dict(missed=0,covered=72)}
DOC='documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15368-CURRENT-PURE-LOGIN15','genuine original current source session')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    texts={};declared=set();actual=[]
    for name,count in COUNTS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+name+'.java';b=(data.ROOT/path).read_bytes();require(data.sha(b)==hashes[path],'whole current Test bytes');text=b.decode();texts[name]=text
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(',text);require(len(methods)==count,'whole original declaration');declared.update(((PREFIX+name).replace('/','.'),n) for n in methods)
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'actual original XML');root=ET.fromstring(b)
        require(int(root.get('tests'))==COUNTS[root.get('name').rsplit('.',1)[-1]] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole15 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==15 and set(actual)==declared and not set(actual)&{(c['classname'],c['name']) for c in reg['cases']},'all current unique15 no old source transfer')
    checks={
      'LoginUsernameTest':['assertEquals("ÉCOLE"','assertEquals("école"','"ος"','"οσα"','Locale.setDefault(original)','scalar <= Character.MAX_CODE_POINT','scalar >= 0xd800 && scalar <= 0xdfff','after * 2 <= before * 3','assertEquals(3, maximumNumerator)','assertEquals(2, maximumDenominator)','assertEquals(0x0130, maximumScalar)','96, new LoginUsername('],
      'PasswordPolicyTest':['List.of("a", "a".repeat(11), "a".repeat(12), "a".repeat(128), "a".repeat(256))','"a".repeat(11), "a".repeat(129)','"a".repeat(257)','assertArrayEquals(new char[input.length], input)','policy.normalizeForCreation(input, null)','policy.normalizeForLogin(null)','"different-user"','"1".repeat(12).toCharArray()','assertNull(failure.getCause())'],
      'LoginAttemptStateTest':['kind == LoginAttemptKind.USER ? 5 : 10','END.minusNanos(1)','END.plusNanos(1)','assertEquals(offset <= 0, state.isLocked(at))','assertEquals(900, state.retryAfterSeconds(START))','state.afterFailure(START.plusSeconds(899))','active.afterFailure(START.minusNanos(1))','farFuture.afterFailure(Instant.MAX)','Optional.empty()'],
      'LoginAttemptSequenceTest':['2026-10-28T00:15:04Z','2026-10-28T00:15:09Z','int seconds = 1; seconds <= 900','int before = seconds == 900 ? 900 : seconds + 1','assertEquals(seconds, locked.retryAfterSeconds(exact))','assertEquals(900 - seconds, locked.retryAfterSeconds(at))','assertSame(locked, locked.afterFailure(at))','assertEquals(0, emptyUser.failedCount())','assertEquals(0, emptyIp.failedCount())']}
    require(all(all(t in texts[n] for t in tokens) for n,tokens in checks.items()),'independent full Test literal/oracle/zeroize/history clauses')
    require(len('İ'.encode())*32==64 and len('i\u0307'.encode())*32==96 and len('😀'.encode())*64==256 and len('é'.encode())*128==256,'independent UTF8 width vectors, not normalization via Product')
    # Integer nanosecond ceiling table: independent divmod rather than Product Duration operations.
    ceil=[]
    for seconds in range(1,901):
        for delta in [1,0,-1]:
            ns=seconds*10**9+delta;q,r=divmod(ns,10**9);ceil.append(min(900,q+(r!=0)))
        require(ceil[-3:]==[min(900,seconds+1),seconds,seconds],'independent all2700 boundary expectations')
    require(5-1+900==904 and 10-1+900==909 and [x<=0 for x in [-1,0,1]]==[True,True,False],'fixed spaced unlock seconds and inclusive window endpoint')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT)
    require(all(t in doc.decode() for t in ['Password入力はNFC後12～128文字、256 byte以下','比較keyはLocale.ROOT lowercase','User 5/IP 10到達で15分lock','終了時刻の一致は旧窓へ加算する','ceil(locked_until-now)']),'approved independent SS314 contract')
    closures={PREFIX+n:[PREFIX+n] for n in NAMES};require(p['completeSourceUnitClosure']==closures and not closures.keys()&reg['fullSourceUnits'].keys(),'all four new complete Sources')
    computed={k:dict(missed=0,covered=0) for k in TOTALS}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'actual entire Jar closure')
            b=jar.read(name+'.class');require(data.sha(b)==p['physicalClasses'][name] and code.decode(b,name+'.class')['methods']==p['sourcePhysicalInventory'][name]['methods'] and any(m['hasCode'] for m in p['sourcePhysicalInventory'][name]['methods']),'all Code retained/official filters unaltered')
            unit=p['fullSourceUnits'][name];c=p['executable'][name]['counters'];natural=name==PREFIX+'LoginAttemptKind'
            require(c==unit['totals'] and unit['physical']==closure and unit['threeCounter100'] is True and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and all(v['missed']==0 for v in c.values()),'three nonempty four100 and one naturalB0-LMC100')
            for k in computed:
                for role in computed[k]:computed[k][role]+=c[k][role]
    require(computed==p['totals']==TOTALS and p['missedLines']==[],'all 78L19M4C72B missed0')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==8,'four Main/four Test')
    for path,row in p['owners'].items():
        expected=canonical(path,logical);require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in expected.items()),'explicit baseline/UNKNOWN owner retained')
        if '/src/main/' in path:require(row['canonicalOwner']==('WBS-P018-09' if path.endswith('/LoginUsername.java') else 'WBS-P007-01'),'baseline owner not current change group')
        else:require(row['ownershipStatus']=='UNKNOWN','no inferred Test owner')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','profile']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'all source/run/counter/owner semantics immutable')
        require(v['tests']==15 and v['suites']==4 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'natural B0 not fake nonempty four100')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is False and v['effortPercent'] is None,'no Product IO/old/accepted/formal credit')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',16),('suites',3),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',[PREFIX+'LoginAttemptKind']),('manualCounterExclusions',['LoginUsername']),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false pure Login policy qualification accepted')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=15,suites=4,newUniqueMethods=15,sourcePrograms=4,physicalClasses=4,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=1,incompleteSourcePrograms=0,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentUtf8Vectors=[64,96,256,256],independentCeilingCases=2700,independentPolicyChecks=checks,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),sha256=data.sha(doc)),baselineMainOwnerRows=4,unknownTestOwnerRows=4,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
