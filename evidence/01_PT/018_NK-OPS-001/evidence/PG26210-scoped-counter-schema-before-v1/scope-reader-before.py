"""Project P00103 counters and default-filter review from one qualified new Protocol run; no JVM."""
from pathlib import Path
import collections,datetime,hashlib,json,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=R/'evidence/01_PT/001_NK-PRO-001/evidence/PG26208-p00103-same-run-scoped-coverage-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
full=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG26206-protocol-whole124-range-independent-v1/manifest.json';assert sha(full)=='d2bd415f1fce8d1ae5521aaa89e9fd14838248275537741080619a233df8b678';m=load(full);assert m['actualExit']==0 and m['tests']==124 and m['measuredFour100'] is True
xml=full.parent/'coverage.xml';assert sha(xml)==m['files']['coverage.xml'];root=E.parse(xml).getroot();report={x.get('name'):x for x in root.findall('.//class')};scope=B/'evidence/PG24776-base6-method97-trace-independent-v1/p00103-all75-reference-summary.json';s=load(scope);paths=set(s['sourcePaths']);assert len(paths)==75
inv=load(B/'evidence/PG23972-current-main-method-delta42-v1/class-method-inventory.json');rows=[x for x in inv if x['physicalKey'].startswith('protocol:') and x['sourcePath'] in paths];assert len(rows)==75
counters=collections.defaultdict(lambda:dict(covered=0,missed=0));filters=[];sources=[];group=collections.Counter()
for x in rows:
 assert x['structure'] is not None and sha(R/x['sourcePath'])==x['sourceSha256'];name=x['physicalKey'].split(':',1)[1].removesuffix('.class');node=report[name];official={(v.get('name'),v.get('desc')) for v in node.findall('method')};text=(R/x['sourcePath']).read_text();record='public record ' in text
 for v in node.findall('counter'):
  t=counters[v.get('type')];t['covered']+=int(v.get('covered'));t['missed']+=int(v.get('missed'))
 for method in x['structure']['methods']:
  if not method['hasCode'] or (method['name'],method['descriptor']) in official:continue
  n=method['name'];d=method['descriptor']
  if record and n=='equals' and d=='(Ljava/lang/Object;)Z':reason='JAVAC_RECORD_EQUALS_STANDARD_JACOCO_FILTER';expected='Record component equality from the Java25 compiler contract; no authored equality logic or custom filter.'
  elif record and n=='hashCode' and d=='()I':reason='JAVAC_RECORD_HASH_STANDARD_JACOCO_FILTER';expected='Java25 generated component hash; no authored hash logic or manual exclusion.'
  elif record and d.startswith('()') and n not in ['toString','<init>','<clinit>']:
   reason='JAVAC_RECORD_ACCESSOR_STANDARD_JACOCO_FILTER';expected='Named getters: independent296 public getter assertions; base payload getters: literal input/immutable list and clone cases in normal124.'
  elif n=='<init>' and d=='()V' and name.endswith('/TypedFieldValues') and 'private TypedFieldValues() {}' in text:
   reason='PRIVATE_EMPTY_UTILITY_CTOR_STANDARD_JACOCO_FILTER';expected='Source confirms empty private constructor for noninstantiable utility, no authored behavior/branch; private reflection remains forbidden.'
  else:raise AssertionError((name,method))
  group[reason]+=1;filters.append(dict(className=name,sourcePath=x['sourcePath'],method=n,descriptor=d,reason=reason,independentReview=expected,measuredRuntimeCoverageClaimed=False))
 sources.append(dict(path=x['sourcePath'],sha256=x['sourceSha256'],physicalClass=name,physicalClassSha256=x['classSha256'],counters={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in node.findall('counter')}))
assert dict(counters)==s['coverageReferences'] and all(counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']);assert len(filters)==445 and group=={'JAVAC_RECORD_EQUALS_STANDARD_JACOCO_FILTER':71,'JAVAC_RECORD_HASH_STANDARD_JACOCO_FILTER':71,'JAVAC_RECORD_ACCESSOR_STANDARD_JACOCO_FILTER':302,'PRIVATE_EMPTY_UTILITY_CTOR_STANDARD_JACOCO_FILTER':1}
testxml=full.parent/'testcases.safe.xml';assert sha(testxml)==m['files']['testcases.safe.xml'];new=[x.attrib for x in E.parse(testxml).getroot().findall('testcase') if x.get('classname')=='dev.codex.schubert.nk.protocol.layout.TypedUnsignedRangeBoundaryTest'];assert len(new)==4
O.mkdir(parents=True);data={'source75-same-run-counters.json':sources,'default-filter445-explicit-review.json':filters,'new-range-four-case-references.json':new}
for n,v in data.items():(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalRun='PG26204-PROTOCOL-WHOLE124-RANGE',wholeModule=dict(path=str(full.relative_to(R)),sha256=sha(full)),owner='WBS-P001-03',sourceArtifacts=75,physicalClasses=75,measuredCodeClasses=73,nonExecutableInterfaces=2,coverage=dict(counters),measuredOwnerFour100=True,allSourceNonemptyBranch100Claimed=False,defaultFilteredMethods=len(filters),defaultFilterReasons=dict(group),filterPolicyChanged=False,manualCoverageExclusions=[],filterReviewIsNotRuntimeCoverage=True,sourceCodeSemanticsUnchanged=True,actualNewTestDefinitions=4,actualNewInputVectorsDeclared=113,testsReexecutedByThisProjection=0,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={n:sha(O/n) for n in data},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,ownerPhysical=75,coverage=dict(counters),filters=dict(group),newTestRefs=4,manifestSha256=sha(O/'manifest.json'))))
