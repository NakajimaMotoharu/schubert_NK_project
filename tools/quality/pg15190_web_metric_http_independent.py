"""Independent Web memory HTTP23/oneSource, corrected LF literal and passive no-held-probe observation."""
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

PIN='c7c26541b7f7d0c482409b703988b7807fee791065acdfcffcf84a179ca778b7'
POST=data.BASE/'PG15188-web-metric-http-twenty-three-post-v1'
OUT=data.BASE/'PG15190-web-metric-http-independent-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
COUNTS={"WebMetricHttpHandlerTest":23}
EXPECTED={"WebMetricHttpHandler":[]}
NATURAL=set()
DOC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only monitoring independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG15186-web-metric-http-twenty-three-pt-v1/manifest.json','68d0e6111fc202618b68899923d15f59dfda0495241325294bee25836964a808')
    registry=data.read_checked(data.BASE/'PG15176-current1654-api-metric-http-registry-v1/manifest.json','92725240633fef82ffec2249137ed57b8c89419505ee502a32ca4a5dbb8aa716')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15186-ORIGINAL-WEB-METRIC-HTTP23','genuine same source/own single exec')
    actual=[];suite_names=set()
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original whole XML bytes');root=ET.fromstring(value);simple=root.get('name').rsplit('.',1)[-1];suite_names.add(simple)
        require(int(root.get('tests'))==COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole16 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(suite_names==COUNTS.keys() and len(actual)==len(set(actual))==23 and set(actual)=={(c['classname'],c['name']) for c in raw['cases']} and not set(actual)&{(c['classname'],c['name']) for c in registry['cases']},'all16/one suite unique new, never prior1367 replay')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    declared=set()
    for simple,count in COUNTS.items():
        path='src/schubert-nk-web/src/test/java/'+PREFIX+simple+'.java';text=(data.ROOT/path).read_text();require(data.sha((data.ROOT/path).read_bytes())==hashes[path],'whole original normal Test source pin')
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==count,'all original declared methods');declared.update(('dev.codex.schubert.nk.web.monitoring.'+simple,n) for n in methods)
    require(declared==set(actual),'every declared Test ID corresponds to one original actual XML')
    expected_http=dict(path='/actuator/prometheus',success=200,notFound=404,methodNotAllowed=405,cacheControl='no-store',metricType='text/plain; version=0.0.4; charset=utf-8',jsonType='application/json; charset=utf-8',readyPrefix='# TYPE schubert_nk_web_ready gauge'+chr(10)+'schubert_nk_web_ready ')
    literal=re.search(r'private static final String READY = (".*");',text)
    require(literal is not None and json.loads(literal.group(1))==expected_http['readyPrefix'] and all(value in text for value in [expected_http['path'],expected_http['cacheControl'],expected_http['metricType'],expected_http['jsonType']]),'independent Web HTTP literals and exactly one real LF byte, never Production expected generator')
    def http_contract(v):require(type(v['readyPrefix']) is str and v['readyPrefix']=='# TYPE schubert_nk_web_ready gauge'+chr(10)+'schubert_nk_web_ready ','exact Web prefix bytes')
    http_contract(expected_http);http_negative=[]
    for label,value in [('escaped-LF',expected_http['readyPrefix'].replace(chr(10),chr(92)+'n')),('missing-LF',expected_http['readyPrefix'].replace(chr(10),'')),('double-LF',expected_http['readyPrefix'].replace(chr(10),chr(10)*2))]:
        candidate=dict(expected_http);candidate['readyPrefix']=value
        try:http_contract(candidate)
        except ValueError:http_negative.append(label)
        else:raise ValueError('false prefix accepted '+label)
    fixture_tests=['WebDbPoolMetricObservationTest','WebServiceMetricBindingTest']
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
    metric_rows={"nk_db_pool_connections":["gauge","service,state"],"nk_http_requests_total":["counter","service,route,method,status_class"],"nk_http_request_duration_seconds":["histogram","service,route"]}
    observed_metrics={}
    metric_section=document.decode().split('## 6. Metric catalog',1)[1].split('## 7. Alert condition',1)[0]
    for line in metric_section.splitlines():
        if not line.startswith('| '):continue
        fields=[value.strip() for value in line.split('|')[1:-1]]
        for name in re.findall(r'`([^`]+)`',fields[0]):
            if name in metric_rows:
                require(name not in observed_metrics,'no repeated approved metric row');observed_metrics[name]=fields[1:3]
    require(observed_metrics==metric_rows and len(observed_metrics)==3,'independent approved API pool/outbox families name/type/label rows from SS351')
    require('JVM/GC/thread、Hikari、process/host/disk、PostgreSQL、Artemisは製品exporter/Micrometer標準metricを使う。' in document.decode(),'approved standard SDK selection, not an invented runtime authority')
    closures={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+child for child in nested]]) for n,nested in EXPECTED.items()};names=set().union(*(set(v) for v in closures.values()))
    require(p['completeSourceUnitClosure']==closures and set(p['physicalClasses'])==set(p['executable'])==names and len(names)==1 and p['metadataClasses']==[] and not closures.keys()&registry['fullSourceUnits'].keys(),'one entire new Source/oneCode, no helper parent promotion')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Jar classfiles')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};unit=p['fullSourceUnits'][name];natural=name in NATURAL
            require(local==unit['totals'] and unit['four100'] is (not natural) and unit['branchNaturallyZero'] is natural and unit['threeCounter100'] is True and all(local[k]['missed']==0 and local[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and (local['BRANCH']==dict(missed=0,covered=0) if natural else local['BRANCH']['missed']==0 and local['BRANCH']['covered']>0),'entire Source: one nonempty four100 Source')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for n in closure:
                value=jar.read(n+'.class');parsed=code.decode(value,n+'.class');require(data.sha(value)==p['physicalClasses'][n] and parsed['methods']==p['sourcePhysicalInventory'][n]['methods'] and any(m['hasCode'] for m in parsed['methods']),'independent actual executable Code, no hidden exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=25),METHOD=dict(missed=0,covered=3),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=4)) and p['missedLines']==[],'actual one-class counters, not union')
    require(len(p['owners'])==2,'only one Main/one whole Test owner rows')
    for path,owned in p['owners'].items():
        expected=canonical(path,logical);require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in expected.items()) and expected['canonicalOwner']==expected['canonicalCostOwner']=='WBS-P018-09' and expected['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','current approved-rule candidate ownership never baseline/accepted')
    passive=p['passiveHeldFailurePrefixObservation'];passive_slot=data.ROOT.parent/'pgpt-runs/PG379/pg15188-web-metric-http-twenty-three-post-v1'
    reader=data.ROOT/'tools/quality/architecture/OwnedWebFailureProbeAbsence.java'
    require(data.sha(reader.read_bytes())==passive['readerSourceSha256']=='92120fdba09ec261e14c78a529c848bee2c3cb53ce4bc83fe6a2d00cc6f250ca','exact reviewed passive reader, no Product imports/load/init/invoke')
    require({v.name for v in (passive_slot/'passive-classes').iterdir()}=={'OwnedWebFailureProbeAbsence.class'} and data.sha((passive_slot/'passive-classes/OwnedWebFailureProbeAbsence.class').read_bytes())==passive['readerClassSha256'],'fresh reader class only, no Product class shadow')
    for label,stage in zip(['passive-reader-compile','passive-reader'],passive['stages'],strict=True):
        require(stage['actualExit']==0 and stage['timedOut'] is False and data.sha((passive_slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((passive_slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'actual passive tool terminal0/stdout/stderr hashes')
    fields=(passive_slot/'passive-reader.stdout').read_text().splitlines()[-1].split(chr(9))
    require(fields==['OWNED_WEB_FAILURE_PREFIX_NO_TRUE_PROBES',str(passive['recordedPrefixClasses']),'0'] and passive['stages'][1]['command'][-3:]==['OwnedWebFailureProbeAbsence',str(data.ROOT.parent/'pgpt-runs/PG379/pg15186-web-metric-http-twenty-three-pt-v1/jacoco.exec'),p['sessionIdentity']],'existing original exec/session only, no Product rerun')
    for label,stage in zip(['wrong-session','missing-arguments'],passive['negativeStages'],strict=True):
        stem='passive-reader-'+label;require(stage['actualExit']==1 and stage['timedOut'] is False and data.sha((passive_slot/(stem+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((passive_slot/(stem+'.stderr')).read_bytes())==stage['stderrSha256'],'two actual tool-negative checks, not failed Product PT')
    require(len(passive['stages'])==len(passive['negativeStages'])==passive['toolNegativeChecks']==2,'all passive tool checks accounted')
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        prefix='dev/codex/schubert/nk/web/bootstrap/WebStartupException'
        expected={name:data.sha(jar.read(name)) for name in jar.namelist() if name==prefix+'.class' or name.startswith(prefix+'$') and name.endswith('.class')}
        require(passive['normalJarPhysicalHashes']==expected and prefix+'.class' in expected,'actual held-prefix class remains normal Jar, never excluded to invent absence')
    def passive_contract(v):
        require(type(v['trueProbes']) is int and v['trueProbes']==0 and type(v['recordedPrefixClasses']) is int and v['recordedPrefixClasses']>=0 and v['execSha256']==p['execSha256'] and v['sessionIdentity']==p['sessionIdentity'] and v['productTestsExecuted']==v['graphCasesExecuted']==0 and v['heldScopesReleased'] is False,'passive original probe observation never dynamic Graph acceptance')
    passive_contract(passive);passive_negative=[]
    for label,key,value in [('true-probe','trueProbes',1),('wrong-exec','execSha256','OLD'),('HOLD-release','heldScopesReleased',True)]:
        candidate=copy.deepcopy(passive);candidate[key]=value
        try:passive_contract(candidate)
        except ValueError:passive_negative.append(label)
        else:raise ValueError('false passive provenance accepted '+label)
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','fixtureHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'all actual original proof/owner/fixture immutable')
        require(v['tests']==23 and v['suites']==1 and v['targetUnitFour100'] is True and v['strictFour100GateExit']==0 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'complete source strict four100 actual')
        require(v['ownChildJvmStandardSdkObserved'] is True and v['forcedGcOrHeapDump'] is False and v['externalVmOrTargetProcessObserved'] is False,'genuine own child SDK measurement never remote/native or forced GC')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['coverageExecUnion'] is False and v['effortPercent'] is None and v['canonicalOwnersRemainCandidateNotAccepted'] is v['helperSourceProgramsNotAcceptedByTheseTargetCounters'] is True,'no helper/old/owner/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('ownChildJvmStandardSdkObserved',False),('forcedGcOrHeapDump',True),('externalVmOrTargetProcessObserved',True),('source','OLD'),('tests',55),('suites',2),('targetUnitFour100',False),('strictFour100GateExit',1),('singleSession',False),('crcMismatch',1),('metadataClasses',list(names)),('manualCounterExclusions',['AlertLifecycle']),('totals',{}),('fullSourceUnits',{}),('fixtureHashes',{'unknown':'0'*64}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('coverageExecUnion',True),('effortPercent',100),('canonicalOwnersRemainCandidateNotAccepted',False),('helperSourceProgramsNotAcceptedByTheseTargetCounters',False)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false Web-pool-context56 proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=23,suites=1,newUniqueMethods=23,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,naturallyBranchZeroPhysicalClasses=0,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,independentThresholdRows=12,independentMetricRows=3,independentMetricTableSha256=data.sha(json.dumps(metric_rows,sort_keys=True).encode()),authoritativeDesign=dict(path=DOC,gitRef='origin/main',commit=doc_head,sha256=data.sha(document)),independentThresholdTableSha256=data.sha(json.dumps(expected_rows,ensure_ascii=False).encode()),candidateOwnerRows=2,independentHttpContract=expected_http,httpOracleNegativeVectors=len(http_negative),passiveMetadataNegativeVectors=len(passive_negative),passiveHeldFailurePrefixObservation=passive,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=True,observationScope="OWN_CHILD_JVM_ONLY",forcedGcOrHeapDump=False,externalVmOrTargetProcessObserved=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
