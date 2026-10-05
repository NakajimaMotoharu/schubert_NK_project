"""Independent same-source completed six-module XML/counter/byte evidence, not formal acceptance."""
import hashlib,json,pathlib,re,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='d3bba6db6eb9fec13e4847a10541cf337f575731'
assert (WORK/'pg469-six-full-v1.exit').read_text().strip()=='0'
assert (WORK/'pg469-six-full-v1.source').read_text().strip()==SOURCE
subprocess.run(['git','diff','--exit-code',SOURCE,'--','src','pom.xml'],cwd=ROOT,check=True)
subprocess.run(['sha256sum','--check','--status',str(WORK/'pg469-six-full-v1.source-files.sha256')],cwd=ROOT,check=True)
rows=[]
log=(WORK/'pg469-six-full-v1.log').read_text()
assert log.count('BugInstance size is 0')==6 and 'BUILD SUCCESS' in log
for module in ['protocol','storage','bootstrap','api','web','batch']:
    target=ROOT/'src'/('schubert-nk-'+module)/'target'; frozen=WORK/'pg469-host'/module
    for path in target.rglob('*'):
        if path.is_file():assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256((frozen/path.relative_to(target)).read_bytes()).digest()
    reports=list((frozen/'surefire-reports').glob('TEST-*.xml')); suites=[E.parse(p).getroot() for p in reports]
    assert suites and all(int(s.get(k,'0'))==0 for s in suites for k in ['failures','errors','skipped'])
    jacoco=E.parse(frozen/'site/jacoco/jacoco.xml').getroot()
    counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in jacoco.findall('counter')}
    rows.append({'module':module,'suiteCount':len(suites),'tests':sum(int(s.get('tests')) for s in suites),'FES':0,'counters':counters,'coverageXmlSha256':hashlib.sha256((frozen/'site/jacoco/jacoco.xml').read_bytes()).hexdigest(),'projectJarSha256':hashlib.sha256((frozen/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')).read_bytes()).hexdigest()})
assert sum(r['tests'] for r in rows)==3301 and sum(r['suiteCount'] for r in rows)==489
writer=E.parse(WORK/'pg469-host/api/site/jacoco/jacoco.xml').getroot().find("./package[@name='dev/codex/schubert/nk/api/application/scenario']/class[@name='dev/codex/schubert/nk/api/application/scenario/ScenarioAuditWriter']")
assert writer is not None and all(int(c.get('missed'))==0 for c in writer.findall('counter'))
manifest={'id':'PG469-scenario-audit-full','branch':'dev-foundation','productionSource':SOURCE,'actualExit':0,'started':(WORK/'pg469-six-full-v1.started').read_text().strip(),'completed':(WORK/'pg469-six-full-v1.completed').read_text().strip(),'command':'bash tools/quality/vm/050_s1/pg469_full_v1.sh '+SOURCE,'modules':rows,'tests':3301,'suiteCount':489,'FES':0,'staticModules':6,'staticIssues':0,'formatNullAwayWerrorPassed':True,'sourceBeforeAfterUnchanged':True,'allFrozenBytesMatched':True,'freshWriterAllCountersMissedZero':True,'globalCoverage100':False,'nativeSameSourceAccepted':False,'allChrPassed':False,'formalPass':False,'relatedBugs':['BUG-742','BUG-743'],'relatedYkt':['YKT-523','YKT-524'],'testIds':['PT-SCN-AUD469001..008'],'environment':{'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','jacoco':'0.8.15'},'logSha256':hashlib.sha256((WORK/'pg469-six-full-v1.log').read_bytes()).hexdigest(),'rawLogsInGit':False}
out=ROOT/'evidence/01_PT/008_NK-SCN-001/evidence/provisional/PG469-scenario-audit-full/manifest.json'
assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':3301,'suites':489,'static6zero':True,'sameSourceBytes':True,'coverage100':False,'formal':False,'manifestSha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
