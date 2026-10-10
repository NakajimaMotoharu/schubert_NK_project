"""Frozen test-only real shutdown PT; preserve existing target evidence first."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

T=Path('/home/mini/codex/project1/work/pgpt-foundation')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
JAVA=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4')
SOURCE='d5b00104280028d9ea81b44c1d1c805f3c2861ed'
TEST='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHoldTest.java'


def require(value):
    if not value:raise ValueError('fixed current stop hold selected PT refused')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=T))
    changes=subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T,text=True).splitlines()
    require(changes==[TEST])
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    for p in Path('/proc').iterdir():
        if p.name.isdigit():
            try:argv=(p/'cmdline').read_bytes()
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            require(b'org.codehaus.plexus.classworlds.launcher.Launcher'not in argv or b'pg1272_stop_hold_selected.py'in argv)
    run=W/'pg1272-stop-hold-selected-v1';require(not os.path.lexists(run))
    require(os.statvfs(W).f_bavail*os.statvfs(W).f_frsize>=805306368)
    run.mkdir(mode=0o700);preserved=run/'previous-target-evidence';preserved.mkdir(mode=0o700)
    target=T/'src/schubert-nk-bootstrap/target'
    prior={}
    for name in ['jacoco.exec','site/jacoco','surefire-reports','spotbugsXml.xml']:
        p=target/name
        if p.is_dir():shutil.copytree(p,preserved/name)
        elif p.is_file():shutil.copy2(p,preserved/name)
    for p in preserved.rglob('*'):
        if p.is_file():prior[str(p.relative_to(preserved))]=sha(p)
    execfile=run/'selected.exec';require(not execfile.exists())
    args=['./mvnw','-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository','-pl','src/schubert-nk-bootstrap','-Dtest=FixedNativeCoverageStopHoldTest','-Djacoco.destFile='+str(execfile),'spotless:check','test','spotbugs:check','jacoco:report']
    env=dict(os.environ,JAVA_HOME=str(JAVA),PATH=str(JAVA/'bin')+os.pathsep+os.environ['PATH'])
    start=datetime.datetime.now(datetime.timezone.utc)
    with(run/'selected.private.log').open('xb')as f:
        result=subprocess.run(args,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT);f.flush();os.fsync(f.fileno())
    finish=datetime.datetime.now(datetime.timezone.utc)
    require(head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()and not subprocess.check_output(['git','status','--porcelain'],cwd=T))
    xml=target/'surefire-reports/TEST-dev.codex.schubert.nk.bootstrap.FixedNativeCoverageStopHoldTest.xml'
    counts=None
    if xml.exists():
        root=ET.parse(xml).getroot();counts={k:int(root.attrib[k])for k in ['tests','failures','errors','skipped']}
    static=None;p=target/'spotbugsXml.xml'
    if result.returncode==0:
        require(counts=={'tests':6,'failures':0,'errors':0,'skipped':0}and execfile.exists()and execfile.stat().st_size>0)
        static=len(ET.parse(p).getroot().findall('BugInstance'));require(static==0)
    safe={'actualExit':result.returncode,'operatorSource':head,'productionSource':SOURCE,'changedTestOnly':[TEST],'testSha256':sha(T/TEST),'command':args,'startedUTC':start.isoformat(),'completedUTC':finish.isoformat(),'elapsedSeconds':(finish-start).total_seconds(),'testCounts':counts,'staticIssues':static,'previousEvidenceHashes':prior,'logSha256':sha(run/'selected.private.log'),'execSha256':sha(execfile)if execfile.exists()else None,'xmlSha256':sha(xml)if xml.exists()else None,'formalAccepted':False,'nativeAppEvidence':False,'ordinaryVmOperations0':True,'childExpectedExit':143}
    with(run/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:safe[k]for k in ['actualExit','elapsedSeconds','testCounts','staticIssues','execSha256','logSha256','ordinaryVmOperations0','formalAccepted']}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
