"""Separate signed candidate hostRO and old/current full resource post."""
import inspect
import pg1866_warning_direct_unused_post as prior

SLOT='pg1871-warning-candidate-ro-post-v1'


def payload(post):
    raw=prior.payload(post).replace(prior.SLOT,SLOT).replace('pg1864-warning-unused-placement-v1','pg1869-warning-candidate-host-ro-v1').replace('unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one independent host RO result boundary required')
    extra="""require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG1846'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
"""
    raw=raw.replace(marker,extra+'\n'+marker).replace("'unusedCandidate187Verified':True","'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    compile(raw,'<same full current and hostRO candidate>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1865-place-v1.safe.json','pg1870-prepare-ro-v1.safe.json')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual RO separate post transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
