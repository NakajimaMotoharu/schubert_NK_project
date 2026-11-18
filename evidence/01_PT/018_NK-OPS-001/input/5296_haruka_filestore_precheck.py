"""One fresh pinned, noninteractive, read-only check of the approved haruka workspace."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys

PMO = Path('../PMO/hourly-monitor').resolve()
sys.path.insert(0, str(PMO / 'haruka-transition-20261114'))
from remote_access import config

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
WORK = '/home/mini/schubert-nk-pgpt/validation-work'
RUN = 'PG40160-p020-haruka-real-filestore-v1'
TOOL = '/opt/schubert-nk-test-tools'
COMMAND = r"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, subprocess
root=Path('/home/mini/schubert-nk-pgpt/validation-work')
run=root/'PG40160-p020-haruka-real-filestore-v1'
assert Path('/etc/hostname').read_text().strip()=='haruka'
assert root.resolve()==root
st=root.stat()
assert st.st_uid==os.getuid()==1000 and st.st_mode & 0o077==0 and os.access(root,os.W_OK|os.X_OK)
assert not os.path.lexists(run)
space=shutil.disk_usage(root).free
assert space>=21474836480
tool=Path('/opt/schubert-nk-test-tools')
names={'java':tool/'jdk-25.0.4/bin/java','javac':tool/'jdk-25.0.4/bin/javac',
       'maven':tool/'maven/bin/mvn'}
pins={}
for name,p in names.items():
    assert p.is_file() and os.access(p,os.R_OK|os.X_OK)
    outcome=subprocess.run([str(p),'--version'],capture_output=True,check=True,timeout=15)
    pins[name]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                    version=outcome.stdout.decode().splitlines()[0])
assert '25.0.4' in pins['java']['version'] and '3.9.12' in pins['maven']['version']
exact_owned=[]
for proc in Path('/proc').iterdir():
    if proc.name.isdecimal():
        try:
            if proc.stat().st_uid==os.getuid():
                cwd=Path(os.readlink(proc/'cwd'))
                if cwd.is_relative_to(root): exact_owned.append(int(proc.name))
        except OSError:
            continue
assert not exact_owned
print(json.dumps(dict(host='haruka',directOs=True,boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    ownerUid=os.getuid(),workspace=str(root),workspaceMode=oct(st.st_mode & 0o777),availableBytes=space,
    rootDevice=st.st_dev,runAbsent=True,activeJobsUnderWorkspace=exact_owned,tools=pins,
    terminalAtUTC=datetime.now(timezone.utc).isoformat())))
"""


def ssh_args():
    pinned = PMO / 'haruka_known_hosts'
    assert pinned.is_file()
    address = config('haruka')['addr']
    host_key = subprocess.run(['/usr/bin/ssh-keygen', '-F', address, '-f', str(pinned)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    assert host_key.returncode == 0
    return ['/usr/bin/ssh', '-F', '/dev/null', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'UserKnownHostsFile=' + str(pinned), '-o', 'GlobalKnownHostsFile=/dev/null',
            '-o', 'UpdateHostKeys=no', '-o', 'ForwardAgent=no', '-o', 'ClearAllForwardings=yes',
            '-o', 'ControlMaster=no', '-o', 'ConnectTimeout=12', 'mini@' + address]


def main():
    start = json.loads(next(D.glob('634_P020*')).read_bytes())['values']
    pmofile = PMO / 'haruka-iori-validation-20261119.json'
    assert hashlib.sha256(pmofile.read_bytes()).hexdigest() == start['approvedEnvironmentRecordSha256']
    assert json.loads(pmofile.read_bytes())['haruka']['path'] == WORK and start['run'] == RUN
    previous = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert previous == start['source']
    completed = subprocess.run([*ssh_args(), 'python3 -'], input=COMMAND.encode(), capture_output=True,
                               check=False, timeout=50)
    received = json.loads(completed.stdout) if completed.returncode == 0 else None
    if received is not None:
        assert received['runAbsent'] and received['activeJobsUnderWorkspace'] == []
        assert received['availableBytes'] >= 21474836480
    value = dict(actualExit=completed.returncode, source=previous, strictPinnedKey=True,
                 knownHostsSha256=hashlib.sha256((PMO / 'haruka_known_hosts').read_bytes()).hexdigest(),
                 host='haruka', observed=received, authRawOutputSaved=False, applicationStarted=False,
                 allocatedRun=False, actualBackendActions=0,
                 terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = E / 'PG40158-haruka-filestore-readonly-precheck-v1'
    folder.mkdir()
    out = folder / 'manifest.json'
    out.write_text(json.dumps(value, indent=2) + '\n')
    print(dict(actualExit=value['actualExit'], proof=str(out), sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
               workspaceEligible=received is not None, availableBytes=received['availableBytes'] if received else None))
    raise SystemExit(completed.returncode)


if __name__ == '__main__':
    main()
