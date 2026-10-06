"""Independent same-source completed six-module XML/counter/byte evidence, not formal acceptance."""
import hashlib,json,pathlib,re,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='a5f9e6a54427ff356626245230496d8667082465'
assert (WORK/'pg473-six-full-v1.exit').read_text().strip()=='0'
assert (WORK/'pg473-six-full-v1.source').read_text().strip()==SOURCE
subprocess.run(['git','diff','--exit-code',SOURCE,'--','src','pom.xml'],cwd=ROOT,check=True)
subprocess.run(['sha256sum','--check','--status',str(WORK/'pg473-six-full-v1.source-files.sha256')],cwd=ROOT,check=True)
rows=[]
log=(WORK/'pg473-six-full-v1.log').read_text()
assert log.count('BugInstance size is 0')==6 and 'BUILD SUCCESS' in log
for module in ['protocol','storage','bootstrap','api','web','batch']:
    target=ROOT/'src'/('schubert-nk-'+module)/'target'; frozen=WORK/'pg473-host'/module
    for path in target.rglob('*'):
        if path.is_file():assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256((frozen/path.relative_to(target)).read_bytes()).digest()
    reports=list((frozen/'surefire-reports').glob('TEST-*.xml')); suites=[E.parse(p).getroot() for p in reports]
    assert suites and all(int(s.get(k,'0'))==0 for s in suites for k in ['failures','errors','skipped'])
    jacoco=E.parse(frozen/'site/jacoco/jacoco.xml').getroot()
    counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in jacoco.findall('counter')}
    rows.append({'module':module,'suiteCount':len(suites),'tests':sum(int(s.get('tests')) for s in suites),'FES':0,'counters':counters,'coverageXmlSha256':hashlib.sha256((frozen/'site/jacoco/jacoco.xml').read_bytes()).hexdigest(),'projectJarSha256':hashlib.sha256((frozen/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')).read_bytes()).hexdigest()})
assert sum(r['tests'] for r in rows)==3356 and sum(r['suiteCount'] for r in rows)==502
writer=E.parse(WORK/'pg473-host/api/site/jacoco/jacoco.xml').getroot().find("./package[@name='dev/codex/schubert/nk/api/application/scenario']/class[@name='dev/codex/schubert/nk/api/application/scenario/ScenarioAuditWriter']")
assert writer is not None and all(int(c.get('missed'))==0 for c in writer.findall('counter'))
webReport=E.parse(WORK/'pg473-host/web/site/jacoco/jacoco.xml').getroot()
closed={}
for name in ['WebRuntimeHealth','WebRuntimeStop','WebRequestContext','CaddyTransportContextFilter']:
 matches=[c for c in webReport.findall('.//class') if c.get('name').endswith('/'+name)];assert len(matches)==1
 counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in matches[0].findall('counter')}
 assert all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['BRANCH','LINE','METHOD','CLASS'])
 closed[name]=counters
manifest={'closedWebClassCounters':closed,'id':'PG473-web-remaining-full','branch':'dev-foundation','productionSource':SOURCE,'actualExit':0,'started':(WORK/'pg473-six-full-v1.started').read_text().strip(),'completed':(WORK/'pg473-six-full-v1.completed').read_text().strip(),'command':'bash tools/quality/vm/050_s1/pg473_full_v1.sh '+SOURCE,'modules':rows,'tests':3356,'suiteCount':502,'FES':0,'staticModules':6,'staticIssues':0,'formatNullAwayWerrorPassed':True,'sourceBeforeAfterUnchanged':True,'allFrozenBytesMatched':True,'freshWriterAllCountersMissedZero':True,'globalCoverage100':False,'nativeSameSourceAccepted':False,'allChrPassed':False,'formalPass':False,'relatedBugs':['BUG-758','BUG-759'],'relatedYkt':['YKT-538','YKT-539'],'testIds':['PT-OPS-NWEB-PART001..003','PT-OPS-NWEB-HEALTH001..004','PT-OPS-NWEB-STOP001..005','PT-OPS-NWEB-UNKNOWN001','PT-WEB-IDENT-CONSIST001..003'],'environment':{'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','jacoco':'0.8.15'},'logSha256':hashlib.sha256((WORK/'pg473-six-full-v1.log').read_bytes()).hexdigest(),'rawLogsInGit':False}
out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG473-web-remaining-full/manifest.json'
assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':3356,'suites':502,'static6zero':True,'sameSourceBytes':True,'coverage100':False,'formal':False,'manifestSha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
