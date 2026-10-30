"""Independent SS351 thresholds/whole56/three complete Web Source proof; fake borrowed getters and own child SDK, no realDB."""
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

PIN='3bfa2745f68498e84cf99840121adfd628c891916d05a28b0278008fafd22b88'
POST=data.BASE/'PG15062-web-pool-context-fifty-six-post-v1'
OUT=data.BASE/'PG15064-web-pool-context-independent-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
COUNTS={"WebDbPoolMetricRecorderTest":8,"WebDbPoolMetricBindingTest":15,"WebMetricContextTest":33}
EXPECTED={"WebDbPoolMetricRecorder":["Counts","State"],"WebDbPoolMetricBinding":[],"WebMetricContext":[]}
NATURAL={PREFIX+'WebDbPoolMetricBinding'}
DOC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15060-web-pool-context-fifty-six-pt-v1/manifest.json','58b316ae27bde38797006d7e4a2a187a2abab3bd0f7c9a5f7dcea3530430c317')
    registry=data.read_checked(data.BASE/'PG15050-current1367-web-exporter-registry-v1/manifest.json','6524ae373d11f4eb8cb691deaff85aee31dc7a64b1839a59ae69bb79a923b0f6')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15060-ORIGINAL-WEB-POOL-CONTEXT56','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole56 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==56 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all56/three suites unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-web/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.web.monitoring.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    fixture_tests=['WebDbPoolMetricObservationTest']
    for simple in fixture_tests:
        relative='src/schubert-nk-web/src/test/java/'+PREFIX+simple+'.java';path=data.ROOT/relative
        require(data.sha(path.read_bytes())==hashes[relative]==raw['begin']['testSourceHashes'][str(path)] and simple not in COUNTS and not any(c.rsplit('.',1)[-1]==simple for c,n in actual),'old fixture Test sources compile-only, no old fixture methods replay/count')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    section=document.decode().split('## 7. Alert condition',1)[1].split('## 8. DEBUG/STANDARD',1)[0]
    expected_rows=[
        ['Filesystem','>=80% 5min','>=90% 1min'],
        ['Transfer','>=3.5GBまたは5,000','>=4.5GBまたは9,000'],
        ['Async Queue','>=5,000または70%','>=9,000または90%'],
        ['Web log Queue/outbox','>=5,000または最古5min','>=9,000または最古30min'],
        ['DLQ','>=1','増加または未調査'],
        ['Expiry','>=1,000','>=5,000'],
        ['DB pool','>=80% 5min','pending/timeout 1件'],
        ['JVM heap','>=75% 10min','>=90%またはOOM'],
        ['Sync p95','>2.0s 5min','>2.5s 5min'],
        ['Backup','05:00 run後当日SUCCESSなし','2回連続失敗'],
        ['Restart','1回','10分に5回・rate limit'],
        ['Integrity/config','1回','常にcritical']]
    names={row[0] for row in expected_rows};actual_rows=[]
    for line in section.splitlines():
        if line.startswith('| '):
            fields=[value.strip() for value in line.split('|')[1:-1]]
            if fields[0] in names:actual_rows.append(fields[:3])
    require(actual_rows==expected_rows and len(actual_rows)==12,'independent SS351 twelve exact threshold rows, not production-generated expected values')
    metric_rows={'nk_db_pool_connections':['gauge','service,state']}
    observed_metrics={}
    metric_section=document.decode().split('## 6. Metric catalog',1)[1].split('## 7. Alert condition',1)[0]
    for line in metric_section.splitlines():
        if not line.startswith('| '):continue
        fields=[value.strip() for value in line.split('|')[1:-1]]
        for name in re.findall(r'`([^`]+)`',fields[0]):
            if name in metric_rows:
                require(name not in observed_metrics,'no repeated approved metric row');observed_metrics[name]=fields[1:3]
    require(observed_metrics==metric_rows and len(observed_metrics)==1,'independent approved Web pool family name/type/label rows from SS351')
    require('JVM/GC/thread、Hikari、process/host/disk、PostgreSQL、Artemisは製品exporter/Micrometer標準metricを使う。' in document.decode(),'approved standard SDK selection, not an invented runtime authority')
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==5 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'three entire new Source/fiveCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: two four100 and one natural B0 Source with LMC100')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=133),METHOD=dict(missed=0,covered=31),CLASS=dict(missed=0,covered=5),BRANCH=dict(missed=0,covered=51)) and p['missedLines']==[],'actual five-class counters, not union')
    require(len(p['owners'])==6,'only three Main/three whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()) and expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-09' and expected['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','current approved-rule candidate ownership never baseline/accepted')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==56 and v['suites']==3 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is True and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',False),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=56,suites=3,newUniqueMethods=56,sourcePrograms=3,physicalClasses=5,four100SourcePrograms=2,naturallyBranchZeroSourcePrograms=1,naturallyBranchZeroPhysicalClasses=1,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentThresholdRows=12,independentMetricRows=1,independentMetricTableSha256=data.sha(json.dumps(metric_rows,sort_keys=True).encode()),authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),independentThresholdTableSha256=data.sha(json.dumps(expected_rows,ensure_ascii=False).encode()),candidateOwnerRows=6,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=True,observationScope="OWN_CHILD_JVM_ONLY",forcedGcOrHeapDump=False,externalVmOrTargetProcessObserved=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
