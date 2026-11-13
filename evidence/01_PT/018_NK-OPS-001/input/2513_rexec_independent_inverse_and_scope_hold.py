"""Finish source-only correction proof; do not attempt outside-scope compile/run or change runner guards."""
from pathlib import Path
import json,hashlib,re,datetime,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';src=i/'2512_rexec5_closure_and_oracle_fix.py';originalScript=src.read_text();e=b/'evidence/PG30448-rexec-oracle-inverse-and-ordinary-scope-hold-v1';assert not e.exists();e.mkdir();(e/'original-executed-producer.py.txt').write_text(originalScript)
# Preserve the executed producer and remove an unused draft tautology, correcting literal escape.
needle=";assert golden(vector(new,'expectedWebVector'))==golden(web) if False else True";assert originalScript.count(needle)==1;corrected=originalScript.replace(needle,'').replace("'\\.start()'","'.start()'");src.write_text(corrected)
t=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedServiceExecArgumentsTest.java';new=t.read_text();before=b/'evidence/PG30444-rexec-original5-source-closure-before-fix-v1/before-test.java.txt';old=before.read_text();work=new
# Lift exact independent literal helpers back to each original assertion position.
helpers={}
for label in ['expectedWebVector','expectedApiVector']:
 pattern=r'  private static List<String> '+label+r'\(\) \{\n(.*?)\n  \}\n\n';match=re.search(pattern,work,re.S);assert match;body=match.group(1).strip();assert body.startswith('return List.of(') and body.endswith(';');helpers[label]=body[len('return '):-1];work=work[:match.start()]+work[match.end():]
workerNew='workers.submit(() -> expectedWebVector().equals(command.arguments()))';assert work.count(workerNew)==1;work=work.replace(workerNew,'workers.submit(() -> first.equals(command.arguments()))');agentNew='assertEquals(\n          service == ServiceConfigFiles.Service.API ? expectedApiVector() : expectedWebVector(),\n          withoutAgent);';assert work.count(agentNew)==1;work=work.replace(agentNew,'assertEquals(command.arguments(), withoutAgent);')
for name,literal in helpers.items():assert work.count(name+'()')==1;work=work.replace(name+'()',literal)
newHeader='    var workers = Executors.newFixedThreadPool(4);\n    try {';assert work.count(newHeader)==1;work=work.replace(newHeader,'    try (var workers = Executors.newFixedThreadPool(4)) {');cleanup='    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS), "owned argv workers terminate");\n    }';assert work.count(cleanup)==1;work=work.replace(cleanup,'    }')
# Whitespace may be formatted; retain every Java string/character literal as one exact token.
tokens=lambda s:re.findall(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/|[A-Za-z_$][\w$]*|\d+|[^\s]',s,re.S);assert tokens(work)==tokens(old);assert len(re.findall(r'@Test\b',new))==5
closure=json.loads((b/'evidence/PG30444-rexec-original5-source-closure-before-fix-v1/manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
for row in closure['allMainSources']:assert sha(r/row['path'])==row['sha256']
runner=r/'tools/quality/pgpt_closed_host_profile.py';policy=runner.read_text();assert "'java.lang.foreign'" in policy and "require('ProcessBuilder' not in text or process.allow_builder" in policy
blocked=[]
for row in closure['allMainSources']:
 text=(r/row['path']).read_text();reasons=[word for word in ['java.lang.foreign','ProcessBuilder'] if word in text]
 if reasons:blocked.append(dict(path=row['path'],sha256=row['sha256'],closedHostForbiddenTokens=reasons))
assert {Path(x['path']).stem for x in blocked}=={'LinuxDirectoryCalls','FixedServiceIdentity'}
commands=[];tc=r.parent/'toolchain'
for label,args in [('format-source-only',[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(t)]),('checkstyle-source-only',[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),str(t)])]:
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:code=subprocess.run(args,stdout=out,stderr=err,check=False,timeout=60).returncode
 commands.append(dict(label=label,command=args,actualExit=code,startUTC=now,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()));assert code==0
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='24fff256ecba4b544780816a4e2d02c1c134bd08',bugs=['BUG-2870','BUG-2871'],allElevenMainBytesUnchanged=True,wholeFiveTestDefinitionsUnchanged=True,allOtherJavaTokensInverseEqual=True,allStringAndCharLiteralBytesInverseEqual=True,expectedHelpersContainProductionCalls=False,finiteWorkerSourceCorrected=True,commands=commands,toolProducerCorrection=dict(original=ref(e/'original-executed-producer.py.txt'),current=ref(src),reason='Removed unused draft conditional-true assertion and corrected literal escaped dot. Actual helper-vector checks and independently computed full Java-token inverse establish proof, not the draft line. Producer not replayed; production Test changed only before this independent check.'),normalGateRule=ref(runner),outsideOrdinaryClosure=blocked,decision='NOT_RUN_HOLD_FULL_CLOSURE_OUTSIDE_NORMAL_HOST_SCOPE',normalPrestylePrepareStaticUnitPostAttempted=False,productClassesCompiled=0,productTestsExecuted=0,coverage=None,ordinaryRunnerOrHoldsChanged=False,alternativeOrExtractedTypeExecution=0,actualVmRootDbNativeKeyUnitArgvExecution=0,formalUpdated=False,newAcceptance=0)
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,fullOtherTokenAndLiteralInverse=True,MainChanges=0,whole5NotRun=True,outsideOrdinaryClosure=blocked)))
