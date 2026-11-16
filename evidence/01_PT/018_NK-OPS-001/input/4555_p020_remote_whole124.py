"""One bounded ordinary SDK/JUnit run in a new dedicated scratch, no service/DB/native entry."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import tarfile

ROOT=Path.cwd(); os.umask(0o077)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(path,value):
    with path.open('x') as out:
        json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
def inventory(root):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
def step(name,cmd,cwd,env,timeout):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (ROOT/(name+'.log')).open('xb') as log:
        child=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
        save(ROOT/(name+'.process.json'),dict(pid=child.pid,command=cmd,cwd=str(cwd),startUTC=start))
        timed=False
        try: code=child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed=True;child.terminate()
            try:code=child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();code=child.wait()
        log.flush();os.fsync(log.fileno())
    v=dict(actualExit=code,timedOut=timed,command=cmd,cwd=str(cwd),startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),logSha256=sha(ROOT/(name+'.log')))
    save(ROOT/(name+'.exit.json'),v);return v

def main():
    assert ROOT.name=='wbs66-p020-20261117-pg37012' and ROOT.stat().st_uid==os.getuid()!=0
    assert not (ROOT/'begin.json').exists() and not (ROOT/'snapshot').exists()
    cfg=json.loads((ROOT/'package.json').read_text());assert sha(ROOT/'snapshot.tar')==cfg['archiveSha256']
    for name,h in cfg['sdkHashes'].items():assert sha(ROOT/'sdk'/name)==h
    assert os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize>20*1024**3
    assert os.statvfs('/tmp').f_bavail*os.statvfs('/tmp').f_frsize<20*1024**3
    snapshot=ROOT/'snapshot';snapshot.mkdir()
    with tarfile.open(ROOT/'snapshot.tar') as t:
        assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in t.getmembers())
        t.extractall(snapshot,filter='data')
    source=inventory(snapshot);assert source==cfg['sourceHashes']
    baseline=inventory(snapshot/'program/characterization/baseline/current')
    save(ROOT/'begin.json',dict(config=cfg,sourceHashes=source,baselineHashes=baseline,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid(),uid=os.getuid(),host=os.uname().nodename,realServicesVmDbNativeActions=0))
    classes=ROOT/'mainclasses';tests=ROOT/'testclasses';classes.mkdir();tests.mkdir()
    jdk=Path('/opt/schubert-nk-test-tools/jdk-25.0.4/bin');sdk=ROOT/'sdk';cp=':'.join(str(sdk/n) for n in cfg['compileSdk'])
    env=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),LANG='C.UTF-8')
    mainfiles=sorted(snapshot.glob('program/characterization/src/main/java/**/*.java'));assert len(mainfiles)==5
    stages={};stages['maincompile']=step('maincompile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(classes),*[str(p) for p in mainfiles]],ROOT,env,120)
    if stages['maincompile']['actualExit']==0:
        testroot=snapshot/'program/characterization/tests/java';selected=[testroot/'dev/codex/schubert/characterization'/(n+'.java') for n in cfg['selectedSuites']]
        stages['testcompile']=step('testcompile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',str(classes)+':'+cp,'-sourcepath',str(testroot),'-d',str(tests),*[str(p) for p in selected]],ROOT,env,120)
    if stages.get('testcompile',{}).get('actualExit')==0:
        temp=Path('/tmp')/ROOT.name;assert not temp.exists();temp.mkdir(mode=0o700)
        xml=ROOT/'xml';xml.mkdir();agent=sdk/'org.jacoco.agent-0.8.15-runtime.jar'
        command=[str(jdk/'java'),'-Xmx1g','-Djava.awt.headless=true','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-Dchr.unitProjectRoot='+str(snapshot),'-Djava.io.tmpdir='+str(temp),'-Xlog:class+init=info:file='+str(ROOT/'class-init.log'),'-javaagent:'+str(agent)+'=destfile='+str(ROOT/'jacoco.exec')+',sessionid=PG37012-COMMON124,append=false','-jar',str(sdk/'junit-platform-console-standalone-1.13.4.jar'),'execute','--disable-banner','--details=summary','--fail-if-no-tests','--class-path',':'.join([str(classes),str(tests),str(snapshot/'program/characterization/tests/resources'),cp]),'--reports-dir',str(xml),*[x for n in cfg['selectedSuites'] for x in ['--select-class','dev.codex.schubert.characterization.'+n]],'--config=junit.jupiter.execution.parallel.enabled=false']
        stages['unit']=step('unit',command,ROOT,env,180)
        if (ROOT/'jacoco.exec').exists():
            stages['coverage']=step('coverage',[str(jdk/'java'),'-jar',str(sdk/'org.jacoco.cli-0.8.15-nodeps.jar'),'report',str(ROOT/'jacoco.exec'),'--classfiles',str(classes),'--xml',str(ROOT/'coverage.xml')],ROOT,env,120)
            stages['execinfo']=step('execinfo',[str(jdk/'java'),'-jar',str(sdk/'org.jacoco.cli-0.8.15-nodeps.jar'),'execinfo',str(ROOT/'jacoco.exec')],ROOT,env,120)
    unchanged=all(sha(snapshot/p)==h for p,h in source.items())
    value=dict(actualExit=0 if all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and 'unit' in stages else 1,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=cfg['source'],sourceCore=cfg['sourceCore'],stages=stages,sourceInputsUnchanged=unchanged,baselineUnchanged=inventory(snapshot/'program/characterization/baseline/current')==baseline,mainClasses=inventory(classes),testClasses=inventory(tests),expectedInvocations=124,files={p.name:sha(p) for p in sorted(ROOT.iterdir()) if p.is_file() and p.suffix in ['.json','.log','.xml','.exec'] and p.name!='package.json'},xmlHashes=inventory(ROOT/'xml') if (ROOT/'xml').exists() else {},formalUpdated=False,newAcceptance=0)
    save(ROOT/'terminal.json',value)
    with tarfile.open(ROOT/'result.tar','x') as tar:
        for path in sorted(ROOT.iterdir()):
            if path.name in ['snapshot','sdk','snapshot.tar','result.tar']:continue
            tar.add(path,arcname=path.name)
    print(json.dumps(dict(actualExit=value['actualExit'],terminalSha256=sha(ROOT/'terminal.json'),resultSha256=sha(ROOT/'result.tar'),resultBytes=(ROOT/'result.tar').stat().st_size)),flush=True)
    raise SystemExit(value['actualExit'])
if __name__=='__main__':main()
