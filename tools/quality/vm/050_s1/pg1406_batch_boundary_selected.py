"""Bounded selected PT with isolated tmpfs DB, old reports kept and Main byte equality."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

T=Path(__file__).resolve().parents[4]
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4')
CHANGED=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupProfileTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchRunRepositoryTest.java']
SUITES={'dev.codex.schubert.nk.batch.repository.BatchRunRepositoryTest':20,'dev.codex.schubert.nk.batch.backup.BackupProfileTest':4}

def require(value):
    if not value:raise ValueError('bounded fixed batch boundary qualification refused')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def class_hashes(jar):
    with zipfile.ZipFile(jar)as z:
        return {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}

def main():
    os.umask(0o077)
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=T))
    changed=subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T,text=True).splitlines();require(changed==CHANGED)
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:argv=(p/'cmdline').read_bytes();cwd=(p/'cwd').readlink()
        except(FileNotFoundError,PermissionError,ProcessLookupError):continue
        require(not(b'org.codehaus.plexus.classworlds.launcher.Launcher'in argv and cwd==T))
    disk=os.statvfs(W);memory=os.statvfs('/dev/shm')
    require(disk.f_bavail*disk.f_frsize>=805306368 and memory.f_bavail*memory.f_frsize>=536870912)
    run=W/'pg1406-batch-boundary-selected-v1';run.mkdir(mode=0o700)
    prior=run/'preexisting';prior.mkdir(mode=0o700)
    target=T/'src/schubert-nk-batch/target'
    for name in ('jacoco.exec','spotbugsXml.xml'):
        if (target/name).exists():shutil.copyfile(target/name,prior/name)
    for name in SUITES:
        p=target/'surefire-reports'/('TEST-'+name+'.xml')
        if p.exists():shutil.copyfile(p,prior/p.name)
    tmp=Path(tempfile.mkdtemp(prefix='pg1406-isolated-db-',dir='/dev/shm'));tmp.chmod(0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    paths=subprocess.check_output(['git','ls-files','src','pom.xml'],cwd=T,text=True).splitlines();hashes={n:sha(T/n)for n in paths}
    execfile=run/'selected.exec'
    args=['./mvnw','-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository','-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch','-Dtest=BatchRunRepositoryTest,BackupProfileTest','-Dsurefire.failIfNoSpecifiedTests=false','-DfailIfNoTests=false','-Djacoco.destFile='+str(execfile),'spotless:check','test-compile','test','spotbugs:check','jacoco:report','jar:jar']
    env=dict(os.environ,JAVA_HOME=str(J),PATH=str(J/'bin')+os.pathsep+os.environ['PATH'],JAVA_TOOL_OPTIONS='-Djava.io.tmpdir='+str(tmp),MAVEN_OPTS='-Xmx768m')
    start=datetime.datetime.now(datetime.timezone.utc)
    with(run/'build.private.log').open('xb')as f:
        r=subprocess.run(args,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT);f.flush();os.fsync(f.fileno())
    counts={};missing=[]
    for suite,count in SUITES.items():
        p=target/'surefire-reports'/('TEST-'+suite+'.xml')
        if not p.exists():missing.append(suite);continue
        x=ET.parse(p).getroot();counts[suite]={k:int(x.attrib[k])for k in ('tests','failures','errors','skipped')}
        shutil.copyfile(p,run/p.name)
    static=None;byte_same=None;code=r.returncode
    if code==0:
        require(not missing and all(counts[n]=={'tests':c,'failures':0,'errors':0,'skipped':0}for n,c in SUITES.items()))
        require(execfile.exists()and execfile.stat().st_size>0)
        static=len(ET.parse(target/'spotbugsXml.xml').getroot().findall('BugInstance'));require(static==0)
        old=W/'pg1279-held-channel-six-host-v1/batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar';new=target/'schubert-nk-batch-0.1.0-SNAPSHOT.jar'
        byte_same=class_hashes(old)==class_hashes(new);require(byte_same)
        shutil.copyfile(new,run/new.name);shutil.copyfile(target/'spotbugsXml.xml',run/'spotbugsXml.xml')
    require(head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()and hashes=={n:sha(T/n)for n in paths})
    record={'run':'PG1406-batch-boundary-selected-v1','actualExit':code,'operatorSource':head,'productionMainSource':SOURCE,'changedTests':CHANGED,'sourceHashes':{n:hashes[n]for n in CHANGED},'command':args,'environment':{'JDK':'25.0.4','temporaryFixtureRoot':str(tmp),'PG':'18.6','databaseOnTmpfs':True,'mavenHeapMiB':768},'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'testCounts':counts,'requiredSelectedTestCount':24,'missingSuites':missing,'dependencySelectedNoTestsNotCountedPassed':True,'staticIssues':static,'allBatchMainClassBytesEqual1279':byte_same,'logSha256':sha(run/'build.private.log'),'execSha256':sha(execfile)if execfile.exists()else None,'previousEvidenceHashes':{p.name:sha(p)for p in prior.iterdir()},'formalAccepted':False,'coverage100':False,'vmActions0':True,'deployedMainUnchanged':True,'oldEvidenceDeleted0':True}
    with(run/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with(run/'exit').open('x')as f:f.write(str(code)+'\n')
    print(json.dumps({k:record[k]for k in ('actualExit','testCounts','staticIssues','allBatchMainClassBytesEqual1279','formalAccepted','vmActions0')}));return code

if __name__=='__main__':raise SystemExit(main())
