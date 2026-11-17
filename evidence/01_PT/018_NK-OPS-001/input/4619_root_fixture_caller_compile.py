"""Strict compile of all changed Test callers and their complete local Test helper closure; never run them."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_catch_manual_lexer import lexical
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
plan=ld(w/'pg37160-test-caller-compile-source-plan.json');inventory=ld(b/'evidence/PG37158-root-fixture-consumer-alignment-v1/consumer-inventory.json');p=ld(b/'evidence/PG37134-caddy20-prepare-static-v1/manifest.json');component=Path(p['work'])/'component';assert len(plan['sources'])==16 and len(p['physicalClassHashes'])==1101
assert all(sha(component/n)==h for n,h in p['physicalClassHashes'].items())
for path in plan['sources']:
 assert Path(path).stem not in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest']
 words={a for a,pos in lexical((r/path).read_text())};assert not words&{'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'}
out=b/'evidence/PG37160-root-fixture-caller-compile-v1';slot=w/'pg37160-root-fixture-caller-compile-v1';assert not out.exists() and not slot.exists();out.mkdir();slot.mkdir();formats=[]
def signature(text):
 v=[]
 for word,at in lexical(text):
  if word!='LITERAL':v.append(word);continue
  if text.startswith('"""',at):end=text.index('"""',at+3)+3
  else:
   end=at+1
   while text[end]!=text[at]:end+=2 if text[end]=='\\' else 1
   end+=1
  v.append(('LITERAL',text[at:end]))
 return v
for x in inventory:
 if not x['changes']:continue
 path=r/x['path'];before=path.read_text();assert sha(path)==x['shaAfter'];name=path.name
 cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--assume-filename',name,'-'];start=datetime.datetime.now(datetime.timezone.utc).isoformat();c=subprocess.run(cmd,input=before,text=True,capture_output=True,timeout=120);end=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (out/(name+'.format.stdout')).write_text(c.stdout);(out/(name+'.format.stderr')).write_text(c.stderr);assert c.returncode==0 and not c.stderr and signature(before)==signature(c.stdout)
 path.write_text(c.stdout);formats.append(dict(path=x['path'],shaBefore=x['shaAfter'],shaAfter=sha(path),actualExit=c.returncode,command=cmd,startUTC=start,endUTC=end,allTokensAndLiteralsIdentical=True))
classes=slot/'test-classes';classes.mkdir();deps=[tc/'junit-platform-console-standalone-1.13.4.jar',tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',tc/'m2/repository/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',tc/'m2/repository/org/checkerframework/checker-qual/3.55.1/checker-qual-3.55.1.jar'];assert all(x.is_file() for x in deps)
cmd=[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',':'.join(map(str,[component,*deps])),'-d',str(classes),*[str(r/n) for n in plan['sources']]];stage.SLOT=out;stage.ENV=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8');result=stage.step('test-caller-compile',cmd,slot,timeout=120)
v=dict(actualExit=result['actualExit'],terminalAtUTC=result['endUTC'],timedOut=result['timedOut'],inputHashes={n:sha(r/n) for n in plan['sources']},formatChanges=formats,sourceClosureCount=16,changedCallerSources=8,alignedFieldReferences=11,wholeMainContext=1101,mainClassHashes=p['physicalClassHashes'],testClassHashes={str(x.relative_to(classes)):sha(x) for x in classes.rglob('*.class')},toolDependencies={str(x):sha(x) for x in deps},stage=result,productTestsExecuted=0,rootOrNativeTestsSelected=0,heldClassfilesReadCompiledOrLoaded=False,actualRootVmDbOrServiceActions=0,bug='BUG3158',horizontal='YKT2627',formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=result['actualExit'],sources=16,changedCallers=8,productTestsExecuted=0)));assert result['actualExit']==0 and not result['timedOut']
