"""Preserve actual failed fresh PT before any target rebuild; never accepts its coverage."""
import datetime
import json
import os
import shutil
from pathlib import Path
from pg831_manager_collect import sha, MODULES

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')

def main():
    os.umask(0o077)
    run=W/'pg1011-stream-six-host-v1'
    assert (run/'exit').read_text().strip()=='1'
    assert (run/'source').read_text().strip()=='94495eb525787969e8174cb8d19f30b70c0e1c61'
    saved=W/'pg1012-stream-failed-preservation-v1';saved.mkdir(mode=0o700)
    files={}
    for m in MODULES:
        target=T/'src'/('schubert-nk-'+m)/'target'
        dest=saved/m;dest.mkdir(mode=0o700)
        for p in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            shutil.copy2(p,dest/p.name);files[m+'/'+p.name]=sha(p)
        for name in ('jacoco.exec','spotbugsXml.xml'):
            p=target/name
            if p.exists():shutil.copy2(p,dest/name);files[m+'/'+name]=sha(p)
    record={'run':saved.name,'failedSource':'94495eb525787969e8174cb8d19f30b70c0e1c61',
      'actualExit':1,'logSha256':sha(run/'build.private.log'),'files':files,
      'preservedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'global100':False,'formalAccepted':False,'acceptedPT':0,'BUG':'BUG-1007'}
    with(saved/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True)
    print(json.dumps({'actualExit':1,'acceptedPT':0,'manifestSha256':sha(saved/'manifest.safe.json')}))

if __name__=='__main__':main()
