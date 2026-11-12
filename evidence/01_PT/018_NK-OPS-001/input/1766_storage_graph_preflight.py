"""Independent exact-source/static preflight; no product method invocation."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27688-storage-public-graph-v1';O=B/'evidence/PG27692-storage-graph-preflight-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));pp=B/'evidence/PG27689-storage-graph-test-import-v2/manifest.json';m=ld(pp);assert not O.exists() and m['actualExit']==0
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('target/classes','physicalClassHashes'),('test-classes-v2','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
original=R/m['initialPrepare']['path'];first=ld(original);assert sha(original)==m['initialPrepare']['sha256'] and first['physicalClassHashes']==m['physicalClassHashes'] and all(first['inputHashes'][p]==m['inputHashes'][p] for p in m['mainSources'])
assert m['importCorrection']['inverseExact'] and not m['importCorrection']['assertionsChanged']
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');assert hashlib.sha256(ET.tostring(compiler)).hexdigest()==first['rootCompilerSha256']
sp=B/'evidence/PG27691-storage-graph-test-static-v2/manifest.json';st=ld(sp);assert st['inputHashes']==m['inputHashes'] and not st['rawFindings'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert {n.removesuffix('.class').replace('/','.') for n in m['physicalClassHashes']}==set(st['spotbugs']['classStats'])
for manifest,stages in [(original,first['stages']),(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==0 and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert len(m['mainSources'])==2 and len(m['testSources'])==1 and len(m['expectedCases'])==4 and len(m['physicalClassHashes'])==3
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),originalMainCompile=ref(original),static=ref(sp),rootCompilerUnchanged=True,initialNewTestStyleFailureRetained=True,MainSourcesRecompiledForImportFix=0,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,productTestsExecuted=0,newDefinitions=4,actualBackendNativeHeldClassOrDirectoryAccess=0,formalUpdated=False,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
