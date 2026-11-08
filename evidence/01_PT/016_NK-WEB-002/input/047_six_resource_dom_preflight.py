"""Six-resource preflight: exact source provenance, fixed namespace, no product Java."""
from pathlib import Path
from html.parser import HTMLParser
import datetime,hashlib,json,re,subprocess
R=Path.cwd();W=R.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
cfg=load(R/'evidence/01_PT/016_NK-WEB-002/input/046_six_resource_dom_scope.json');pm=load(W/cfg['compileSlot']/'manifest.json');out=R/cfg['preflightPath'];assert not out.exists();assert pm['actualExit']==0;assert all(sha(R/p)==h for p,h in pm['inputHashes'].items());review=[]
class ResourceAttributes(HTMLParser):
 def __init__(self):super().__init__();self.namespaces=[];self.resourceNames=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k=='xmlns:th':assert v=='http://www.thymeleaf.org';self.namespaces.append(v)
   elif v is not None:assert 'http://' not in v and 'https://' not in v and 'T(dev.codex' not in v
for p in cfg['testClasses']:
 s=(R/p).read_text();old=subprocess.check_output(['git','show',cfg['beforeGit']+':'+p],text=True);v='pool' if 'var pool = Executors.' in s else 'executor';start='    var '+v+' = Executors.newFixedThreadPool(2);\n    try {';assert s.count(start)==1;inverse=s.replace(start,'    try (var '+v+' = Executors.newFixedThreadPool(2)) {');tail='    } finally {\n      '+v+'.shutdownNow();\n      assertTrue('+v+'.awaitTermination(10, TimeUnit.SECONDS));\n';assert inverse.count(tail)==1;inverse=inverse.replace(tail,'');assert inverse==old;assert old.count('.get(10, TimeUnit.SECONDS)')==s.count('.get(10, TimeUnit.SECONDS)');assert not re.search(r'^import dev\.codex\.',s,re.M)
 for required in ['setMethod("GET")','Jsoup.parse(','ClassLoaderTemplateResolver','Files.writeString(','StandardOpenOption.CREATE_NEW']:assert required in s
 for forbidden in ['ProcessBuilder','Runtime.getRuntime','java.net.','DriverManager','new Socket','RestClient','WebClient','HttpClient','setMethod("POST")','SpringApplication','ApplicationContext','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']:assert forbidden not in s
 review.append(dict(path=p,sha256=sha(R/p),rawExactInverse=True,originalOraclesAndAnnotationsPreserved=True,futureGetSeconds=10,ownedAwaitSeconds=10,actualBackendOperations=0))
refs=set();parsers=[]
for p in cfg['resources']:
 s=(W/cfg['compileSlot']/'resources'/p).read_text();h=ResourceAttributes();h.feed(s);assert h.namespaces==['http://www.thymeleaf.org'];assert 'T(dev.codex' not in s;refs.update(re.findall(r'~\{([\w/-]+) ::',s));parsers.append(dict(resource=p,namespaces=h.namespaces))
assert refs=={'fragments/layout','fragments/pagination'}
negative=[]
for bad in ['<html xmlns:th="https://unknown.invalid">','<a href="https://outside.invalid">','<img src="http://outside.invalid">','<div th:text="T(dev.codex.Example)">']:
 try:h=ResourceAttributes();h.feed(bad)
 except AssertionError:negative.append(True)
 else:raise AssertionError('negative accepted')
static=load(W/cfg['staticSlot']/'manifest.json');assert static['inputHashes']==pm['inputHashes'];assert static['stages']['pmd']['actualExit']==4 and static['stages']['checkstyle']['actualExit']==0;assert not static['reports']['pmd']['processingErrors'] and not static['reports']['checkstyle']['items'];app=[]
for row in static['reports']['pmd']['items']:
 assert row['rule'] in ['CloseResource','DoNotUseThreads'];p=next(p for p,cls in cfg['testClasses'].items() if cls.endswith('.'+row['class']));lines=(R/p).read_text().splitlines();line=int(row['beginline']);assert 1<=line<=len(lines);s=(R/p).read_text();assert '.shutdownNow();' in s and '.awaitTermination(10, TimeUnit.SECONDS)' in s
 app.append(dict(test=p,line=line,rule=row['rule'],applicable=False,reason='Explicit finally shutdownNow plus finite successful awaitTermination' if row['rule']=='CloseResource' else 'Standalone owned JUnit memory renderer, no managed J2EE application threads'))
assert len(app)==30 and sum(x['rule']=='CloseResource' for x in app)==6
v=dict(actualExit=0,inputHashes=pm['inputHashes'],productionJavaClasspath=False,actualBackendOperations=0,review=review,resourceHashes=pm['resourceHashes'],resourceIncludes=sorted(refs),namespaceEvidence=parsers,namespaceNegativeCases=4,dependencies=cfg['dependencies'],testsExpected=43,originalPureResourceOracles=True,productTestsExecuted=0,pmdRaw=30,pmdApplicable=0,staticApplicability=app,preflightDriver=dict(path=str(Path(__file__)),sha256=sha(__file__)),supersededFailure=None,atJST=datetime.datetime.now().astimezone().isoformat());out.parent.mkdir();out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(preflight=0,negative=4,pmdRaw=30,pmdApplicable=0,sha256=sha(out))))
