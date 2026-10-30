"""Independent SS314 authorization policy matrix2; complete three Sources, no real authentication."""
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

POST=('PG15392-pure-authorization-two-post-v2','baa867dc17450ec2c1d8e85d62abc23a7f6ce86543fda6a5d0136b16d622d495')
RAW=('PG15390-pure-authorization-two-pt-v1','a089e2fca2e137e95e64431b841ab6af80bd93d4f2c025e0e52f5d77a1c6a122')
REG=('PG15374-current1795-time-login-registry-v1','d245e0fbad5b2b3436b4d2338e82318352ffd0e457190aaccd33fc98f1218f17')
OUT=data.BASE/'PG15394-pure-authorization-two-independent-v1'
PREFIX='dev/codex/schubert/nk/api/security/'
NAMES=['AuthorizationService','AuthorizationException','AuthenticatedActor']
TEST=PREFIX+'AuthorizationServiceTest'
TOTALS={'LINE':dict(missed=0,covered=34),'METHOD':dict(missed=0,covered=9),'CLASS':dict(missed=0,covered=3),'BRANCH':dict(missed=0,covered=24)}
DOC='documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15390-ORIGINAL-AUTHORIZATION2','genuine source/current session')
    expected={'literalOwnerAndAdminMatrixNeverExposesOtherNotifications','actorOwnerAndErrorNullInvariantsFailAtBoundaries'};actual=[]
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'actual XML')
        root=ET.fromstring(b);require(root.get('name')==TEST.replace('/','.') and int(root.get('tests'))==2 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole2 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==2 and {n for c,n in actual}==expected and not set(actual)&{(c['classname'],c['name']) for c in reg['cases']},'current original unique2')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    path='src/schubert-nk-api/src/test/java/'+TEST+'.java';test=(data.ROOT/path).read_text()
    require(data.sha((data.ROOT/path).read_bytes())==hashes[path]=='f290e044393ebbdd7778fdf474aaff8a211987c8f9c7686cba60591ef1aa465b' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==expected,'whole Test source/IDs')
    tokens=['new AuthenticatedActor(7, "synthetic-user", role)','service.requireNotificationOwner(actor, 7)','service.requireQuestionOwner(actor, 7)','service.requireNotificationOwner(actor, 8)','assertEquals(ResultCode.NOT_FOUND, notification.resultCode())','"operation is not available"','assertNull(notification.getCause())','if (role == Role.ADMIN)','service.requireAdmin(actor)','service.requireQuestionOwner(actor, 8)','ResultCode.FORBIDDEN','999_999_999_999L','1_000_000_000_000L','"é".repeat(32) + "x"','new AuthenticatedActor(1, null, Role.USER)','new AuthenticatedActor(1, "u", null)','service.requireAdmin(null)','service.requireNotificationOwner(null, 1)','service.requireQuestionOwner(null, 1)','new AuthorizationException(null)','new AuthorizationException(ResultCode.SUCCESS)']
    require(all(t in test for t in tokens) and not any(t in test for t in ['ApiLogDatabaseFixture','TemporaryInfrastructureException','getConnection(','@BeforeAll']),'independent literal matrix/null/N12/UTF8 and bounded JDK exception only')
    matrix=[['USER','admin',None,'FORBIDDEN'],['ADMIN','admin',None,'ALLOW'],['USER','notification','OWN','ALLOW'],['USER','notification','OTHER','NOT_FOUND'],['ADMIN','notification','OWN','ALLOW'],['ADMIN','notification','OTHER','NOT_FOUND'],['USER','question','OWN','ALLOW'],['USER','question','OTHER','NOT_FOUND'],['ADMIN','question','OWN','ALLOW'],['ADMIN','question','OTHER','ALLOW']]
    require(len(matrix)==10 and sum(r[3]=='ALLOW' for r in matrix)==6 and sum(r[3]=='NOT_FOUND' for r in matrix)==3 and len('é'.encode())*32==64 and len(('é'*32+'x').encode())==65,'ten independent SS policy decisions and UTF8 boundary')
    doc=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);text=doc.decode().split('## 9. 認可・owner検証')[1]
    require(all(t in text for t in ['notification owner=actor。ADMIN拡張なし','USER SQLはowner必須、ADMIN handlerだけ全scope','User管理','Application Service','Repository SQL']),'approved layered owner matrix, not runtime/SQL authorization')
    closures={PREFIX+n:[PREFIX+n] for n in NAMES};require(p['completeSourceUnitClosure']==closures and not closures.keys()&reg['fullSourceUnits'].keys(),'all three new complete Sources')
    computed={k:dict(missed=0,covered=0) for k in TOTALS}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'entire physical Jar closure')
            b=jar.read(name+'.class');require(data.sha(b)==p['physicalClasses'][name] and code.decode(b,name+'.class')['methods']==p['sourcePhysicalInventory'][name]['methods'],'actual retained Code')
            unit=p['fullSourceUnits'][name];c=p['executable'][name]['counters'];require(c==unit['totals'] and unit['physical']==closure and unit['four100'] is unit['threeCounter100'] is True and unit['branchNaturallyZero'] is False and all(v['missed']==0 and v['covered']>0 for v in c.values()),'three entire nonempty four100 Sources')
            for k in computed:
                for role in computed[k]:computed[k][role]+=c[k][role]
    require(computed==p['totals']==TOTALS and p['missedLines']==[],'34L9M3C24B missed0')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==4,'three Main/one Test')
    for path,row in p['owners'].items():
        require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual baseline pair/UNKNOWN retained')
        require((row['canonicalOwner']=='WBS-P007-03' and row['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE') if '/src/main/' in path else row['ownershipStatus']=='UNKNOWN','no inferred Test owner or change-owner transfer')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','profile']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'all exact source/run/counter/owner semantics')
        require(v['tests']==2 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'entire policy Source nonempty four100')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is v['cryptoOrKeyOperationsInvoked'] is False and v['effortPercent'] is None,'no actual auth/IO/old/formal credit')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',3),('suites',2),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',[PREFIX+'AuthenticatedActor']),('manualCounterExclusions',['requireOwnerId']),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('cryptoOrKeyOperationsInvoked',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false authorization proof accepted')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=2,suites=1,newUniqueMethods=2,sourcePrograms=3,physicalClasses=3,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=0,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentPolicyMatrix=matrix,independentOracleTokens=tokens,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),sha256=data.sha(doc)),baselineMainOwnerRows=3,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
