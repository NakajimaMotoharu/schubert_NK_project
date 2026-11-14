"""Source-only inventory contract checks; no application compilation or runtime."""
from pathlib import Path
import datetime,json,subprocess,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379/pg31464-source-ast-tool-v1';e=b/'evidence/PG31466-source-ast-tool-selftest-v1';e.mkdir();empty=w/'empty';empty.mkdir();toy=w/'toysrc';toy.mkdir();java=r.parent/'toolchain/jdk-25.0.4/bin/java';env=dict(JAVA_HOME=str(java.parent.parent),PATH=str(java.parent)+':/usr/bin:/bin',LANG='C.UTF-8',TZ='Asia/Tokyo');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
source='''package auditfixture;
import no.such.Dependency;
public class Holder {
  String text = """
      public record Phantom(int x) {}
      public enum PhantomEnum { BAD }
      """;
  // public record Commented(int x) {}
  record Member(int x) {}
  enum Tone { A, B }
  void f() { record Local(int y) {} }
  Object value = new Object() { record Inner(int z) {} };
  Dependency unresolved;
}
''';holder=toy/'Holder.java';holder.open('x').write(source);(e/'Holder.java.txt').open('x').write(source);before=sha(holder);commands=[]
def run(name,args,zero=True):
 cmd=[str(java),'-cp',str(w/'toolclasses'),'dev.codex.schubert.quality.DeclaredTypeInventory',*map(str,args)];start=datetime.datetime.now(datetime.timezone.utc).isoformat();v=subprocess.run(cmd,cwd=w,env=env,capture_output=True,timeout=60);out=e/(name+'.stdout');err=e/(name+'.stderr');out.write_bytes(v.stdout);err.write_bytes(v.stderr);row=dict(command=cmd,cwd=str(w),environment=env,actualExit=v.returncode,expectedZero=zero,startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdout=ref(out),stderr=ref(err));commands.append(row);(e/(name+'.json')).open('x').write(json.dumps(row,indent=2)+'\n');assert (v.returncode==0)==zero,(name,v.stderr.decode()[:700]);return v.stdout.decode()
text=run('parse-owned-fixture',[empty,holder]);rows=[line.split('\t') for line in text.splitlines() if line.startswith('TYPE\t')];tot=[line for line in text.splitlines() if line.startswith('TOTAL\t')];checks=[]
def check(identity,value,detail):assert value,(identity,detail);checks.append(dict(testId=identity,result='PASS_TOOL_ONLY',detail=detail))
check('TOOL-SOURCEAST001',len(rows)==4 and tot==['TOTAL\t1\t4'],dict(expectedRecords=3,expectedEnums=1,actual=rows))
actual={row[4]:row for row in rows};check('TOOL-SOURCEAST002',actual['auditfixture.Holder.Member'][5]=='auditfixture.Holder$Member' and actual['auditfixture.Holder.Tone'][5]=='auditfixture.Holder$Tone',dict(memberBinaryCandidatesFixed=True))
check('TOOL-SOURCEAST003',all('Phantom' not in row[4] and 'Commented' not in row[4] for row in rows),dict(textBlockAndCommentNotDeclarations=True))
local=[row for row in rows if row[6]=='LOCAL_OR_ANONYMOUS_UNBOUND'];check('TOOL-SOURCEAST004',len(local)==2 and all(row[5]=='-' for row in local),dict(localAndAnonymousBinaryNamesNotInvented=local))
check('TOOL-SOURCEAST005',not list(toy.rglob('*.class')) and not list(empty.iterdir()),dict(unresolvedImportAndFieldParsedWithoutAttribution=True,generatedClasses=0))
bad=toy/'Bad.java';bad.write_text('package auditfixture; public record Bad( {\n');run('reject-syntax',[empty,bad],False);check('TOOL-SOURCEAST006',True,dict(expectedNonzero='syntax error, no acceptance'))
notempty=w/'notempty';notempty.mkdir();(notempty/'marker.txt').write_text('owned');run('reject-nonempty-classpath',[notempty,holder],False);run('reject-missing-arguments',[empty],False);invalid=toy/'not-source.txt';invalid.write_text('owned');run('reject-nonjava-source',[empty,invalid],False);check('TOOL-SOURCEAST007',True,dict(nonemptyClasspathAndMissingOrNonJavaArgumentsRejected=True))
check('TOOL-SOURCEAST008',sha(holder)==before and not list(toy.rglob('*.class')) and not list(empty.iterdir()),dict(allInputBytesUnchanged=True,allAnalysisClassEmission=0,emptyClassSourceProcessorPaths=True,parseOnlyNoAnalyzeOrGenerate=True))
(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolSelfchecks=8,checks=checks,commands=commands,tool=ref(r/'tools/quality/source/DeclaredTypeInventory.java'),compiler=ref(b/'evidence/PG31464-source-ast-tool-v1/manifest.json'),applicationTestsExecuted=0,applicationClassesCompiledOrInitialized=0,noClassfileOutputFromParsing=True,formalUpdated=False,newAcceptance=0),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolSelfchecks=8,fixtureAstTypes=4,ignoredFakeDeclarations=3,applicationCompilation=0)))
