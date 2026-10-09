"""One owned-current readonly stack diagnostic, raw private, no starts/stops."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import pathlib,subprocess
def owner():
 v=dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,InvocationID,Job,ExecMainStartTimestampMonotonic'],text=True).splitlines())
 assert v=={'MainPID':'2468821','InvocationID':'2aff8ecf3b7d4d15b24a8af0f73a8745','Job':'132812','ExecMainStartTimestampMonotonic':'127549297774'}
 assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
 s=pathlib.Path('/proc/2468821/stat').read_text();assert int(s[s.rindex(')')+2:].split()[19])==12754929
 assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG715')
 return v
before=owner()
r=subprocess.run(['/opt/jdk-25.0.4/bin/jcmd','2468821','Thread.print','-l'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
assert r.returncode==0 and owner()==before
import sys
sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr)
'''


def main():
    os.umask(0o077)
    log=W/'pg734-owned-parent-stack-v1.private.log'
    err=W/'pg734-owned-parent-stack-v1.private.stderr'
    assert not log.exists() and not err.exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('xb')as out,err.open('xb')as stderr:
        r=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=out,stderr=stderr,timeout=45)
        for f in (out,stderr):f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'atUTC':at,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),
          'privateStderrSha256':hashlib.sha256(err.read_bytes()).hexdigest(),
          'rawExported':False,'startsStops0':True,'businessMutations0':True,
          'frames':re.findall(r'^\s+at (dev\.codex\.schubert\.nk\.[A-Za-z0-9_.$]+\([^\r\n]*\))',log.read_text(errors='replace'),re.M)[:24],
          'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip()}
    with (W/'pg734-owned-parent-stack-v1.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.write('\n')
    print(json.dumps(safe));raise SystemExit(r.returncode)


if __name__=='__main__':main()
