"""New-only official promtool installation in owned host toolchain; never a server or VM tool."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import tarfile
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
TC=Path('/home/mini/codex/project1/work/toolchain')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
TOOL=TC/'promtool-3.13.5-linux-amd64'
SLOT=W/'pg8162-promtool-prepare-v1'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8162-promtool-prepare-v1'
URL='https://github.com/prometheus/prometheus/releases/download/v3.13.5/prometheus-3.13.5.linux-amd64.tar.gz'
ARCHIVE_SHA='0388822ace519c5a3a8ef556a541ce1b536e21d872f82deded465bd27a5a0699'
PREFIX='prometheus-3.13.5.linux-amd64/'
SELECTED=('promtool','LICENSE','NOTICE')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def write(path,value):
    with path.open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def main():
    invocation=capture(Path(__file__))
    if TOOL.exists() or SLOT.exists() or OUT.exists():
        raise ValueError('new-only owned tool installation; existing artifacts require read-only recovery')
    if platform.system()!='Linux' or platform.machine()!='x86_64':
        raise ValueError('exact declared host platform only')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    os.umask(0o077)
    SLOT.mkdir(mode=0o700)
    TOOL.mkdir(mode=0o700)
    command=['/usr/bin/curl','--fail','--location','--silent','--show-error','--proto','=https',
             '--tlsv1.2','--max-time','240','--max-filesize','167772160',URL]
    begin=dict(source=source,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               pid=os.getpid(),command=command,archiveExpectedSha256=ARCHIVE_SHA,
               invocation=invocation,toolTarget=str(TOOL),publicArtifactDownloadOnly=True,
               actualTargetVmOrServiceOperations=0,environmentSerialized=False)
    write(SLOT/'begin.safe.json',begin)
    archive=TOOL/'official-distribution.tar.gz'
    with archive.open('xb') as f:
        child=subprocess.Popen(command,cwd=SLOT,stdout=f,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,close_fds=True)
        write(SLOT/'download-process.safe.json',dict(pid=child.pid,ownerPid=os.getpid(),command=command))
        _,stderr=child.communicate(timeout=250)
        f.flush()
        os.fsync(f.fileno())
    write(SLOT/'download-terminal.safe.json',dict(actualExit=child.returncode,
        endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        stderr=stderr.decode('utf-8','replace'),bytes=archive.stat().st_size,archiveSha256=sha(archive)))
    if child.returncode!=0:
        raise ValueError('official public download failed; preserved original terminal, no alternate route')
    if sha(archive)!=ARCHIVE_SHA:
        raise ValueError('official published archive checksum mismatch; no extraction or execution')
    extracted={}
    with tarfile.open(archive,'r:gz') as tf:
        members=tf.getmembers()
        if len(members)>100 or len({m.name for m in members})!=len(members):
            raise ValueError('bounded unique distribution entries required')
        for name in SELECTED:
            matches=[m for m in members if m.name==PREFIX+name]
            if len(matches)!=1 or not matches[0].isfile() or matches[0].linkname or not 0<matches[0].size<300*1024*1024:
                raise ValueError('only exact regular public tool/license members')
            src=tf.extractfile(matches[0])
            if src is None:
                raise ValueError('selected source member unavailable')
            target=TOOL/name
            with src,target.open('xb') as out:
                shutil.copyfileobj(src,out,1024*1024)
                out.flush()
                os.fsync(out.fileno())
            target.chmod(0o700 if name=='promtool' else 0o600)
            extracted[name]=dict(path=str(target),sha256=sha(target),bytes=target.stat().st_size,
                                 mode=oct(stat.S_IMODE(target.stat().st_mode)),regular=True)
    if (TOOL/'prometheus').exists():
        raise ValueError('daemon extraction forbidden for this tool-only preparation')
    version_command=[str(TOOL/'promtool'),'--version']
    version=subprocess.run(version_command,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},
                           stdin=subprocess.DEVNULL,text=True,capture_output=True,timeout=15,close_fds=True,check=False)
    if version.returncode!=0 or 'version 3.13.5' not in version.stdout+version.stderr:
        raise ValueError('actual verified binary version required')
    verify(invocation)
    value=dict(actualExit=0,source=source,invocation=invocation,begin=begin,
        endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        platform=platform.platform(),downloadCommand=command,downloadExit=child.returncode,
        archive=dict(path=str(archive),sha256=sha(archive),expectedSha256=ARCHIVE_SHA,bytes=archive.stat().st_size,
                     url=URL,checksumSource='https://prometheus.io/download/',signatureVerified=False),
        selectedMembers=extracted,unselectedMembersExtracted=0,
        version=dict(command=version_command,actualExit=version.returncode,stdout=version.stdout,stderr=version.stderr),
        publicArtifactDownloads=1,targetNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,
        actualDaemonActions=0,actualCredentialReads=0,toolOnly=True,productTestsExecuted=0,
        formalUpdated=False,newAccepted=0,effortPercent=None)
    write(SLOT/'manifest.safe.json',value)
    OUT.mkdir(mode=0o700)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,version='3.13.5',archiveSha256=ARCHIVE_SHA,
                         binarySha256=extracted['promtool']['sha256'],manifestSha256=sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
