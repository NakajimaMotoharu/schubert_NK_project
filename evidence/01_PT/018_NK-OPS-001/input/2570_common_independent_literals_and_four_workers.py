"""BUG2878/2879: exact test-only constant lifting and finite workers, preserving all old oracle tokens."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';pkg=r/'program/characterization/tests/java/dev/codex/schubert/characterization';e=b/'evidence/PG30716-common-test-literal-and-four-worker-repair-v1';assert not e.exists();e.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ledger=(r/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();assert all('## BUG-'+n+' ' in ledger for n in ['2878','2879'])
# Whole Java lexical tokens retain quoted literals/text blocks/comments without rewriting their contents.
lex=re.compile(r'(?P<BLOCKTEXT>""".*?""")|(?P<STRING>"(?:\\.|[^"\\])*")|(?P<CHAR>\'(?:\\.|[^\'\\])*\')|(?P<COMMENT>//[^\n]*|/\*.*?\*/)|(?P<WORD>[A-Za-z_$][\w$]*)|(?P<NUMBER>\d+)|(?P<OTHER>[^\s])',re.S)
tokens=lambda text:[(m.lastgroup,m.group()) for m in lex.finditer(text)]
replacements={
 '"chr.projectRoot"':'ORACLE_PROJECT_ROOT_PROPERTY','"verify-source"':'ORACLE_VERIFY_COMMAND',
 '"compare-current"':'ORACLE_COMPARE_COMMAND','"PASS"':'ORACLE_PASS','"status"':'ORACLE_STATUS',
 '"FAIL"':'ORACLE_FAIL','"failures"':'ORACLE_FAILURES',
 '"program/characterization/reports/current"':'ORACLE_CURRENT_REPORTS',
 '"pgpt-gate-20260901-05"':'ORACLE_FIRST_RUN','"pgpt-gate-20260901-06"':'ORACLE_SECOND_RUN',
 '"program/characterization/reports/current-repeat-comparison.json"':'ORACLE_REPEAT_REPORT',
 '"chr.usersFile"':'ORACLE_USERS_PROPERTY','"gates"':'ORACLE_GATES',
 '"chr.gateCommit"':'ORACLE_COMMIT_PROPERTY','"abcdef1"':'ORACLE_COMMIT'}
before={}; plans={}
for name,mapping in [('GateCliTest',replacements),('GateContractTest',{'"NK_ONLY"':'ORACLE_NK_ONLY'})]:
 p=pkg/(name+'.java');old=p.read_text();before[name]=old;(e/(name+'.before.java.txt')).write_text(old)
 assert all(identifier not in old for identifier in mapping.values()) and '"""' not in old
 new=''.join('' for _ in [])
 def sub(match):
  return mapping.get(match.group(),match.group()) if match.lastgroup=='STRING' else match.group()
 # Token replacement leaves every intervening whitespace and comment byte intact.
 new=lex.sub(sub,old)
 declaration=''.join('  private static final String '+identifier+' = '+literal+';\n' for literal,identifier in mapping.items())
 anchor='class '+name+' {\n';assert new.count(anchor)==1;new=new.replace(anchor,anchor+declaration)
 p.write_text(new);plans[name]=mapping
workers=['BaselineNumericMetadataTest','GateMetricsCountTest','GateDefinitionDocumentsTest','GateEvidenceDocumentsTest']
for name in workers:
 p=pkg/(name+'.java');old=p.read_text();before[name]=old;(e/(name+'.before.java.txt')).write_text(old)
 header='    try (var workers = Executors.newFixedThreadPool(2)) {\n';assert old.count(header)==1 and old.count('.get()')==2
 new=old.replace('import java.util.concurrent.Executors;\n','import java.util.concurrent.Executors;\nimport java.util.concurrent.TimeUnit;\n')
 new=new.replace(header,'    var workers = Executors.newFixedThreadPool(2);\n    try {\n').replace('.get()','.get(5, TimeUnit.SECONDS)')
 pos=new.index('    }\n',new.index('    var workers = Executors.newFixedThreadPool(2);'))
 new=new[:pos]+'    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n    }\n'+new[pos+6:]
 # NUM previously did not import assertTrue; it is used only for the new finite ownership condition.
 if 'import static org.junit.jupiter.api.Assertions.assertTrue;' not in new:
  new=new.replace('import static org.junit.jupiter.api.Assertions.assertThrows;\n','import static org.junit.jupiter.api.Assertions.assertThrows;\nimport static org.junit.jupiter.api.Assertions.assertTrue;\n')
 p.write_text(new)
tc=r.parent/'toolchain';paths=[pkg/(name+'.java') for name in before];fmt=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run([*fmt,'--replace',*map(str,paths)],check=True,capture_output=True,timeout=60)
proof=[]
for name,old in before.items():
 p=pkg/(name+'.java');new=p.read_text()
 if name in plans:
  inverse=tokens(new)
  for literal,identifier in plans[name].items():
   declaration=[('WORD','private'),('WORD','static'),('WORD','final'),('WORD','String'),('WORD',identifier),('OTHER','='),('STRING',literal),('OTHER',';')]
   places=[k for k in range(len(inverse)-len(declaration)+1) if inverse[k:k+len(declaration)]==declaration];assert len(places)==1
   k=places[0];del inverse[k:k+len(declaration)]
   inverse=[('STRING',literal) if item==('WORD',identifier) else item for item in inverse]
  assert inverse==tokens(old)
 else:
  inverse=new.replace('import java.util.concurrent.TimeUnit;\n','').replace('    var workers = Executors.newFixedThreadPool(2);\n    try {\n','    try (var workers = Executors.newFixedThreadPool(2)) {\n').replace('.get(5, TimeUnit.SECONDS)','.get()').replace('    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n    }\n','    }\n')
  if 'import static org.junit.jupiter.api.Assertions.assertTrue;' not in old:
   inverse=inverse.replace('import static org.junit.jupiter.api.Assertions.assertTrue;\n','')
  assert tokens(inverse)==tokens(old)
 assert len(re.findall(r'@Test\b',new))==len(re.findall(r'@Test\b',old))
 proof.append(dict(path=str(p.relative_to(r)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),allOtherJavaTokensAndLiteralBytesInverseEqual=True,testDefinitionsUnchanged=True))
commands=[]
for label,args in [('format-source-only',fmt+['--dry-run','--set-exit-if-changed',*map(str,paths)]),('checkstyle-source-only',[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),*map(str,paths)])]:
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:code=subprocess.run(args,stdout=out,stderr=err,timeout=60,check=False).returncode
 commands.append(dict(label=label,command=args,actualExit=code));assert code==0
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),bugs=['BUG-2878','BUG-2879'],testOnlyRepairs=proof,constantValuesFromOriginalTestsOnly=True,productionMethodOrConstantUsedToGenerateExpected=False,metadataFourWorkerSitesFixed=True,newTestDefinitions=0,allOriginalTestsAndOraclesRetained=True,commands=commands,productTestsExecuted=0,actualRemoteOperations=0,ordinaryNinetyOneAndPostPending=True)
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,allSixTestInverse=True,originalOraclesPreserved=True,newDefinitions=0,sourceGjfCs=0)))
