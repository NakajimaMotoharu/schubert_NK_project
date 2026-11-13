from pathlib import Path
import ast,copy,hashlib,json,subprocess,sys,datetime
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';sys.path.insert(0,str(R/'tools/quality'));import pgpt_closed_host_profile as h;import pgpt_unstarted_process as u
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));c=json.loads((B/'input/2201_mpol8_closed_profile.json').read_text());cases=[]
for label,mutate in [('extraMain',lambda x:x['mainSources'].append(u.SOURCE)),('extraTest',lambda x:x['testSources'].append(dict(path=u.TESTDIR+'OtherTest.java',tests=0))),('testFragment',lambda x:x['testSources'][0].update(tests=1)),('realParentRuntime',lambda x:x['physicalClasses'].append(u.BASE+'.class')),('missingEnum',lambda x:x['physicalClasses'].remove(u.ENUM+'.class')),('enumInitialization',lambda x:x['forbiddenInitializedClasses'].remove(u.ENUM)),('unknownWitness',lambda x:x['reviewedUnstartedProcess']['typeWitness'].update(sha256='0'*64)),('rootCapability',lambda x:x.update(reviewedGuardSignature={})),('reflection',lambda x:x.update(reviewedReflection=[{}])),('backendSDK',lambda x:x['sdkJars'].append('postgres/foo.jar')),('property',lambda x:x.update(systemProperties={'unreviewed':'true'})),('unboundSourceProof',lambda x:x['closureProofs'].pop(0))]:
 x=copy.deepcopy(c);mutate(x)
 try:u.syntax(x)
 except ValueError:cases.append(dict(id=label,rejected=True))
 else:raise AssertionError(label)
assert u.checked(c) is not None
factory=(R/u.FACTORY).read_text();assert u.allow_builder(c,u.FACTORY,factory);assert not u.allow_builder({},u.FACTORY,factory);assert not u.allow_builder(c,u.PLATFORM+'Other.java',factory);assert not u.allow_builder(c,u.FACTORY,'ProcessBuilder x;\n'+factory)
def fn(source,name):
 return ast.dump(next(x for x in ast.walk(ast.parse(source)) if isinstance(x,ast.FunctionDef) and x.name==name),include_attributes=False)
old=subprocess.check_output(['git','show','HEAD:tools/quality/pgpt_closed_host_profile.py'],text=True);assert fn(old,'compiler_element')==fn((R/'tools/quality/pgpt_closed_host_profile.py').read_text(),'compiler_element')
# Confirm exact ordinary JVM command expression retained rather than loosening admission.
old=subprocess.check_output(['git','show','HEAD:tools/quality/pgpt_closed_host_stages.py'],text=True)
def command(source):
 node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name=='run')
 return [ast.dump(x,include_attributes=False) for x in ast.walk(node) if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='cmd' for y in x.targets)]
assert command(old)==command((R/'tools/quality/pgpt_closed_host_stages.py').read_text())
old=subprocess.check_output(['git','show','HEAD:tools/quality/pgpt_closed_host_post.py'],text=True)
def counter_assignment(source):
 rows=[ast.dump(x,include_attributes=False) for x in ast.walk(ast.parse(source)) if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='counters' for y in x.targets)]
 assert len(rows)==1
 return rows[0]
assert counter_assignment(old)==counter_assignment((R/'tools/quality/pgpt_closed_host_post.py').read_text())
o=B/'evidence/PG28806-mpol-feature-metadata-qualification-v1';assert not o.exists();o.mkdir();(o/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),profile=ref(B/'input/2201_mpol8_closed_profile.json'),positiveCheckedSources=True,negativeSyntax=cases,factoryDefaultDenied=True,exactUncalledFactoryOnly=True,rootCompilerUnchanged=True,jvmCommandUnchanged=True,coverageCounterFunctionUnchanged=True,productClassActions=0,productTestsExecuted=0,newAcceptance=0,verifier=ref(Path(__file__).resolve())),indent=2)+'\n');print('metadata checks0; twelve negative cases; ProductPT0')
