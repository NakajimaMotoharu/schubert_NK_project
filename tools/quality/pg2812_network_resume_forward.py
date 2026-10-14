"""New-only owned forwarding for explicit network resume; no guest key transferred."""
import hashlib
import inspect
import os
from pathlib import Path
import lan_forward as prior

OUT=Path('/home/mini/codex/project1/work/pgpt-vm/private/pg2812-network-resume-forward-v1')


def save(name,value):
    value=dict(value)
    parent=Path('/proc')/str(os.getpid())
    value.update(parentStartTicks=int((parent/'stat').read_text().rpartition(')')[2].split()[19]),
        parentArgvSha256=hashlib.sha256((parent/'cmdline').read_bytes()).hexdigest())
    if name=='running.safe.json':
        child=Path('/proc')/str(value['sshPid'])
        value['sshArgvSha256']=hashlib.sha256((child/'cmdline').read_bytes()).hexdigest()
        value['currentGuestBootNotYetProven']=True
    with(OUT/name).open('x')as f:prior.json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())


def main():
    raw=inspect.getsource(prior.main).replace('PG1436_OWNED_FORWARD_READY','PG2812_OWNED_FORWARD_READY')
    ns={**prior.__dict__,'OUT':OUT,'save':save}
    exec(compile(raw,'<new-only network resume local forward>','exec'),ns);return ns['main']()


if __name__=='__main__':main()
