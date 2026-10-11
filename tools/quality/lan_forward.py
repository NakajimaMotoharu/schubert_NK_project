"""Owned mini-only local forwarding; VM access private key stays on this host."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import pexpect
from lan_server import HOST, pinned_key, credentials, ssh_options

OUT=Path('/home/mini/codex/project1/work/pgpt-vm/private/pg1436-lan-forward-v1')


def save(name, value):
    with (OUT/name).open('x') as f:
        json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['ss','-H','-lnt','( sport = :22222 )'])
    key=pinned_key()
    OUT.mkdir(mode=0o700)
    known=OUT/'known_hosts.public'
    known.write_text(key+'\n');os.chmod(known,0o600)
    args=['-N','-T',*ssh_options(known),'-o','ExitOnForwardFailure=yes',
          '-L','127.0.0.1:22222:127.0.0.1:22222',f'mini@{HOST}']
    child=pexpect.spawn('ssh',args,encoding='utf-8',timeout=20,echo=False)
    stopped=False
    def stop(signum, frame):
        nonlocal stopped
        stopped=True
    signal.signal(signal.SIGTERM,stop)
    signal.signal(signal.SIGINT,stop)
    try:
        child.expect(r'(?i)password:');child.sendline(credentials())
        for _ in range(100):
            if not child.isalive():raise RuntimeError('Owned forwarding child exited before bind')
            if subprocess.check_output(['ss','-H','-lnt','( sport = :22222 )']):break
            time.sleep(.1)
        else:raise RuntimeError('Owned forwarding bind unavailable')
        save('running.safe.json',{'parentPid':os.getpid(),'sshPid':child.pid,
             'sshStartTicks':Path(f'/proc/{child.pid}/stat').read_text().split()[21],
             'forward':'127.0.0.1:22222->server127.0.0.1:22222','miniOnly':True,
             'guestPrivateKeyTransferred':False,'guestReadyNotProven':True})
        print('PG1436_OWNED_FORWARD_READY',flush=True)
        while not stopped and child.isalive():time.sleep(1)
    finally:
        child.close(force=True)
        save('closed.safe.json',{'ownedLocalChildClosed':True,'operatorStop':stopped,
                                 'remoteVmStopped':False,'sshExit':child.exitstatus,
                                 'sshSignal':child.signalstatus})


if __name__=='__main__':main()
