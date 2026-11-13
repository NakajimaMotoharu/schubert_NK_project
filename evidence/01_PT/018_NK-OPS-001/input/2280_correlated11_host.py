"""New-only fixed-source ordinary Characterization tool tests; no real capture or authority operation.

Full five Main coverage is reported, never accepted as100 with GateCliTest capacity HOLD.
No existing runner defaults, synthetic free-space, method extraction or quality skip flags.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import signal
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET

R=Path(__file__).resolve().parents[4]
TC=R.parent/'toolchain'
W=R.parent/'pgpt-runs/PG379'
B=R/'evidence/01_PT/018_NK-OPS-001/evidence'
SELECTED=('CorrelatedLogEvidenceValidatorTest',)
MAIN=('ArtifactComparator','GateCli','GateContractValidator','TargetAdapter','CorrelatedLogEvidenceValidator')
EXPECTED={'CorrelatedLogEvidenceValidatorTest':11}
ENV=dict(PATH=str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin', JAVA_HOME=str(TC/'jdk-25.0.4'), MAVEN_USER_HOME=str(TC/'m2'), MAVEN_SKIP_RC='true', LANG='C.UTF-8', MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,v):
    with p.open('x') as f:
        json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
def inventory(p): return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()}

def run(source):
    assert len(source)==40 and all(c in '0123456789abcdef' for c in source)
    assert subprocess.check_output(['git','diff','--name-only',source,'--','program/characterization','pom.xml','.mvn','mvnw','tools/quality/static'],cwd=R)==b''
    slot=W/'pg29286-correlated-whole11-normal-v1';public=B/'PG29286-correlated-whole11-normal-v1'
    assert not slot.exists() and not public.exists(),'observe existing begin/terminal; no restart'
    # Inventory only immutable public baseline. Actual private resources are never enumerated.
    baseline=R/'program/characterization/baseline/current';before=inventory(baseline);assert len(before)==27
    os.umask(0o077);slot.mkdir();public.mkdir()
    paths=['pom.xml','.mvn','mvnw','program/characterization',*['src/schubert-nk-'+n+'/pom.xml' for n in ('protocol','storage','bootstrap','api','web','batch')]]
    archive=slot/'source.tar'
    with archive.open('xb') as f: subprocess.run(['git','archive','--format=tar',source,*paths],cwd=R,stdout=f,check=True)
    snap=slot/'snapshot';snap.mkdir()
    with tarfile.open(archive) as t:
        for e in t.getmembers():
            p=Path(e.name);assert not p.is_absolute() and '..' not in p.parts and (e.isfile() or e.isdir())
        t.extractall(snap,filter='data')
    assert inventory(snap/'program/characterization/baseline/current')==before
    inputs=inventory(snap)
    format_files=['src/main/java/dev/codex/schubert/characterization/'+n+'.java' for n in MAIN]+['tests/java/dev/codex/schubert/characterization/'+n+'.java' for n in SELECTED]
    command=[str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-pl','program/characterization','-Dtest='+','.join(SELECTED),'-DspotlessFiles='+','.join(format_files),'test','org.jacoco:jacoco-maven-plugin:0.8.15:report']
    begin=dict(source=source,operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),startUTC=now(),command=command,cwd=str(snap),archiveSha256=sha(archive),inputHashes=inputs,originalBaselineHashes=before,selectedWholeClasses=list(SELECTED),expectedTests=EXPECTED,expectedInvocations=11,heldWholeClasses={'GateCliTest':'12; actual20GiB precondition unavailable'},allMainSources=list(MAIN),coverageExclusions=[],qualitySkips=[],fullBundleVerify='HOLD_NOT_EXECUTED_NOT_ACCEPTED',runnerSha256=sha(Path(__file__)),actualVmDatabaseNetworkNativeMasterCredentialActions=0)
    write(slot/'begin.safe.json',begin);write(public/'begin.json',begin)
    with (slot/'maven.log').open('xb') as log:
        child=subprocess.Popen(command,cwd=snap,env=ENV,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
        write(slot/'process.safe.json',dict(pid=child.pid,ownerPid=os.getpid(),startUTC=now(),source=source,command=command,cwd=str(snap)))
        timeout=False
        try: code=child.wait(timeout=480)
        except subprocess.TimeoutExpired:
            timeout=True;os.killpg(child.pid,signal.SIGTERM)
            try: code=child.wait(timeout=15)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait(timeout=15)
        log.flush();os.fsync(log.fileno())
    terminal=dict(source=source,actualExitCode=code,timedOut=timeout,endUTC=now(),logSha256=sha(slot/'maven.log'),beginSha256=sha(slot/'begin.safe.json'))
    write(slot/'exit.safe.json',terminal);write(public/'exit.json',terminal)
    unchanged=inventory(baseline)==before and all(sha(snap/p)==v for p,v in inputs.items())
    write(public/'manifest.json',dict(**terminal,status='RAW_TERMINAL_INDEPENDENT_POST_PENDING',sourceInputsUnchanged=unchanged,fullBundleAccepted=False,formalAcceptanceAdded=0,effortCompletionRate=None))
    print(json.dumps(dict(source=source,actualExitCode=code,timedOut=timeout,sourceInputsUnchanged=unchanged,post='PENDING')),flush=True)
    assert unchanged
    return code

if __name__=='__main__':sys.exit(run(sys.argv[1]))
