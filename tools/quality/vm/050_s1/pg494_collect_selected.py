"""SSC203 independent fresh selected XML/hash freeze; dirty source, not formal/native."""
import datetime, hashlib, json, os, pathlib, shutil, xml.etree.ElementTree as E
os.umask(0o077)
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
base=WORK/'pg494-completion-compound-selected-v3'
read=lambda ext:pathlib.Path(str(base)+ext).read_text().strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read('.exit')=='0'
log=read('.log');assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0')==5
assert log.count('No errors/warnings found')==5
started=datetime.datetime.fromisoformat(read('.started')).timestamp()
ended=datetime.datetime.fromisoformat(read('.completed')).timestamp()
freeze=WORK/'pg494-selected-v3-freeze';assert not freeze.exists();freeze.mkdir(mode=0o700)
modules=[]
for name in ['protocol','storage','bootstrap','api','batch']:
 target=ROOT/'src'/('schubert-nk-'+name)/'target';out=freeze/name
 shutil.copytree(target,out)
 for p in [out,*out.rglob('*')]:
  p.chmod(0o700 if p.is_dir() else 0o600)
  if p.is_file():assert sha(p)==sha(target/p.relative_to(out))
 suites=[]
 for p in sorted((out/'surefire-reports').glob('TEST-*.xml')):
  assert started<=p.stat().st_mtime<=ended+1
  doc=E.parse(p).getroot();assert int(doc.get('tests'))>0
  assert all(int(doc.get(k,'0'))==0 for k in ['failures','errors','skipped'])
  assert len(doc.findall('testcase'))==int(doc.get('tests'))
  suites.append({'class':doc.get('name'),'tests':int(doc.get('tests')),'xmlSha256':sha(p)})
 assert suites
 coverage=out/'site/jacoco/jacoco.xml';assert started<=coverage.stat().st_mtime<=ended+1
 doc=E.parse(coverage).getroot()
 counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in doc.findall('counter')}
 modules.append({'module':name,'suites':suites,'tests':sum(s['tests'] for s in suites),'coverage':counters,'coverageXmlSha256':sha(coverage)})
payload={'id':'PG494-completion-compound-selected-v3','branch':'dev-foundation','baseHead':read('.source'),
 'testedDirtyDiffSha256':sha(pathlib.Path(str(base)+'.completed-source-diff.private')),
 'sourceBeforeFormatterDiffSha256':sha(pathlib.Path(str(base)+'.source-diff.private')),
 'sourceFixedCommit':False,'actualExit':0,'started':read('.started'),'completed':read('.completed'),
 'command':'bash tools/quality/vm/050_s1/pg494_completion_selected_v3.sh','modules':modules,
 'tests':sum(m['tests'] for m in modules),'suites':sum(len(m['suites']) for m in modules),
 'staticModules':5,'staticIssues':0,'FES':0,'testIds':['RLOOK493001','COMP203001..004','existing retained-original group'],
 'related':['SSC-203','BUG-799','BUG-800','BUG-801','YKT-570'],'logSha256':sha(pathlib.Path(str(base)+'.log')),
 'environment':{'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15'},
 'coverage100':False,'formal':False,'nativeAccepted':False,'ITSTAccepted':False,'rawLogsInGit':False}
out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG494-completion-compound-selected-v3/manifest.json'
assert not out.exists();out.parent.mkdir(parents=True)
with out.open('x') as f:json.dump(payload,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'tests':payload['tests'],'suites':payload['suites'],'static5zero':True,'formal':False,'manifestSha256':sha(out)}))
