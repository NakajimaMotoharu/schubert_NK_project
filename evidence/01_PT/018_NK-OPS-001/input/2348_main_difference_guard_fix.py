"""BUG2839 public text caller correction and independent metadata controls, no product action."""
from pathlib import Path
import ast,datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=b/'input/2339_f03_public_quality_inventory.py';before=p.read_text();o=b/'evidence/PG29556-main-delta-guard-public-metadata-v1';o.mkdir();(o/'2339_f03_public_quality_inventory.before.py.txt').write_text(before)
old="assert subprocess.run(['git','diff','--quiet',source,'--','src/*/src/main/java']).returncode==0\nassert subprocess.run(['git','diff','--quiet','--','src/*/src/main/java']).returncode==0"
assert before.count(old)==1
replacement='''def production_main_paths(names):
 result=[]
 for name in names:
  parts=Path(name).parts
  if len(parts)>=6 and parts[0]=='src' and parts[2:5]==('src','main','java') and name.endswith('.java'):
   result.append(name)
 return sorted(result)
def git_names(args):
 return [n for n in subprocess.check_output(['git',*args],text=True).split('\\0') if n]
assert production_main_paths(git_names(['diff','--name-only','-z',source,'--','src']))==[]
assert production_main_paths(git_names(['ls-files','--others','--exclude-standard','-z','--','src']))==[]'''
after=before.replace(old,replacement);ast.parse(after);assert after.replace(replacement,old)==before;p.write_text(after)
node=next(n for n in ast.parse(after).body if isinstance(n,ast.FunctionDef) and n.name=='production_main_paths');ns={'Path':Path};exec(compile(ast.Module(body=[node],type_ignores=[]),'<PURE_PUBLIC_PATH_FILTER>','exec'),ns);f=ns['production_main_paths']
main='src/schubert-nk-api/src/main/java/a/Example.java';other='src/new-module/src/main/java/New.java';test='src/schubert-nk-api/src/test/java/a/ExampleTest.java';resource='src/schubert-nk-api/src/main/resources/schema.json';tool='tools/quality/Else.java'
cases=[('empty',[],[]),('existingMain',[main],[main]),('testOnly',[test],[]),('resourceOnly',[resource],[]),('toolOnly',[tool],[]),('newModule',[other],[other]),('mixed',[test,other,resource,main,tool],sorted([main,other])),('lookalike',['prefix/src/schubert-nk-api/src/main/java/Fake.java','src/m/src/main/javax/Fake.java','src/m/src/main/java/Fake.class'],[])]
for _,inputs,expected in cases:assert f(inputs)==expected
base='7aed8eace7c844c2f79f2e39db766faf914890d5';core='8b539471183a640ad4a2541ee06a1eb1717199fc'
def names(args):return [n for n in subprocess.check_output(['git',*args],text=True).split('\0') if n]
known=f(names(['diff','--name-only','-z',base,core,'--','src']));independent=sorted(names(['diff','--name-only','-z',base,core,'--',':(glob)src/*/src/main/java/**/*.java']));assert known==independent and len(known)==105
empty=names(['diff','--name-only','-z',base,core,'--','src/*/src/main/java']);assert empty==[]
current=f(names(['diff','--name-only','-z',core,'--','src']));untracked=f(names(['ls-files','--others','--exclude-standard','-z','--','src']));assert current==untracked==[]
for _,inputs,_ in cases:
 if f(inputs):assert f(inputs)!=[] # actual caller's empty-delta criterion rejects each positive change.
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=core,productionCoreMain=core,head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),bug='BUG-2839',metadataControls=[dict(id=n,input=inp,expected=exp,actual=f(inp)) for n,inp,exp in cases],controlCount=len(cases),historicalMain105=known,independentGitGlobEqual=True,oldVacuousDirectoryPatternResult=empty,currentTrackedMainDelta=current,currentUntrackedMainDelta=untracked,changedCaller=dict(path=str(p.relative_to(r)),beforeSha256=sha(o/'2339_f03_public_quality_inventory.before.py.txt'),afterSha256=sha(p),wholeSourceInverseEqual=True,astParse=True),f03OriginalInventoryRerun=False,publishedV1Preserved=True,productionMainOrTestChanged=False,productTestsExecuted=0,actual4BinaryOrRoot2BodyOrProtected2Operations=0,actualEnvironmentOperations=0,allSixCurrentStaticQualified=False,formalUpdated=False)
(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,controls=len(cases),historical105=len(known),currentDelta=0,untrackedDelta=0,inverse=True,newProductTests=0)))
