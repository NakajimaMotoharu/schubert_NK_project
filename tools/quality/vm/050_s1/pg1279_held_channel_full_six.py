"""One SSC261-triggered new-source whole-six; preserve target evidence before clean."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from pg1018_stream_full_v2 import source as previous

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
T=Path('/home/mini/codex/project1/work/pgpt-foundation')


def source():
    s=previous()
    if s.count('pg1018-stream-six-host-v2')!=1:raise ValueError('fixed current whole6 slot substitution required')
    return s.replace('pg1018-stream-six-host-v2','pg1279-held-channel-six-host-v1').replace('PG1018_FULL','PG1279_FULL')


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain'],cwd=T):raise ValueError('clean fixed source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    save=W/'pg1279-previous-six-targets-v1'
    if os.path.lexists(save)or os.path.lexists(W/'pg1279-held-channel-six-host-v1'):raise ValueError('new-only full and preservation slots required')
    if os.statvfs(W).f_bavail*os.statvfs(W).f_frsize<1073741824:raise ValueError('full-regression preservation and close cushion required')
    save.mkdir(mode=0o700);hashes={}
    for module in ['protocol','storage','bootstrap','api','web','batch']:
        root=T/('src/schubert-nk-'+module+'/target');out=save/module;out.mkdir(mode=0o700)
        for name in ['surefire-reports','site/jacoco','jacoco.exec','spotbugsXml.xml','schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar']:
            p=root/name
            if p.is_dir():shutil.copytree(p,out/name)
            elif p.is_file():shutil.copy2(p,out/name)
        for p in out.rglob('*'):
            if p.is_file():hashes[str(p.relative_to(save))]=hashlib.sha256(p.read_bytes()).hexdigest()
    with(save/'manifest.safe.json').open('x')as f:json.dump({'sourceBefore':head,'preservedEvidenceHashes':hashes,'wholeAcceptance':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    return subprocess.run(['/bin/bash','-s','--',head],input=source().encode(),cwd=T).returncode


if __name__=='__main__':raise SystemExit(main())
