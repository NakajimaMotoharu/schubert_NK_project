"""Independent SS351 standard clause/whole44/three complete API Sources, own child SDK only."""
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

PIN='09fa1d277dc8424e696c6f70814c2c355e8818ca97d6801f12fcf1ec7be2e50e'
POST=data.BASE/'PG15098-api-standard-forty-four-post-v1'
OUT=data.BASE/'PG15100-api-standard-independent-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/'
COUNTS={"ApiGcMetricRegistrationTest":16,"ApiJvmMetricsTest":14,"ApiSystemMetricsTest":14}
EXPECTED={"ApiGcMetricRegistration":[],"ApiJvmMetrics":[],"ApiSystemMetrics":[]}
NATURAL=set()
DOC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15096-api-standard-forty-four-pt-v1/manifest.json','df02890ba9f2845918b5f59772972a9c1f5bfd758eb7f26106aab24d44c42059')
    registry=data.read_checked(data.BASE/'PG15086-current1467-web-standard-registry-v1/manifest.json','3afff3fa9803f14fb483a28e91a42358e9369fcf2a63eef1bee76e03c7f15542')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15096-ORIGINAL-API-STANDARD44','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole44 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==44 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all44/three suites unique new, never prior1423 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.api.monitoring.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    # Static whole-body comparison to the fully-read Web originals, never transfer PT success.
    for simple in COUNTS:
        api_path='src/schubert-nk-api/src/test/java/'+PREFIX+simple+'.java'
        web_path=api_path.replace('schubert-nk-api','schubert-nk-web').replace('/nk/api/','/nk/web/').replace('/Api','/Web')
        text=(data.ROOT/web_path).read_text()
        for old,new in [('schubert.nk.web.','schubert.nk.api.'),('Web','Api'),('WEB','API'),('webgc','apigc'),('webjvm','apijvm'),('websys','apisys'),('invalid monitoring mode','CONFIG_INVALID'),('/1787','/1785'),('/1781','/1779'),('/1791','/1789')]:text=text.replace(old,new)
        require(text==(data.ROOT/api_path).read_text() and data.sha((data.ROOT/web_path).read_bytes())==hashes[web_path],'complete original role-normalized Test bodies, no fixture differences hidden')
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
    metric_rows={}
    observed_metrics={}
    metric_section=document.decode().split('## 6. Metric catalog',1)[1].split('## 7. Alert condition',1)[0]
    for line in metric_section.splitlines():
        if not line.startswith('| '):continue
        fields=[value.strip() for value in line.split('|')[1:-1]]
        for name in re.findall(r'`([^`]+)`',fields[0]):
            if name in metric_rows:
                require(name not in observed_metrics,'no repeated approved metric row');observed_metrics[name]=fields[1:3]
    require(observed_metrics==metric_rows and len(observed_metrics)==0,'independent approved Web pool family name/type/label rows from SS351')
    require('JVM/GC/thread、Hikari、process/host/disk、PostgreSQL、Artemisは製品exporter/Micrometer標準metricを使う。' in document.decode(),'approved standard SDK selection, not an invented runtime authority')
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==3 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'three entire new Source/threeCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: three nonempty four100 Sources')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=54),METHOD=dict(missed=0,covered=13),CLASS=dict(missed=0,covered=3),BRANCH=dict(missed=0,covered=31)) and p['missedLines']==[],'actual three-class counters, not union')
    require(len(p['owners'])==6,'only three Main/three whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()) and expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-09' and expected['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','current approved-rule candidate ownership never baseline/accepted')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==44 and v['suites']==3 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is True and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',False),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-standard44 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=44,suites=3,newUniqueMethods=44,sourcePrograms=3,physicalClasses=3,four100SourcePrograms=3,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentThresholdRows=12,independentMetricRows=0,independentMetricTableSha256=data.sha(json.dumps(metric_rows,sort_keys=True).encode()),authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),independentThresholdTableSha256=data.sha(json.dumps(expected_rows,ensure_ascii=False).encode()),candidateOwnerRows=6,roleNormalizedWholeBodiesVerified=3,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=True,observationScope="OWN_CHILD_JVM_ONLY",forcedGcOrHeapDump=False,externalVmOrTargetProcessObserved=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
