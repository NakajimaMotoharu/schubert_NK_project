"""Separate current full post plus candidate-only actual hostRO verification."""
import inspect
import json
import pg1685_unused_candidate_independent_post as prior
from pg1446_current_cold_stage import W

SLOT='pg1690-completed-candidate-ro-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT).replace('pg1684-completed-unused-placement-v4','pg1689-completed-candidate-host-ro-v1').replace('unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one independent actual RO post boundary required')
    extra=r'''
require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG1638'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
'''
    raw=raw.replace(marker,extra+'\n'+marker).replace("'unusedCandidate187Verified':True", "'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    compile(raw,'<separate completed current and candidate hostRO post>','exec')
    return raw


def main():
    actual=json.loads((W/'pg1688-prepare-ro-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['currentApprovalEpochChanged']is not False or actual['candidateSource']!='2741c4546afad6c1e8b6efbd53dfb58144edf7bb':raise ValueError('actual complete candidate-only hostRO required')
    code=inspect.getsource(prior.prior.prior.main).replace('pg1639-completed-current-before-v1',SLOT)
    ns={**prior.prior.prior.__dict__,'payload':payload}
    exec(compile(code,'<new separate full RO post transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
