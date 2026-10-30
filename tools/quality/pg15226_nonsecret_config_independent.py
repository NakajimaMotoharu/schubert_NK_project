"""Independent same-exec original14 proof; public template + SS343 literals, no product replay."""
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

PIN='5d714d963f1183844fb41f46e41ebd2e3ecece0a37d3c6d7700ca18f9a218c53'
POST=data.BASE/'PG15224-nonsecret-config-fourteen-post-v1'
OUT=data.BASE/'PG15226-nonsecret-config-independent-v1'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
DOC='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
COUNTS={"ApiNonSecretConfigTest":7,"WebNonSecretConfigTest":7}
TEST_PATHS={"ApiNonSecretConfigTest":"src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfigTest.java","WebNonSecretConfigTest":"src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfigTest.java"}
TEST_PINS={"ApiNonSecretConfigTest":"c48aaae03b6901d3511ac2cda416c0f184044b6baefcf307d64c69997937a63c","WebNonSecretConfigTest":"d56e00afaac0bfe0dd269d689b10df907a0f04a31e6021837a180ccea7f0b78b"}
PACKAGES={"ApiNonSecretConfigTest":"dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest","WebNonSecretConfigTest":"dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest"}
TEMPLATES={"src/deployment/config/common.yml.template":"d61acf911e08a15cfdb2700eb81db7bbbb920cb3ccd80f1665652af4b4b7880a","src/deployment/config/api.yml.template":"206f4ed29da0fca31c1bab15015eb5b4db93255846c411f5d1815050d66bf267","src/deployment/config/web.yml.template":"3e9a7ba4ada50e82e450cdd634439c2c122fed051de089010dee07dfd2d25cb7"}
DEFS={"dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig":["44f593abd6204f9dbc9ebf672405e4adac7ff793f16c91c71f411d21d3b8ac45",[]],"dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfig":["a0254c980bdbead9800395cc2ea98704708cda4d7d81763fcd4d67b64f1c7620",[]]}
def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15222-nonsecret-config-fourteen-pt-v1/manifest.json','74ac8c3a3c38d50da20e80ca81a75d59dd2295d61d3ffec11368f59857959c73')
    registry=data.read_checked(data.BASE/'PG15212-current1697-borrowed-outbox-registry-v1/manifest.json','1aa2ef15483fc5f64130c25ac6de40de80ed860d1debd4659aac82b722f816cc')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']==SOURCE and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15222-ORIGINAL-NONSECRET-CONFIG14','genuine own source run')
    hashes=normal['begin']['inputHashes'];actual=[]
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1]
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'original whole FES0')
        for c in root.findall('testcase'):require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    declared=set()
    for simple,path in TEST_PATHS.items():
        text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==TEST_PINS[simple],'whole Test source bytes')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==COUNTS[simple],'all declared methods');declared.update((PACKAGES[simple],n) for n in methods)
    require(len(p['xmlHashes'])==2 and len(actual)==len(set(actual))==14 and set(actual)==declared=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all fourteen new unique IDs')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    section=document.decode().split('## 4. Config file・設定sourceの優先順',1)[1].split('## 6. Credential catalog',1)[0]
    expected_rows=[['nk.protocol.version','001'],['nk.time.display-zone','Asia/Tokyo'],['nk.monitoring.mode','STANDARD'],['nk.web.http.address/port','127.0.0.1 / 8080'],['nk.web.management.port','8081'],['nk.web.mq.reply-timeout','2s'],['nk.web.mq.wait.initial/max','12 / 20'],['nk.web.session.idle-timeout','8h'],['nk.web.session.max-per-user','2'],['nk.web.media.max-streams','20'],['nk.web.media.max-range-bytes','1048576'],['nk.mq.url','tcp://127.0.0.1:61616'],['nk.api.sync-consumers.initial/max','4 / 8'],['nk.api.async-consumers','1'],['nk.db.url','jdbc:postgresql://127.0.0.1:5432/schubert_nk'],['nk.db.pool.api.max/min','8 / 2'],['nk.db.pool.web.max/min','2 / 1'],['nk.db.connect-timeout','3s'],['nk.inbox.reference/update-retention','24h / 7d'],['nk.outbox.sent-retention','7d']]
    observed={}
    for line in section.splitlines():
        if not line.startswith('| '):continue
        fields=[v.strip().replace(chr(96),'') for v in line.split('|')[1:-1]]
        if fields[0] in {r[0] for r in expected_rows}:require(fields[0] not in observed,'unique key');observed[fields[0]]=fields[1]
    require(observed==dict(expected_rows),'independent twenty approved SS343 key/value rows')
    common={'nk.db.connect-timeout':'3s','nk.db.url':'jdbc:postgresql://127.0.0.1:5432/schubert_nk','nk.monitoring.mode':'STANDARD','nk.mq.url':'tcp://127.0.0.1:61616','nk.protocol.version':'001','nk.time.display-zone':'Asia/Tokyo'}
    api={**common,'nk.api.async-consumers':'1','nk.api.storage.asset-manifest-entries':'59627','nk.api.storage.asset-root':'/srv/schubert-nk/data/assets','nk.api.storage.transfer-root':'/srv/schubert-nk/data/transfer','nk.api.sync-consumers.initial':'4','nk.api.sync-consumers.max':'8','nk.db.pool.api.max':'8','nk.db.pool.api.min':'2','nk.inbox.reference-retention':'24h','nk.inbox.update-retention':'7d','nk.mq.async-work':'nk.async.work','nk.mq.dlq':'nk.dead.letter','nk.mq.expiry':'nk.expiry','nk.mq.sync-reply':'nk.sync.reply.web','nk.mq.sync-request':'nk.sync.request','nk.mq.web-log':'nk.web.log','nk.outbox.sent-retention':'7d'}
    web={**common,'nk.db.pool.web.max':'2','nk.db.pool.web.min':'1','nk.web.http.address':'127.0.0.1','nk.web.http.port':'8080','nk.web.management.port':'8081','nk.web.media.max-range-bytes':'1048576','nk.web.media.max-streams':'20','nk.web.mq.reply-timeout':'2s','nk.web.mq.wait.initial':'12','nk.web.mq.wait.max':'20','nk.web.session.idle-timeout':'8h','nk.web.session.max-per-user':'2','nk.web.storage.asset-root':'/srv/schubert-nk/data/assets','nk.web.storage.transfer-root':'/srv/schubert-nk/data/transfer'}
    golden_hashes={}
    for simple,values in [('ApiNonSecretConfigTest',api),('WebNonSecretConfigTest',web)]:
        text=(data.ROOT/TEST_PATHS[simple]).read_text();declaration=text.split('private static final String GOLDEN =',1)[1].split(';',1)[0]
        literal=''.join(json.loads(v) for v in re.findall(r'"(?:\\.|[^"\\])*"',declaration));expected=''.join(k+'='+values[k]+chr(10) for k in sorted(values))
        require(literal==expected and len(values)==(23 if simple.startswith('Api') else 20) and 'MessageDigest.getInstance("SHA-256")' in text and '.digest(GOLDEN.getBytes(StandardCharsets.UTF_8))' in text,'independent sorted literal SHA256 oracle')
        golden_hashes[simple]=data.sha(expected.encode())
    snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    for path,h in TEMPLATES.items():require(data.sha((snapshot/path).read_bytes())==data.sha((data.ROOT/path).read_bytes())==hashes[path]==h==data.sha(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT)),'public template current/snapshot/source identity')
    require(p['publicTemplateHashes']==TEMPLATES and p['repositorySnapshotProperty']=='-Dnk.pt.repository='+str(snapshot) and raw['stages'][1]['command'].count(p['repositorySnapshotProperty'])==1 and p['actualPrivateConfigRead'] is False,'snapshot property only')
    closures={n:[n] for n in DEFS};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==closures.keys() and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'two actual complete new Sources')
    with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:
        for n in closures:
            require({v[:-6] for v in jar.namelist() if v==n+'.class' or v.startswith(n+'$') and v.endswith('.class')}=={n},'full nested closure')
            v=jar.read(n+'.class');parsed=code.decode(v,n+'.class');require(data.sha(v)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'actual executable Code identity')
            unit=p['fullSourceUnits'][n];local=p['executable'][n]['counters'];require(unit['totals']==local and unit['four100'] is True and unit['threeCounter100'] is True and unit['branchNaturallyZero'] is False and all(c['missed']==0 and c['covered']>0 for c in local.values()),'nonempty four counters all100')
            path='src/schubert-nk-bootstrap/src/main/java/'+n+'.java';require(hashes[path]==DEFS[n][0],'Main source pin')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=237),METHOD=dict(missed=0,covered=25),CLASS=dict(missed=0,covered=2),BRANCH=dict(missed=0,covered=150)) and p['missedLines']==[],'measured counters not a union')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==4,'four owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()),'canonical byte/owner identity')
        if '/src/main/java/' in path:require(expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-01' and expected['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','Main baseline logical only')
        else:require(expected['canonicalOwner'] is expected['canonicalCostOwner'] is None and expected['ownershipStatus']=='UNKNOWN','Test unknown not inferred')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes','publicTemplateHashes','repositorySnapshotProperty']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'immutable actual proof')
        require(v['tests']==14 and v['suites']==2 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['manualCounterExclusions']==[] and v['metadataClasses']==[],'all whole counters/IDs')
        require(v['ownChildJvmStandardSdkObserved'] is v['forcedGcOrHeapDump'] is v['externalVmOrTargetProcessObserved'] is v['actualPrivateConfigRead'] is False and v['baselineMainOwnerRows']==v['unknownTestOwnerRows']==2,'no actual SDK/config/runtime/unknown promotion')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None,'no formal or historical conversion')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('cases',[]),('execSha256','0'*64),('sessionIdentity','OLD'),('physicalClasses',{}),('completeSourceUnitClosure',{}),('sourcePhysicalInventory',{}),('fullSourceUnits',{}),('totals',{}),('owners',{}),('fixtureHashes',{'x':'0'*64}),('publicTemplateHashes',{}),('repositorySnapshotProperty','/etc'),('tests',15),('suites',1),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('manualCounterExclusions',['x']),('metadataClasses',['x']),('ownChildJvmStandardSdkObserved',True),('actualPrivateConfigRead',True),('baselineMainOwnerRows',4),('unknownTestOwnerRows',0),('newAccepted',1),('formalUpdated',True),('effortPercent',100),('coverageExecUnion',True),('productTestsReexecutedByPost',1)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false qualification '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=PIN,tests=14,suites=2,newUniqueMethods=14,sourcePrograms=2,physicalClasses=2,four100SourcePrograms=2,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentInitialValueRows=20,independentGoldenSha256=golden_hashes,goldenKeyCounts=dict(api=23,web=20),authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),baselineMainOwnerRows=2,unknownTestOwnerRows=2,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
