"""Exact fresh selected suites + sanitized SSC179 operator flags; not full/formal coverage."""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import xml.etree.ElementTree as E

ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG457-caddy-timeout-v1'
assert not OUT.exists()
OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'PageViewModelTest':8},'batch':{'MorningCaddyReadinessTest':6,'BackupUnitStartClientTest':16,'MorningStartupLaunchOwnerTest':3,'RootFailedStartPairRecoveryTest':11,'StartupPermitFilesTest':15}}
frozen=WORK/'pg457-caddy-selected-v6-frozen'
modules={};files={}
for module,suites in selected.items():
    target=frozen/('schubert-nk-'+module)/'target'
    static=E.parse(target/'spotbugsXml.xml').getroot()
    assert not static.findall('BugInstance') and int(static.find('Errors').get('errors'))==0
    for name,count in suites.items():
        reports=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'))
        assert len(reports)==1
        original=E.parse(reports[0]).getroot()
        assert int(original.get('tests'))==count and len(original.findall('testcase'))==count
        assert all(int(original.get(k))==0 for k in ('failures','errors','skipped'))
        safe=E.Element('testsuite',{k:original.get(k) for k in ('name','tests','failures','errors','skipped','time')})
        for case in original.findall('testcase'):
            assert all(child.tag in ('system-out','system-err') for child in case)
            E.SubElement(safe,'testcase',{k:case.get(k) for k in ('name','classname','time')})
        p=OUT/'junit'/module/reports[0].name;p.parent.mkdir(parents=True,exist_ok=True)
        E.indent(safe);E.ElementTree(safe).write(p,encoding='utf-8',xml_declaration=True)
        files[str(p.relative_to(OUT))]=sha(p)
    modules[module]={'tests':sum(suites.values()),'suites':len(suites),'failures':0,'errors':0,'skipped':0,'staticViolations':0}
    # All actual target bytes are privately frozen; no stale XML is selected into this run.
    files_to_hash=sorted(p for p in target.rglob('*') if p.is_file())
    modules[module]['privateTargetInventorySha256']=hashlib.sha256(json.dumps({str(p.relative_to(target)):sha(p) for p in files_to_hash},sort_keys=True,separators=(',',':')).encode()).hexdigest()
log=WORK/'pg457-caddy-selected-v6.log'
assert '[INFO] BUILD SUCCESS' in log.read_text() and '[INFO] BUILD FAILURE' not in log.read_text()
assert sum(m['tests'] for m in modules.values())==86
assert sum(m['suites'] for m in modules.values())==10
native_jobs=[('pg457-isolation-native-v1.log',0),('pg457-timeout-verify-v1.log',1),('pg457-timeout-verify-v2.log',1),('pg457-timeout-verify-v3.log',1),('pg457-timeout-verify-v4.log',1),('pg457-timeout-verify-v5.log',0),('pg457-timeout-verify-v6.log',0)]
if (WORK/'pg457-timeout-recover-v1.log').exists():
    native_jobs.append(('pg457-timeout-recover-v1.log',0))
raws=[]
for name,code in native_jobs:
    p=WORK/name
    lines=[line for line in p.read_text().splitlines() if re.fullmatch(r'PG(?:456|457)[A-Za-z0-9_.$:= /-]+',line)]
    assert lines
    if 'recover-v1' in name:assert any(s.startswith('PG457_TIMEOUT_PAIR_RECOVERED ') for s in lines)
    safe=OUT/'logs'/name;safe.parent.mkdir(parents=True,exist_ok=True);safe.write_text('\n'.join(lines)+'\n')
    files[str(safe.relative_to(OUT))]=sha(safe)
    raws.append({'name':name,'exitCode':code,'rawPrivateSha256':sha(p),'safePath':str(safe.relative_to(OUT)),
                 'qualified':name not in ('pg457-timeout-verify-v5.log',) and code==0})
sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.glob('tools/quality/vm/050_s1/*457*')) if p.is_file()}
for p in sorted((ROOT/'src/schubert-nk-batch').rglob('*.java')):
    if p.name in {'BackupUnitStartClient.java','MorningCaddyReadiness.java','RootFailedStartRecovery.java','BackupUnitStartClientTest.java','MorningCaddyReadinessTest.java','RootFailedStartPairRecoveryTest.java'}:sources[str(p.relative_to(ROOT))]=sha(p)
manifest={'id':'PG457-caddy-timeout-v1','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formal':False,
 'hostSourceHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'hostSourceDirty':True,'hostSourceFiles':sources,
 'nativeProductionSource':'559bf7eacb401d6d07037dbdd295b32f174976a0','nativeRelease':'0.1.0-PG456',
 'nativeManifestSha256':'21affa1850d60f3a7d54f5dbcc37e12c6460563865771fa49a52a433fe91b424','privateCaptureSetSha256':'c9a01ff80c118373f474e0d1993f72601808d4cc4bbbc8227b62714ca7edf215',
 'command':'six-reactor spotless:check test-compile jar:test-jar test exact10classes spotbugs:check jacoco:report; pg457-caddy-selected-v6.log','hostExitCode':0,'hostLogSha256':sha(log),
 'modules':modules,'tests':86,'suites':10,'failures':0,'errors':0,'skipped':0,'nullAwayCompile':'PASS',
 'java':'25.0.4','maven':'3.9.12','spotbugs':'4.10.4','jacoco':'0.8.15','nativeJobs':raws,
 'toolOnlyAssertions':{'isolation':12,'timeoutLatest':197,'productionPtCount':0},'toolCompileLatestLogSha256':sha(WORK/'pg457-timeout-compile-v7.log'),
 'toolIndependentLatestLogSha256':sha(WORK/'pg457-timeout-independent-v7.log'),'toolClassSha256':sha(WORK/'pg457-timeout-tool-v7/Pg457TimeoutPairRecovery.class'),
 'bugs':['BUG-671','BUG-672','BUG-673','BUG-674','BUG-675','BUG-676','BUG-677'],'ssc':['SSC-179','SSC-178'],'qa':['QA-047'],
 'testIds':['CADDY457001','CADDY457002','CADDY457003','ROOTPAIR179-001','ROOTPAIR179-002','TIMEOUT457-ENV','TIMEOUT457-PHASE','TIMEOUT457-NATIVE'],
 'coverage':{'qualified':False,'reason':'selected run without clean; append exec may contain older source, never accepted for coverage100'},
 'limitations':['Formal run24/1964PT/53scope unchanged','Whole fresh six regression/new signed source/native Caddy/CHR/coverage100 pending','External Web Root was not captured; actual parent launch correlation is distinct','Source capture after selected completion, not invented pre-run all-source proof'],
 'before':[{'run':'selected-v3','tests':60,'exitCode':0,'frozenPrivate':str(WORK/'pg457-caddy-selected-v3-frozen'),'coverageQualified':False},
 {'run':'selected-v4','exitCode':1,'batchTestsNotRun':True,'reason':'new test fixture hook checked IOException compile failure'},
 {'run':'selected-v5','exitCode':1,'tests':86,'failures':1,'reason':'old retirement-only fixture deliberately rejects current replacement; new publication fixture required'}],
 'redaction':'Exact selected XML properties/stdout/stderr removed; fixed operator flags/class frames only; private owner/permit/launch/credentials/session/data/dump not copied','files':files}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':86,'suites':10,'formal':False,'manifestSha256':sha(OUT/'manifest.json')}))
