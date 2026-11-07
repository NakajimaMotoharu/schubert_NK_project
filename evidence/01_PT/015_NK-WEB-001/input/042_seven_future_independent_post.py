"""Independent evidence-only qualification; no Test/Main invocation, no old exec union."""
from pathlib import Path
import collections,datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22542-seven-security-port-future58-unit-v2';META=RUNS/'pg22544-seven-security-port-passive-metadata-v1';OUT=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22546-seven-future-independent-v1';SOURCE='e876330336ff85c3c45b510445d3327e34da8149';CORE='7aed8eace7c844c2f79f2e39db766faf914890d5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def need(ok,label):
 if not ok:raise ValueError(label)
def counters(t):return {x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in t.findall('counter')}
def initnames(p):return {re.sub(r'\$\$Lambda\+0x[0-9a-f]+','$$Lambda',s) for s in re.findall(r"Initializing '([^']+)",Path(p).read_text()) if s.startswith('dev/codex/schubert/nk/') and 'Test' not in s and 'Fixture' not in s}
def projection(d):return {k:v for k,v in d.items() if not k.endswith('/041_seven_security_port_future_qualifier.py')}
def checkdeps(actual,expected):need(actual==expected,'exact SDK dependency union');need(all(sha(p)==h for p,h in actual.items()),'SDK byte hashes')
def java_tokens(s):
 return re.findall(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/|[A-Za-z_$][A-Za-z0-9_$]*|\d+(?:\.\d+)?|>>>=|>>=|<<=|>>>|>>|<<|==|!=|<=|>=|&&|\|\||\+\+|--|->|::|\S',s)
def main():
 need(not OUT.exists(),'one post only');cfg=load(R/'evidence/01_PT/015_NK-WEB-001/input/040_seven_security_port_future_requalification.json');m=load(U/'manifest.json');b=load(U/'begin.json');need(m['begin']==b and (b['source'],b['normalSource'])==(SOURCE,CORE),'source identity');need((m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,58,0,0,0),'actual whole terminal')
 for p,h in b['inputHashes'].items():need(sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+p],cwd=R)).hexdigest(),'frozen input')
 comp=load(RUNS/'pg22526-seven-security-port-future58-compile-v2/manifest.json');need(comp['actualExit']==0 and projection(comp['inputHashes'])==projection(b['inputHashes']),'unchanged compile projection');need(sha(RUNS/'pg22526-seven-security-port-future58-compile-v2/manifest.json')==b['compileManifestSha256'],'compile receipt');need(b['compileInputProjectionDriverOnlyChanged'] is True,'runtime-only driver correction')
 expectedcases=set();oldcov={};oldids={};oldprobes={};allowedinit=set();sdk={};properties={};oldreceipts=[]
 for row in cfg['priorQualifications']:
  pub=R/row['path'];need(sha(pub)==row['sha256'],'original qualification');old=load(pub);need(old['actualExit']==0 and old['tests']==row['tests'],'original whole');expectedcases.update(map(tuple,old['selectedMethods']));oldcov.update(old['coverage']);oldids.update(old['classIds']);ep=pub.parent/'execinfo.stdout';need(sha(ep)==old['files']['execinfo.stdout'],'old raw probe pin');oldprobes.update({n:[h,int(hit),int(total)] for h,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ep.read_text(),re.M) if n in old['classIds']});orig=old['originalManifest'];need(sha(orig['path'])==orig['sha256'],'original manifest');raw=load(orig['path']);oldreceipts.append(row)
  log=pub.parent/'original-class-init.stdout';need(sha(log)==old['files']['original-class-init.stdout'],'old init pin');allowedinit|=initnames(log)
  begin=pub.parent/'begin.json';need(sha(begin)==old['files']['begin.json'],'public dependency source')
  for path,h in load(begin)['dependencies'].items():
   if '/toolchain/' in path:need(path not in sdk or sdk[path]==h,'no conflicting SDK');sdk[path]=h
   else:need('/schubert-nk-web/' in path or '/schubert-nk-protocol/' in path,'only two Main module roles')
  for arg in raw['stages']['unit']['command']:
   if arg.startswith('-D') and not arg.startswith('-Djava.io.tmpdir='):
    k,v=arg[2:].split('=',1);need(k not in properties or properties[k]==v,'no conflicting property');properties[k]=v
 normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');expecteddeps={normal['jars'][v]['path']:normal['jars'][v]['sha256'] for v in ['web','protocol']};expecteddeps.update(sdk);checkdeps(b['dependencies'],expecteddeps);need(len(sdk)==14,'all fourteen SDKs')
 cmd=m['stages']['unit']['command'];actualprops=dict(x[2:].split('=',1) for x in cmd if x.startswith('-D') and not x.startswith('-Djava.io.tmpdir='));need(all(actualprops.get(k)==v for k,v in properties.items()),'all original JVM properties');need(actualprops['spring.security.strategy']=='MODE_THREADLOCAL','thread local prerequisite');need(cmd.count('--select-class')==7 and '--select-method' not in cmd and '--scan-classpath' not in cmd,'seven whole classes only')
 cases=[];env={}
 for p in sorted((U/'xml').glob('TEST-*.xml')):
  t=E.parse(p).getroot();need(not any(t.findall('.//'+x) for x in ['failure','error','skipped']),'XML no failed/skipped');cases.extend((c.get('classname'),c.get('name')) for c in t.findall('testcase'))
  for x in t.findall('./properties/property'):
   if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']:env[x.get('name')]=x.get('value')
 need(len(cases)==len(set(cases))==58 and set(cases)==expectedcases,'all original independent Test IDs');need(collections.Counter(c for c,n in cases)=={ 'dev.codex.schubert.nk.web.security.'+Path(x['path']).stem:x['expectedWholeTests'] for x in cfg['testClasses']},'per-class counts')
 for text in ['58 tests found','58 tests started','58 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:need(text in (U/'unit.stdout').read_text(),'JUnit actual summary')
 for label,s in m['stages'].items():
  need(s['actualExit']==0 and not s['timedOut'],'actual stage zero')
  for stream in ['stdout','stderr']:need(sha(U/(label+'.'+stream))==s[stream+'Sha256'],'actual stream pin')
 need(load(U/'unit-exit.safe.json')==m['stages']['unit'],'original terminal identity');need(m['physical']==cfg['targetPhysical'],'eight target physical SHA')
 for n,h in m['physical'].items():need(sha(U/'component'/(n+'.class'))==h,'extracted current physical')
 t=E.parse(U/'coverage.xml').getroot();family={c.get('name'):counters(c) for c in t.findall('.//class')};need(family==oldcov,'all eight class counters match independent prior oracle');total=counters(t);need(all(v['missed']==0 for v in total.values()),'all counters covered');need({k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=163,METHOD=29,CLASS=8,BRANCH=58),'exact total counters')
 ids=dict((n,h) for h,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text()));need(ids==oldids,'current CRC vs old byte-identical targets');ex=(U/'execinfo.stdout').read_text();need(ex.count('Session "')==1 and 'Session "PG22542-SEVEN-SECURITY-PORT58"' in ex,'one fresh exec session');probes={n:[h,int(hit),int(all_)] for h,hit,all_,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
 for n,h in ids.items():need(probes[n][0]==h and probes[n]==oldprobes[n],'all physical raw probes match pinned prior; filtered Code checked separately')
 actualinit=initnames(U/'class-init.log');need(actualinit==allowedinit and len(actualinit)==33,'same normalized Product init union; seven JVM counts are not added')
 blocked=['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec','dev/codex/schubert/nk/web/bootstrap/WebStartupException'];fullinit=re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text());need(not any(n in fullinit for n in blocked),'held four not initialized');need(not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','dev/codex/schubert/nk/batch/','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','java/net/Socket')) for n in fullinit),'no actual backend/cipher/native module init')
 met=load(META/'manifest.json');need(met['actualExit']==0 and met['productTestsExecuted']==0 and met['execSha256']==sha(U/'jacoco.exec'),'passive metadata same exec');actual={}
 for module in ['web','protocol']:
  for cl in E.parse(META/(module+'-methods.xml')).getroot().findall('.//class'):
   methods=[dict(name=x.get('name'),desc=x.get('desc')) for x in cl.findall('method') if any(c.get('type')=='INSTRUCTION' and int(c.get('covered'))>0 for c in x.findall('counter'))]
   if methods:need(cl.get('name') in allowedinit,'executed Main belongs to old graph');actual[cl.get('name')]=methods
 restricted={'SessionPayloadCodec':{'<init>','validateKey','close','<clinit>'},'JdbcWebSessionStore':{'<init>'},'SpringEncryptedSessionRepository':{'<init>'},'EncryptedWebSessionRepository':{'<init>'},'SessionAttributeCodec':{'<init>','<clinit>'},'EncryptedSessionPayload':{'validateVersion'}}
 for n,methods in actual.items():
  if n.rsplit('/',1)[-1] in restricted:need({x['name'] for x in methods}<=restricted[n.rsplit('/',1)[-1]],'supplied-session constructor-only graph; no actual crypto/store')
 original=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22512-seven-port-future-original-v1';op=load(original/'manifest.json');need(sha(R/cfg['support']['path'])==cfg['support']['sha256'],'support byte unchanged')
 for row in cfg['testClasses']:
  p=original/Path(row['path']).name;need(sha(p)==row['originalSha256'],'preserved original Test');s=p.read_text()
  for patch in row['patches']:need(s.count(patch['before'])>=1,'original patch site');s=s.replace(patch['before'],patch['after'])
  need(java_tokens(s)==java_tokens((R/row['path']).read_text()),'only eight finite wait argument additions')
 stat=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22518-seven-security-port-static-applicability-v1/manifest.json';st=load(stat);need(st['pmdRaw']==39 and all(st[k]==0 for k in ['applicableViolations','checkstyle','spotbugs','processingErrors']),'static exact scope zero applicable');need(all(x['classification']=='NOT_APPLICABLE' and x['reason'] for x in st['individualClassifications']),'all39 individual reasons');need(projection(st['inputHashes'])==projection(b['inputHashes']),'same static Test inputs')
 negative=0
 for changed in [dict(list(expecteddeps.items())[1:]),dict(expecteddeps,**{next(iter(expecteddeps)):'0'*64})]:
  try:checkdeps(changed,expecteddeps)
  except ValueError:negative+=1
 need(negative==2,'dependency drop/hash negative guards');need(java_tokens('assertEquals( x, y);')==java_tokens('assertEquals(\n x,\n y);'),'format-only delimiter change');need(java_tokens('foo bar')!=java_tokens('foobar') and java_tokens('\"a b\"')!=java_tokens('\"ab\"'),'identifier and literal content preserved')
 OUT.mkdir();files={}
 for base,prefix in [(U,'original-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file() and p.name!='jacoco.exec':
    name=prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);need(name not in files,'unique evidence names');shutil.copyfile(p,OUT/name);files[name]=sha(OUT/name)
 shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec');files['jacoco.exec']=sha(OUT/'jacoco.exec');write(OUT/'executed-main-methods.json',actual);files['executed-main-methods.json']=sha(OUT/'executed-main-methods.json')
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,productionCoreMain=CORE,tests=58,newUniqueTests=0,requalifiedExistingTests=58,newSourceProofs=0,retainedWholeSources=7,coverage=total,physicalClassCount=8,physical=m['physical'],classIds=ids,probes={n:probes[n] for n in ids},manualExclusions=[],oldExecCombined=False,productInitUniqueClasses=33,productInitializationCountEqualityNotClaimed=True,executedMainClasses=len(actual),heldFourInitializations=0,allOtherTestTokensAndAssertionsUnchanged=True,finiteWaitAdditions=8,staticClassification=dict(path=str(stat.relative_to(R)),sha256=sha(stat)),originalRun=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),priorQualifications=oldreceipts,inputHashes=b['inputHashes'],environment=env,dependencies=b['dependencies'],requiredProperties=properties,toolNegativeGuards=negative,files=files,bugs=['BUG-2434','BUG-2435','BUG-2436'],yktFutureAuditStillOpen='YKT-2177',newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));write(OUT/'manifest.json',result);print(json.dumps(dict(actualExit=0,tests=58,requalified=58,newUnique=0,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
