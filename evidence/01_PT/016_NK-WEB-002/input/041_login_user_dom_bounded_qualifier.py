"""Original four complete display fixtures only. SDK mock GET, no product Java classes."""
from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,sys,zipfile,xml.etree.ElementTree as E
import pg9666_pagination_static as capture
R=Path.cwd();W=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain';J=TC/'jdk-25.0.4/bin'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
CFG=R/'evidence/01_PT/016_NK-WEB-002/input/042_login_user_dom_bounded_scope.json';cfg=load(CFG);phase=sys.argv[1];assert phase in ['prepare','static','preflight','run']
normal=W/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==cfg['normalManifestSha256'];nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5';jar=Path(nm['jars']['web']['path']);assert sha(jar)==nm['jars']['web']['sha256']
tests=cfg['testClasses'];assert len(tests)==4 and sum(len(re.findall(r'@Test\s+void\s+(\w+)\(', (R/p).read_text())) for p in tests)==28
console=TC/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892';deps=cfg['dependencies'];assert len(deps)==15 and all(sha(p)==h for p,h in deps.items())
resourcePaths=['src/schubert-nk-web/src/main/resources/'+p for p in cfg['resources']];inputs={p:sha(R/p) for p in [*tests,*resourcePaths,str(CFG.relative_to(R)),str(Path(__file__).relative_to(R))]};cp=':'.join([*deps,str(console)]);pre=W/cfg['compileSlot'];sta=W/cfg['staticSlot'];unit=W/cfg['unitSlot']
if phase=='prepare':
 fmt=W/cfg['formatSlot'];assert not fmt.exists() and not pre.exists();fmt.mkdir();capture.SLOT=fmt;fm=load(R/'evidence/01_PT/018_NK-OPS-001/evidence/PG21744-explicit-ordinary-test-format-audit-v1/manifest.json');cmd=fm['stage']['command'];prefix=cmd[:cmd.index('com.google.googlejavaformat.java.Main')+1];stage=capture.step('format',prefix+['--skip-reflowing-long-strings','--replace',*tests],R);write(fmt/'manifest.json',dict(actualExit=stage['actualExit'],stage=stage,productTestsExecuted=0));assert stage['actualExit']==0
 inputs.update({p:sha(R/p) for p in tests});pre.mkdir();(pre/'classes').mkdir();(pre/'resources').mkdir()
 with zipfile.ZipFile(jar) as z:
  for p in cfg['resources']:
   data=z.read(p);assert hashlib.sha256(data).hexdigest()==inputs['src/schubert-nk-web/src/main/resources/'+p];dest=pre/'resources'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 capture.SLOT=pre;stage=capture.step('javac',[str(J/'javac'),'-proc:none','-implicit:none','--release','25','-Xlint:all','-Werror','-encoding','UTF-8','-cp',cp,'-d',str(pre/'classes'),*tests],R);write(pre/'manifest.json',dict(actualExit=stage['actualExit'],stage=stage,inputHashes=inputs,dependencies=deps,resourceHashes={p:sha(pre/'resources'/p) for p in cfg['resources']},classes={str(p.relative_to(pre/'classes')):sha(p) for p in (pre/'classes').rglob('*.class')},productionJavaClasspath=False,productTestsExecuted=0));print(dict(compile=stage['actualExit']));sys.exit(stage['actualExit'])
pm=load(pre/'manifest.json');assert pm['actualExit']==0 and pm['inputHashes']==inputs and pm['dependencies']==deps;assert all(sha(pre/'classes'/p)==h for p,h in pm['classes'].items());assert all(sha(pre/'resources'/p)==h for p,h in pm['resourceHashes'].items())
if phase=='static':
 assert not sta.exists();sta.mkdir();capture.SLOT=sta;sg=TC/'static-gates-20261015';rules=R/'tools/quality/static';listing=sta/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in tests));stages={};stages['pmd']=capture.step('pmd',[str(J/'java'),'-cp',':'.join(map(str,[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))])),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--aux-classpath',str(TC/'jdk-25.0.4/lib/jrt-fs.jar')+':'+cp,'--no-cache','--format','xml','--report-file',str(sta/'pmd.xml')],R);stages['checkstyle']=capture.step('checkstyle',[str(J/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(sta/'checkstyle.xml'),'@'+str(listing)],R);reports={}
 for name,tag in [('pmd','violation'),('checkstyle','error')]:
  tree=E.parse(sta/(name+'.xml')).getroot();reports[name]=dict(sha256=sha(sta/(name+'.xml')),items=[dict(x.attrib,message=' '.join(''.join(x.itertext()).split())) for x in tree.iter() if x.tag.rsplit('}',1)[-1]==tag],processingErrors=[dict(x.attrib) for x in tree.iter() if name=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']])
 write(sta/'manifest.json',dict(inputHashes=inputs,stages=stages,reports=reports,productTestsExecuted=0));print({n:len(v['items']) for n,v in reports.items()});sys.exit(0)
if phase=='preflight':
 out=R/cfg['preflightPath'];assert not out.exists();out.parent.mkdir();before=load(R/cfg['beforeManifest']);assert sha(R/cfg['beforeManifest'])==cfg['beforeSha256'];review=[]
 for p in tests:
  s=(R/p).read_text();old=subprocess.check_output(['git','show',cfg['beforeGit']+':'+p],text=True);v='pool' if 'var pool = Executors.' in s else 'executor';inverse=s.replace('    var '+v+' = Executors.newFixedThreadPool(2);\n    try {','    try (var '+v+' = Executors.newFixedThreadPool(2)) {');tail='    } finally {\n      '+v+'.shutdownNow();\n      assertTrue('+v+'.awaitTermination(10, TimeUnit.SECONDS));\n';assert inverse.count(tail)==1;inverse=inverse.replace(tail,'');assert inverse==old;assert old.count('.get(10, TimeUnit.SECONDS)')==s.count('.get(10, TimeUnit.SECONDS)');assert not re.search(r'^import dev\.codex\.',s,re.M);assert 'setMethod("GET")' in s and 'Jsoup.parse(' in s and 'ClassLoaderTemplateResolver' in s and 'Files.writeString(' in s and 'StandardOpenOption.CREATE_NEW' in s
  for forbidden in ['ProcessBuilder','Runtime.getRuntime','java.net.','DriverManager','new Socket','RestClient','WebClient','HttpClient','setMethod("POST")','SpringApplication','ApplicationContext','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']:assert forbidden not in s
  review.append(dict(path=p,sourceSha256=sha(R/p),rawExactInverse=True,originalOraclesAndAnnotationsPreserved=True,ownedAwaitSeconds=10,actualBackendOperations=0))
 for p in deps:
  with zipfile.ZipFile(p) as z:assert not any(n.startswith('dev/codex/schubert/nk/') for n in z.namelist())
 refs=set()
 for p in cfg['resources']:
  s=(pre/'resources'/p).read_text();assert not any(k in s for k in ['T(dev.codex','http://','https://']);refs.update(re.findall(r'~\{([\w/-]+) ::',s))
 assert refs=={'fragments/layout'};write(out,dict(actualExit=0,inputHashes=inputs,productionJavaClasspath=False,actualBackendOperations=0,review=review,resourceHashes=pm['resourceHashes'],resourceIncludes=sorted(refs),dependencies=deps,testsExpected=28,originalFixedQa055=True,productTestsExecuted=0));print(dict(preflight=0,testsExpected=28,sha256=sha(out)));sys.exit(0)
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pf=load(R/cfg['preflightPath']);assert pf['actualExit']==0 and pf['inputHashes']==inputs
assert not any(os.environ.get(k) for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']);assert not unit.exists();unit.mkdir();(unit/'tmp').mkdir();(unit/'output').mkdir();capture.SLOT=unit
cmd=[str(J/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djava.io.tmpdir='+str(unit/'tmp'),'-Downed.output='+str(unit/'output'),'-Djunit.jupiter.extensions.autodetection.enabled=false','-Djunit.jupiter.execution.parallel.enabled=false','-Xlog:class+init=info:file='+str(unit/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',':'.join([str(pre/'classes'),str(pre/'resources'),*deps]),'--reports-dir',str(unit/'xml'),'--fail-if-no-tests','--details','summary']
for cls in tests.values():cmd+=['--select-class',cls]
begin=dict(source=source,productionCoreMain=nm['source'],inputHashes=inputs,dependencyHashes=deps,resourceHashes=pm['resourceHashes'],compileSha256=sha(pre/'manifest.json'),preflightSha256=sha(R/cfg['preflightPath']),productionJavaClasspath=False,actualBackendOperations=0,expectedTests=28,selected=list(tests.values()),startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());write(unit/'begin.json',begin);stage=capture.step('unit',cmd,R,timeout=180);write(unit/'manifest.json',dict(actualExit=stage['actualExit'],stage=stage,begin=begin,formalUpdated=False));print(dict(unitExit=stage['actualExit']));sys.exit(stage['actualExit'])
