"""Run only new whole value5 against exact unchanged qualified Main10, preserving one new exec."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

r=Path.cwd();os.umask(0o077);b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379';slot=w/'pg37022-common-values5-unit-v1';assert not slot.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert source.startswith('6cc5994cb3')
assert subprocess.run(['git','diff','--exit-code',source,'--','program/characterization'],stdout=subprocess.DEVNULL).returncode==0
prior=load(b/'evidence/PG37016-p020-whole124-independent-v1/manifest.json');classes=w/'pg37012-p020-remote124-recovered/mainclasses';cfg=load(w/'pg37008-p020-public-package-v1/package.json');sdk=w/'pg37008-p020-public-package-v1/sdk'
assert all(sha(classes/name)==h for name,h in prior['classSha256'].items())
assert all(sha(r/path)==h for path,h in prior['sourceTestPins'].items() if '/src/main/java/' in path)
assert all(sha(sdk/name)==h for name,h in cfg['sdkHashes'].items())
p=r/'program/characterization/tests/java/dev/codex/schubert/characterization/CommonValueContractTest.java';spec=b/'4466_P020生成値契約5仕様.md'
slot.mkdir();(slot/'testclasses').mkdir();(slot/'xml').mkdir()
def save(path,value):path.open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def step(name,cmd,cwd):
 save(slot/(name+'.begin.json'),dict(command=cmd,cwd=str(cwd),source=source,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 with (slot/(name+'.stdout')).open('xb') as stdout,(slot/(name+'.stderr')).open('xb') as stderr:
  child=subprocess.Popen(cmd,cwd=cwd,stdout=stdout,stderr=stderr,env=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',LANG='C.UTF-8'))
  save(slot/(name+'.pid.json'),dict(pid=child.pid,source=source,command=cmd))
  timed=False
  try:code=child.wait(timeout=120)
  except subprocess.TimeoutExpired:timed=True;child.kill();code=child.wait()
 v=dict(actualExit=code,timedOut=timed,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdoutSha256=sha(slot/(name+'.stdout')),stderrSha256=sha(slot/(name+'.stderr')));save(slot/(name+'.exit.json'),v);return v
jdk=tc/'jdk-25.0.4/bin';cp=':'.join([str(classes),*[str(sdk/n) for n in cfg['compileSdk']]])
begin=dict(source=source,sourceCore=prior['sourceCore'],run='PG37022-VALUES5',testPath=str(p.relative_to(r)),testSha256=sha(p),specPath=str(spec.relative_to(r)),specSha256=sha(spec),physicalClassHashes=prior['classSha256'],sdkHashes=cfg['sdkHashes'],expected=5,selectedSuites=['dev.codex.schubert.characterization.CommonValueContractTest'],startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old124Replayed=False,oldExecUnion=False,privateReflection=False,productNativeBrowserDbRootActions=0)
save(slot/'begin.json',begin)
stages={}
stages['format']=step('format',[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(p)],r)
stages['checkstyle']=step('checkstyle',[str(jdk/'java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(slot/'checkstyle.xml'),str(p)],r)
stages['compile']=step('compile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(slot/'testclasses'),str(p)],r)
if all(v['actualExit']==0 for v in stages.values()):
 cmd=[str(jdk/'java'),'-Xlog:class+init=info:file='+str(slot/'class-init.log'),'-javaagent:'+str(sdk/'org.jacoco.agent-0.8.15-runtime.jar')+'=destfile='+str(slot/'jacoco.exec')+',sessionid=PG37022-VALUES5,append=false','-jar',str(sdk/'junit-platform-console-standalone-1.13.4.jar'),'execute','--disable-banner','--details=summary','--fail-if-no-tests','--class-path',str(slot/'testclasses')+':'+cp,'--reports-dir',str(slot/'xml'),'--select-class','dev.codex.schubert.characterization.CommonValueContractTest','--config=junit.jupiter.execution.parallel.enabled=false']
 stages['unit']=step('unit',cmd,slot)
value=dict(actualExit=0 if all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and 'unit' in stages else 1,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=source,sourceCore=prior['sourceCore'],run=begin['run'],stages=stages,testUnchanged=sha(p)==begin['testSha256'],mainPhysicalUnchanged=all(sha(classes/n)==h for n,h in prior['classSha256'].items()),classHashes={str(p.relative_to(slot/'testclasses')):sha(p) for p in (slot/'testclasses').rglob('*.class')},xmlHashes={p.name:sha(p) for p in (slot/'xml').glob('*.xml')},execSha256=sha(slot/'jacoco.exec') if (slot/'jacoco.exec').exists() else None)
save(slot/'terminal.json',value);print(json.dumps(dict(actualExit=value['actualExit'],stages={k:v['actualExit'] for k,v in stages.items()},source=source,run=begin['run'])));raise SystemExit(value['actualExit'])
