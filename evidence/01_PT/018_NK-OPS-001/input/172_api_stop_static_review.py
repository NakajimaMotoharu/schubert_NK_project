"""Bind already executed static scans, unchanged diagnostic anchors and saved offline probes."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
normalp=w/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';sbp=w/'pg22086-api-stop-state-six-static-reactor-v1/manifest.safe.json';stylep=w/'pg22094-api-stop-state-style-v2/raw-manifest.safe.json';normal,sb,style=map(load,[normalp,sbp,stylep]);assert sha(normalp)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and sha(sbp)=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2' and normal['actualExit']==sb['actualExit']==0
assert len(sb['reports'])==6 and all(v['bugs']==v['errors']==v['missing']==0 for v in sb['reports'].values()) and sb['jarsStillEqualCompile'] and sb['normalCompileManifestSha256']==sha(normalp)
assert len(style['findings'])==25 and style['stages']['pmd']['actualExit']==4 and style['stages']['checkstyle']['actualExit']==0 and not style['processingErrors']
for n,h in style['inputHashes'].items():assert sha(r/n)==h
reviewp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG20154-current-d8-context-requalification-v1/review.json';oldreview=load(reviewp);rawp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG20150-current-d8-six-main-static-v1/manifest.json';raw=load(rawp);judgments=[];main_count=0
for index,f in enumerate(style['findings']):
 n=f['path'];a=f['attributes'];text=(r/n).read_text().splitlines();span=text[int(a['beginline'])-1:int(a['endline'])];rule=a['rule'];method=a.get('method');prior=[]
 if '/src/main/' in n:
  current={k:v for k,v in a.items() if k not in ['beginline','endline']}
  for row in oldreview['classified']:
   o=row['rawFinding']
   if o['path']!=n or o['message']!=f['message'] or {k:v for k,v in o['attributes'].items() if k not in ['beginline','endline']}!=current:continue
   oldtext=subprocess.check_output(['git','show',raw['normalSource']+':'+n],text=True).splitlines();oldspan=oldtext[int(o['attributes']['beginline'])-1:int(o['attributes']['endline'])]
   if oldspan==span:prior.append(row)
  assert prior and all(x['actualViolation'] is False for x in prior)
  if rule=='AvoidSynchronizedStatement':reason='ApiStopBudget.'+method+': same private lock must serialize first clock capture and remaining readers. Atomic publication does not remove that mutual exclusion. Actual production supplier is System.nanoTime, no arbitrary I/O. No blanket Java25 monitor/native-performance exemption.'
  elif rule=='CompareObjectsWithEquals':reason='ApiProcessLifetime.shutdown: Thread.currentThread()==owner is identity of the exact captured cleanup owner; substituting arbitrary Thread.equals would alter the owner gate. Stop publication change does not touch this line.'
  else:assert rule=='DoNotUseThreads';reason='ApiProcessLifetime.'+str(method or a.get('variable','field'))+': standalone API owns fixed owner/hook notification and interrupt preservation; not a J2EE deployment. Same source span and existing independent context judgment; no hook/TERM execution or stopping-completion inference.'
  main_count+=1
 else:
  assert n.endswith('/ApiStopBudgetTest.java')
  if rule=='DoNotUseThreads':reason='ApiStopBudgetTest.'+str(method)+': own finite latch/pool/Future scenario and interrupt restoration. Original helper/015/016 or new019 only; JVM180s owns all test threads, no external worker/runtime. J2EE restriction is inapplicable to this standalone JUnit test.'
  elif rule=='NullAssignment':assert all('f.failure = null;' in x for x in span);reason='ApiStopBudgetTest.'+str(method)+': clear only the synthetic failure injection, then verify already published stop/sticky exhausted budget without another clock read. Not Production null normalization or live resource disposal.'
  else:assert rule=='AvoidUsingVolatile';assert any('volatile ' in x for x in span);reason='ApiStopBudgetTest.Fixture: explicit volatile Throwable/Runnable port provides cross-thread visibility for the two owned test workers. No compound mutation is justified by volatile; counts/latches remain atomic/synchronized.'
 judgments.append(dict(ordinal=index,raw=f,sourceSha256=sha(r/n),sourceSpan=span,classification='CONTEXTUAL_NONAPPLICABLE',actualViolation=False,reason=reason,priorMatches=[x['id'] for x in prior],priorReasons=[x['reason'] for x in prior]))
assert main_count==9 and len(judgments)-main_count==16
bp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22096-api-stop-state-bytecode-format-v1/manifest.json';pm=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22102-api-stop-probe-metadata-v1/manifest.json';bytecode,probes=map(load,[bp,pm]);assert sha(bp)=='016ef6b91df81c9e4ed6724a8b521615b7d7d4dba1bc9412c9804ae9abb08a06' and sha(pm)=='6b56090164a8ad7679fdc34eece9cd5d1ef19e3b8528d69225f9322d834211c0';assert bytecode['actualExit']==probes['actualExit']==0 and bytecode['productInitialisations']==probes['productInitialisations']==0
j=(pm.parent/'javap.stdout').read_text();time=j.split('private long time();',1)[1].split('static {};',1)[0];assert probes['probeRecords']==[dict(crc='aac04d643a58f83d',name='dev/codex/schubert/nk/api/bootstrap/ApiStopBudget',probeCount=29,unhit=[23,25])]
assert re.search(r'48: bipush\s+23',time) and re.search(r'67: bipush\s+25',time) and '31: ifeq          42' in time and '63: ifeq          74' in time
interpretation=dict(actualExit=0,sourceMethod='ApiStopBudget.time',rawHit=27,rawTotal=29,unhit=[23,25],unhitLocations={'23':'offline BCI42..51: normal return finally copy with returned=false, despite preceding assignment=true','25':'offline BCI66..70: exception finally copy with returned=true; supplier throw precedes that assignment'},logicalSourceCondition='if (!returned) expired=true; normal success and supplier RuntimeException/Error both exercised',coveredSiblingProbes=[22,24,26,27],sourceConditionBranches={'covered':2,'missed':0},reportPolicy='Standard JaCoCo0.8.15 javac duplicated-finally filtering; no manual excludes, no artificial calls or forced VM faults',wholePhysicalSourceIncluded=True,newCoverageExecution=False)
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22106-api-stop-static-independent-input-v1';assert not out.exists();out.mkdir();write(out/'style-applicability.json',dict(rawPmd=25,rawPmdExit=4,mainFindings=9,testFindings=16,applicableViolations=0,checkstyle=0,processingErrors=0,suppressionsAdded=False,judgments=judgments));write(out/'probe-interpretation.json',interpretation);files={}
for name,p in [('normal.json',normalp),('six-static.json',sbp),('style-raw.json',stylep),('pmd.xml',stylep.parent/'pmd.xml'),('checkstyle.xml',stylep.parent/'checkstyle.xml')]:shutil.copyfile(p,out/name);files[name]=sha(out/name)
for role,v in sb['reports'].items():name='spotbugs-'+role+'.xml';shutil.copyfile(v['path'],out/name);files[name]=sha(out/name)
for key in ['pmd','checkstyle']:
 for suffix in ['stdout','stderr','exit.safe.json','begin.safe.json']:
  name=key+'-'+suffix if suffix.endswith('.json') else key+'.'+suffix;shutil.copyfile(stylep.parent/name,out/name);files[name]=sha(out/name)
for n in ['style-applicability.json','probe-interpretation.json']:files[n]=sha(out/n)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain=normal['source'],normalManifestSha256=sha(normalp),sixStaticManifestSha256=sha(sbp),styleInputHashes=style['inputHashes'],rawPmd=25,mainPmd=9,testPmd=16,applicableViolations=0,checkstyle=0,sixStaticZero=True,bytecodeManifest=dict(path=str(bp.relative_to(r)),sha256=sha(bp)),probeManifest=dict(path=str(pm.relative_to(r)),sha256=sha(pm)),rawProbeHit=27,rawProbeTotal=29,productTestsExecuted=0,callerDynamicStatus='NOT_RUN_HOLD',whole451Accepted=False,files=files,driverSha256=sha(__file__))
write(out/'manifest.json',value);print(json.dumps(dict(actualExit=0,rawPmd=25,applicable=0,rawProbeHit=27,rawProbeTotal=29,manifestSha256=sha(out/'manifest.json'))))
