"""Independent SS351-derived catalog/whole55/five complete Source proof; candidate ownership never accepted."""
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

PIN='431b26429dbe7d2e83789988d7fdb8b71c40048c52dd85b81ced32330330e1ea'
POST=data.BASE/'PG14930-batch-monitoring-pure-fifty-five-post-v1'
OUT=data.BASE/'PG14932-batch-monitoring-pure-independent-v1'
PREFIX='dev/codex/schubert/nk/batch/monitoring/'
COUNTS={'AlertLifecycleTest':12,'ContinuousConditionWindowTest':8,'MetricContractTest':6,'BatchMetricContractTest':5,'MonitoringModePolicyTest':7,'GeneratedBatchValueContractTest':7,'AlertContinuityTest':2,'MonitoringRetentionConfigurationTest':8}
EXPECTED={'AlertLifecycle':['CauseClearance','Condition','Event','Service','Severity'],'ContinuousConditionWindow':['State'],'MetricContract':['Kind'],'MonitoringModePolicy':['DetailService','RetentionConfiguration'],'BatchMetricContract':['Status','Step']}
DOC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14928-batch-monitoring-pure-fifty-five-pt-v1/manifest.json','a3f69e58778cf48e8aa307429e5bf26a428e5ed928d6160c3186347babf75b24')
    registry=data.read_checked(data.BASE/'PG14918-current934-step-registry-v1/manifest.json','d5e51d97016f1916626a6f3da771593f151236cf20d3683f0caec396c1e66de6')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG14928-ORIGINAL-BATCH-MONITORING-PURE55','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole55 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==55 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all55/eight suites unique new, never prior934 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-batch/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.batch.monitoring.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    document=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=data.ROOT);doc_head=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip();rows=[]
    for line in document.decode().splitlines():
        if line.startswith('| `nk_'):
            fields=[v.strip() for v in line.split('|')[1:-1]]
            for name in re.findall(r'`(nk_[a-z0-9_]+)`',fields[0]):rows.append([name,fields[1],fields[2]])
    fixture='src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv';value=(data.ROOT/fixture).read_bytes()
    require(len(rows)==len({r[0] for r in rows})==26 and [line.split('\t') for line in value.decode().splitlines()]==rows and data.sha(value)==p['fixtureHashes'][fixture]=='1447faabc6f056120561e4356dd75696ace4df613b6379246af29f9837fc43dc','independent authoritative SS351 catalog expansion exactly26/three columns')
    require('15日/5GB' in document.decode() and 'Warningは5分正常' in document.decode(),'independent documented retention/recovery units retained')
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==16 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'five entire new Source/16Code, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};require(local==p['fullSourceUnits'][name]['totals'] and p['fullSourceUnits'][name]['four100'] is True and all(v['missed']==0 and v['covered']>0 for v in local.values()),'entire Source independent nonempty four100')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=232),METHOD=dict(missed=0,covered=50),CLASS=dict(missed=0,covered=16),BRANCH=dict(missed=0,covered=83)) and p['missedLines']==[],'actual sixteen-class four counters, not union')
    require(len(p['owners'])==13,'only five Main/eight whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()) and expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-09' and expected['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','current approved-rule candidate ownership never baseline/accepted')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==55 and v['suites']==8 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('tests',45),('suites',6),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false monitoring55 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=55,suites=8,newUniqueMethods=55,sourcePrograms=5,physicalClasses=16,four100SourcePrograms=5,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentCatalogRows=26,authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),fixtureSha256=p['fixtureHashes'][fixture],candidateOwnerRows=13,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
