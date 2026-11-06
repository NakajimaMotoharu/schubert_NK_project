"""Read-only post of the completed CSS tests/build; no original Test helper imports or reruns."""
from pathlib import Path
import json,hashlib,subprocess,xml.etree.ElementTree as E,ast,shutil,re,zipfile,datetime
import tinycss2
R=Path.cwd();W=R.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());SOURCE='fb189b11ee9dc39a5ef269f4018b809439cfc0f9';assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==SOURCE
gp=R/'evidence/01_PT/016_NK-WEB-002/input/030_media_css_golden.json';g=load(gp);nm=W/'pg20704-media-css-six-main-resource-compile-v1/manifest.safe.json';assert sha(nm)=='8bf2c7ca6ada19b2e23a1e007ca2db680d6916d1e215d470f072f27508d23be9';normal=load(nm);ci=normal['classIdentity'];assert normal['actualExit']==0 and normal['source']==SOURCE and normal['sourceInputsUnchanged'] and ci['physicalClasses']==1844 and ci['codeOrDebugDifferences']==0 and ci['allJavaMainSourceBytesUnchanged'] and ci['allPomBytesUnchanged'];assert normal['begin']['changes']==['src/schubert-nk-web/src/main/resources/static/css/schubert.css']
unit=W/'pg20706-new-media-css-green-v1';um=load(unit/'manifest.safe.json');result=load(unit/'results/manifest.json');assert um['actualExit']==result['actualExit']==0 and result['source']==SOURCE and result['tests']==7 and all(result[k]==0 for k in ['failures','errors','skipped','aborted']);stage=um['stage'];assert stage['actualExit']==0 and not stage['timedOut'] and stage['stdoutSha256']==sha(unit/'unit.stdout') and stage['stderrSha256']==sha(unit/'unit.stderr');assert um['childManifestSha256']==sha(unit/'results/manifest.json')
for name,h in result['inputBindings'].items():assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+name])).hexdigest()
for name,h in result['files'].items():assert sha(unit/'results'/name)==h
code=ast.parse((R/'evidence/01_PT/016_NK-WEB-002/input/029_media_css_contracts.py').read_text());cls=next(n for n in code.body if isinstance(n,ast.ClassDef) and n.name=='CssCompatibilityContracts');expected={n.name for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')};xml=E.parse(unit/'results/tests.xml').getroot();cases=xml.findall('testcase');assert len(cases)==len(expected)==7 and {x.get('name') for x in cases}==expected and all(not list(x) for x in cases);assert len(result['cases'])==7 and all(x['status']=='PASS' for x in result['cases'])
jar=Path(normal['jars']['web']['path']);assert sha(jar)==normal['jars']['web']['sha256'];data=zipfile.ZipFile(jar).read('static/css/schubert.css');assert hashlib.sha256(data).hexdigest()==um['actualCssSha256']==result['actualCssSha256']==sha(unit/'actual-css.css');assert data==subprocess.check_output(['git','show',SOURCE+':src/schubert-nk-web/src/main/resources/static/css/schubert.css']);original=(R/g['before']['snapshot']).read_bytes();assert hashlib.sha256(original).hexdigest()==g['before']['sha256'];assert data.startswith(original)
# Independent AST walk directly against standard parser, not input029.parse/one.
actual={}
def collect(nodes,contexts=()):
 for node in nodes:
  if node.type=='at-rule':
   assert node.lower_at_keyword=='media' and node.content is not None;param=' '.join(tinycss2.serialize(node.prelude).split());param=re.sub(r':\s*',':',param);collect(tinycss2.parse_rule_list(node.content,skip_comments=True,skip_whitespace=True),contexts+('media:'+param,));continue
  assert node.type=='qualified-rule';sel=re.sub(r'\s*,\s*',',',' '.join(tinycss2.serialize(node.prelude).split()));properties={}
  for decl in tinycss2.parse_declaration_list(node.content,skip_comments=True,skip_whitespace=True):
   assert decl.type=='declaration' and not decl.important and decl.lower_name not in properties;properties[decl.lower_name]=tinycss2.serialize(decl.value).strip()
  actual.setdefault((contexts,sel),[]).append(properties)
collect(tinycss2.parse_stylesheet(data.decode(),skip_comments=True,skip_whitespace=True));comparisons=[]
for row in g['rules']:
 key=(tuple(row['context']),re.sub(r'\s*,\s*',',',row['selector']));matches=actual.get(key,[]);assert len(matches)==1 and matches[0]==row['properties'];comparisons.append(dict(context=row['context'],selector=row['selector'],expected=row['properties'],actual=matches[0],matched=True))
assert len(comparisons)==16 and sum(len(x['actual']) for x in comparisons)==62
assert sha(Path(g['current']['path']))==g['current']['sha256'];templates={}
for p in (R/'src/schubert-nk-web/src/main/resources/templates').rglob('*.html'):
 classes=set(c for group in re.findall(r'class="([^"]*)"',p.read_text()) for c in group.split())
 if classes&{'video-shell','music-player','song-player'}:templates[str(p.relative_to(R))]=sorted(classes&{'video-shell','music-player','song-player'})
assert templates=={'src/schubert-nk-web/src/main/resources/templates/animation-watch.html':['video-shell'],'src/schubert-nk-web/src/main/resources/templates/music-list.html':['music-player','song-player']}
base=R/'evidence/01_PT/016_NK-WEB-002/evidence'
for name,src in [('PG20704-media-css-normal-six-v1',W/'pg20704-media-css-six-main-resource-compile-v1'),('PG20706-new-media-css-green-v1',unit)]:
 out=base/name;assert not out.exists();out.mkdir();pins={}
 for p in src.iterdir():
  if p.is_file() and (p.name.endswith(('.json','.stdout','.stderr','.css'))):dest=out/p.name;shutil.copyfile(p,dest);pins[dest.name]=sha(dest)
 if (src/'results').exists():
  shutil.copytree(src/'results',out/'results')
  for p in (out/'results').iterdir():pins['results/'+p.name]=sha(p)
 value=dict(actualExit=0,source=SOURCE,files=pins,scope='NORMAL_COMPILE_NO_TEST_PASS' if src==W/'pg20704-media-css-six-main-resource-compile-v1' else 'SEVEN_CSS_RESOURCE_CONTRACTS_NO_BROWSER',testsExecuted=False if src!=unit else True,productTests=7 if src==unit else 0,javaCoverage=None)
 (out/'manifest.json').write_text(json.dumps(value,indent=2)+'\n')
out=base/'PG20708-media-css-independent-post-v1';assert not out.exists();out.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),runtimeSource=SOURCE,producerPath=str(Path(__file__).relative_to(R)),producerSha256=sha(Path(__file__)),producerGitBinding='PENDING_NEXT_PUBLICATION_SEPARATE_VERIFIER_SOURCE',normalManifestSha256=sha(nm),greenManifestSha256=sha(unit/'manifest.safe.json'),tests=7,failures=0,errors=0,skipped=0,aborted=0,xmlMethods=sorted(expected),comparisons=comparisons,ruleContractsMatched=16,propertiesMatched=62,oldPrefixBytesPreserved=True,oldPrefixSha256=g['before']['sha256'],actualCssSha256=hashlib.sha256(data).hexdigest(),oldRed=dict(source='dd1a916c70c30cf3760103d22208a68063d28fd9',tests=7,failures=7,notCounted=True),classIdentity=ci,affectedTemplates=templates,scope='Static CSS asset/Current values only. No computed Browser/layout/media/API/runtime/native/CHR/451 or old source union.',productTestsReexecutedByPost=0,javaCoverage=None,newAccepted=0,formalUpdated=False,toolchainManifestSha256=sha(R.parent/'toolchain/css-contract-parser-1.4.0/manifest.json'),canonicalOwner='WBS-P016-25',changeOwners=['WBS-P016-10','WBS-P016-13'],bugs=['BUG-2350','YKT-2095']);(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(dict(postExit=0,tests=7,matchedRules=16,matchedProperties=62,javaClassByteDifferences=0,manifestSha256=sha(out/'manifest.json')))
