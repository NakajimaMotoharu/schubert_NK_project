"""Independent SS351 thresholds/whole57/ten complete Source proof; no actual observed metrics or control."""
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

PIN='a182513b3388ad70a7d02b3057365f4ebef7805b4e68360f4f6fbe8e12c8e176'
POST=data.BASE/'PG14966-fake-source-clock-fifty-seven-post-v1'
OUT=data.BASE/'PG14968-fake-source-clock-independent-v1'
PREFIX='dev/codex/schubert/nk/batch/monitoring/'
COUNTS={'MonitoringPolicyEngineTest':9,'MonitoringStatusTextTest':6,'MonitoringPollerTest':8,'MonitoringObservationClockTest':8,'FilesystemHealthObservationTest':10,'JvmHeapHealthObservationTest':9,'MonitoringMissingObservationTest':3,'AlertRegistryTest':4}
EXPECTED={n:[] for n in ["MonitoringPolicyEngine","ObservationContext","MonitoringStatusText","MonitoringPoller","MonitoringObservationClock","FilesystemHealthObservation","FilesystemHealthMonitor","HealthUsageRatio","JvmHeapHealthObservation","AlertRegistry"]}
NATURAL={PREFIX+n for n in ['MonitoringPolicyEngine','FilesystemHealthMonitor','JvmHeapHealthObservation']}
DOC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14964-fake-source-clock-fifty-seven-pt-v1/manifest.json','7c5f68b6bb19825a69d094e45e921525a8cd0a88bf153f6a1503d800b0259e59')
    registry=data.read_checked(data.BASE/'PG14954-current1033-timed-registry-v1/manifest.json','b8b3d535d29704fd2290b0a74702121733d04f3d1f9cf74b6a5b4adfaef7483b')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG14964-ORIGINAL-FAKE-SOURCE-CLOCK57','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole57 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==57 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all57/eight suites unique new, never prior1033 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-batch/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.batch.monitoring.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
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
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==10 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'ten entire new Source/10Code, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: seven nonempty four100, three actual B0 N/A with LMC100')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=177),METHOD=dict(missed=0,covered=48),CLASS=dict(missed=0,covered=10),BRANCH=dict(missed=0,covered=44)) and p['missedLines']==[],'actual ten-class counters, not union')
    require(len(p['owners'])==18,'only ten Main/eight whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()) and expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-09' and expected['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','current approved-rule candidate ownership never baseline/accepted')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==57 and v['suites']==8 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('tests',56),('suites',7),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false fake-source57 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=57,suites=8,newUniqueMethods=57,sourcePrograms=10,physicalClasses=10,four100SourcePrograms=7,naturallyBranchZeroSourcePrograms=3,naturallyBranchZeroPhysicalClasses=3,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentThresholdRows=12,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),independentThresholdTableSha256=data.sha(json.dumps(expected_rows,ensure_ascii=False).encode()),candidateOwnerRows=18,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()

