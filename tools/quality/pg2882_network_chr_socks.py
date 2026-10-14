"""One owned loopback-only newboot CHR SOCKS, no guest key transfer/business command."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from pg1446_current_cold_stage import P,W

SLOT='pg2882-network-chr-socks-v1'


def main():
    if subprocess.check_output(['ss','-H','-ltn','sport = :55169']):raise ValueError('existing SOCKS listener is never replaced')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    argv=['ssh','-N','-D','127.0.0.1:55169','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes',
        '-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-oExitOnForwardFailure=yes','-oServerAliveInterval=5','-oServerAliveCountMax=2','ubuntu@127.0.0.1']
    with(out/'ssh.private.log').open('xb')as log:
        child=subprocess.Popen(argv,stdout=log,stderr=log)
        for _ in range(100):
            if child.poll()is not None:raise ValueError('new owned SOCKS failed, no retry')
            if subprocess.check_output(['ss','-H','-ltn','sport = :55169']):break
            time.sleep(.05)
        else:raise ValueError('bounded SOCKS readiness failed, preserve child')
        p=Path('/proc')/str(child.pid);raw=(p/'cmdline').read_bytes()
        if raw!=b'\0'.join(x.encode()for x in argv)+b'\0':raise ValueError('exact owned SSH argv required')
        value={'pid':child.pid,'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(raw).hexdigest(),
            'executable':str((p/'exe').readlink()),'parentPid':os.getpid(),'loopbackPort':55169,'businessCommandsIssued':0,'guestKeysTransferred':0}
        with(out/'running.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps(value),flush=True);code=child.wait()
    with(out/'exit.safe.json').open('x')as f:json.dump({'actualExit':code,'ownedPid':child.pid},f);f.flush();os.fsync(f.fileno())
    return code


if __name__=='__main__':raise SystemExit(main())
