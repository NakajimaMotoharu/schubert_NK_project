"""Independent source/XML/normal-artifact/CRC qualification; no product execution."""
import json,hashlib,re,copy,zipfile,subprocess,xml.etree.ElementTree as E,datetime,shutil
from pathlib import Path
ROOT=Path('/home/mini/codex/project1/work/pgpt-foundation');RUNS=ROOT.parent/'pgpt-runs/PG379';SLOT=RUNS/'pg18644-jms-uuid-normal-unit-v1';SOURCE='b09393b0e746b55fd480176d57996d65bd76a95d';OUT=ROOT/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18644-jms-uuid-normal-post-v1';assert not OUT.exists();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rawp=SLOT/'manifest.safe.json';assert sha(rawp)=='113c482177059b17343334ffa7ecccff2e964b5d7e91558a5048dc47e1341976';raw=json.loads(rawp.read_text());normalp=RUNS/'pg18642-jms-uuid-six-main-compile-v1/manifest.safe.json';assert sha(normalp)=='6dec0021543c6c13c100237055b1f8bfe38fbdeeca5ac462b6a4ab2e1d45e010';normal=json.loads(normalp.read_text());assert raw['source']==normal['source']==SOURCE and raw['actualExit']==normal['actualExit']==0
for p,h in raw['files'].items():assert sha(SLOT/p)==h,(p,'raw output modified')
assert all(s['actualExit']==0 and not s['timedOut'] for s in raw['stages'].values());assert raw['tests']==14 and raw['failures']==raw['errors']==raw['skipped']==0
pins={**raw['begin']['mainHashes'],**raw['begin']['testHashes']};expected=set()
for p,h in pins.items():
 b=(ROOT/p).read_bytes();assert hashlib.sha256(b).hexdigest()==h;assert b==subprocess.check_output(['git','show',SOURCE+':'+p],cwd=ROOT)
 if '/test/' in p:
  text=b.decode();pkg=re.search(r'(?m)^package ([\w.]+);',text).group(1);cl=Path(p).stem;names=re.findall(r'@Test\s+void (\w+)\(',text);assert len(names)==7;expected.update((pkg+'.'+cl,n) for n in names)
for p,h in raw['begin']['dependencies'].items():assert sha(p)==h
physical={};jarPins={}
for mod,name in [('api','dev/codex/schubert/nk/api/messaging/guard/JmsMessageGuard'),('web','dev/codex/schubert/nk/web/messaging/JmsReplyDecoder')]:
 jar=normal['jars'][mod];assert sha(jar['path'])==jar['sha256'];assert raw['begin']['dependencies'][jar['path']]==jar['sha256'];jarPins[mod]=jar
 with zipfile.ZipFile(jar['path']) as z:
  members={n for n in z.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')};assert members=={name+'.class'}
  assert (SLOT/'component'/(name+'.class')).read_bytes()==z.read(name+'.class')
 assert not (SLOT/'classes'/(name+'.class')).exists(),'test classes must not shadow normal Main'
 physical[name]={'normalClassSha256':sha(SLOT/'component'/(name+'.class'))}
report=E.parse(SLOT/'coverage.xml').getroot();assert {c.get('name') for c in report.findall('.//class')}==set(physical)
execText=(SLOT/'execinfo.stdout').read_text();sessions=re.findall(r'^Session "([^"]+)"',execText,re.M);assert sessions==['PG18644-JMS-CANONICAL-NORMAL'];assert len(report.findall('sessioninfo'))==1
classText=(SLOT/'classinfo.stdout').read_text()
for c in report.findall('.//class'):
 name=c.get('name');counters={n.get('type'):{'missed':int(n.get('missed')),'covered':int(n.get('covered'))} for n in c.findall('counter')};assert all(v['missed']==0 for v in counters.values());assert all(counters[k]['covered']>0 for k in ('LINE','METHOD','CLASS','BRANCH'))
 crc=re.search(r'class 0x([0-9a-f]{16}) '+re.escape(name)+r'$',classText,re.M).group(1);row=re.search(r'^'+crc+r'\s+(\d+) of\s+(\d+)\s+'+re.escape(name)+r'$',execText,re.M);assert row and int(row.group(1))==int(row.group(2)) and int(row.group(1))>0
 physical[name].update(crc64=crc,counters=counters,probeHits=int(row.group(1)),probes=int(row.group(2)),four100=True)
cases=[];xmlpins={};env=[]
for p in sorted((SLOT/'xml').glob('TEST-*.xml')):
 x=E.parse(p).getroot();xmlpins[p.name]=sha(p)
 assert all(int(x.get(k,'0'))==0 for k in ('failures','errors','skipped'))
 for c in x.findall('.//testcase'):
  assert not c.findall('failure')+c.findall('error')+c.findall('skipped');cases.append((c.get('classname'),c.get('name')))
 env.append({n.get('name'):n.get('value') for n in x.findall('properties/property') if n.get('name') in ('java.version','java.runtime.version','os.name','os.arch','os.version')})
assert len(cases)==len(set(cases))==14 and set(cases)==expected
init=[]
for name in re.findall(r"Initializing '([^']+)'",(SLOT/'class-init.log').read_text()):
 if name.startswith('dev/codex/schubert/nk/') and 'Test' not in name and '$$Lambda' not in name:
  assert name.startswith('dev/codex/schubert/nk/protocol/') or any(name.startswith(p) for p in ['dev/codex/schubert/nk/api/messaging/guard/JmsMessageGuard','dev/codex/schubert/nk/api/messaging/guard/GuardedJmsMessage','dev/codex/schubert/nk/web/messaging/JmsReplyDecoder','dev/codex/schubert/nk/web/messaging/ValidatedReply']);init.append(name)
def qualify(m):
 if m['source']!=SOURCE or type(m['actualExit']) is not int or m['actualExit']!=0 or m['tests']!=14 or any(m[k]!=0 for k in ('failures','errors','skipped')) or len(m['cases'])!=len({(x['classname'],x['name']) for x in m['cases']}):raise ValueError('not qualified')
qualify(raw);neg=[]
for key,val in [('source','6b53efeec87f3ec36a840dd8e7759656cb4aee5c'),('actualExit',1),('actualExit',True),('tests',13),('failures',1),('errors',1),('skipped',1)]:
 m=copy.deepcopy(raw);m[key]=val
 try:qualify(m)
 except ValueError:neg.append(key+':'+str(val))
 else:raise AssertionError('invalid metadata accepted')
m=copy.deepcopy(raw);m['cases'][1]=copy.deepcopy(m['cases'][0])
try:qualify(m)
except ValueError:neg.append('duplicate_case')
else:raise AssertionError('duplicate accepted')
assert len(neg)==8
OUT.mkdir()
for n in ('coverage.xml','coverage.csv','post.py','manifest.safe.json','execinfo.stdout','classinfo.stdout'):shutil.copyfile(SLOT/n,OUT/n)
for p in sorted((SLOT/'xml').glob('TEST-*.xml')):
 x=E.parse(p).getroot()
 for n in x.findall('properties')+x.findall('system-out')+x.findall('system-err'):x.remove(n)
 E.ElementTree(x).write(OUT/p.name,encoding='utf-8',xml_declaration=True)
manifest={'actualExit':0,'source':SOURCE,'rawManifestSha256':sha(rawp),'normalCompileManifestSha256':sha(normalp),'scope':'TWO_CHANGED_MAIN_NORMAL_ARTIFACT_FULL_SOURCE_UNITS_NOT_451','sourcePins':pins,'jarPins':jarPins,'tests':14,'newUniqueTestMethods':2,'preexistingMethodsRerunForChangedSource':12,'newMethodLiteralVectors':22,'sourceUnits':physical,'sessionIdentity':sessions[0],'execSha256':sha(SLOT/'jacoco.exec'),'originalXmlPins':xmlpins,'cases':[{'classname':a,'name':b,'result':'PASS'} for a,b in cases],'failures':0,'errors':0,'skipped':0,'metadataNegativeVectors':neg,'classInitMain':init,'reportedEnvironment':env,'actualBackendActions':0,'actualRootInvocation':False,'whole451Accepted':False,'wholeF03Accepted':False,'formalUpdated':False,'newAccepted':0,'oldSourceExecTransferred':False,'priorLocalCompilePG18638CountedAgain':False,'files':{p.name:sha(p) for p in OUT.iterdir() if p.name!='manifest.json'}};(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':sha(OUT/'manifest.json'),'tests':14,'newUniqueMethods':2,'sourceUnits':physical,'negativeMetadata':len(neg)}))
