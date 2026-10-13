"""Separate retained-current and new candidate actual host mount RO oracle."""
import inspect
import pg2418_question_unused_post as prior
from pyflakes.api import check

SLOT='pg2426-question-candidate-ro-post-v1'


def payload(candidate=None):
    raw=prior.payload(candidate).replace(prior.SLOT,SLOT).replace(
        'pg2416-question-unused-placement-v1','pg2424-question-candidate-host-ro-v1').replace(
        'unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:
        raise ValueError('one independent whole readonly post boundary required')
    extra="""require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2406'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
"""
    raw=raw.replace(marker,extra+marker).replace("'unusedCandidate187Verified':True",
        "'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    if check(raw,'<whole actual new candidate hostRO post>'):
        raise ValueError('full independent readonly globals required')
    compile(raw,'<question RO whole post>','exec')
    return raw


def main():
    raw=inspect.getsource(prior.prior.main).replace('pg2146-place-v1.safe.json','pg2422-prepare-ro-v1.safe.json')
    namespace={**prior.prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<normal current new candidate RO post>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':
    raise SystemExit(main())
