"""Independent actual host-namespace RO candidate and current retained original post."""
import inspect
from pyflakes.api import check
import pg2664_operation_unused_post as current
from pg2658_operation_candidate_sources import SAVE
from pg2666_operation_ro_sources import SAVE as RO_SAVE

SLOT='pg2672-operation-ro-post-v1'


def payload(candidate=None):
    raw=current.payload(candidate).replace(current.SLOT,SLOT).replace(SAVE,RO_SAVE).replace('unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one complete RO post save boundary required')
    extra="""require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2654'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
"""
    raw=raw.replace(marker,extra+marker).replace("'unusedCandidate187Verified':True","'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    if check(raw,'<whole new candidate independent RO post>'):raise ValueError('whole post namespace required')
    compile(raw,'<operation resource RO post>','exec');return raw


def main():
    raw=inspect.getsource(current.previous.engine.main).replace('pg2146-place-v1.safe.json','pg2668-prepare-ro-v1.safe.json')
    ns={**current.previous.engine.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new RO post transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
