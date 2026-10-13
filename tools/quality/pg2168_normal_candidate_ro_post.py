"""Separate whole post plus actual host read-only mount and normal receipt."""
import inspect
import json
import pg2150_normal_unused_independent_post as prior

SLOT='pg2168-normal-candidate-ro-post-v1'


def payload():
    raw=prior.payload().replace('pg2150-normal-unused-independent-post-v1',SLOT)
    raw=raw.replace('pg2148-current-normal-unused-placement-v1','pg2167-normal-candidate-host-ro-v1').replace('unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
    marker="save=base/'"+SLOT+"'"
    extra="""require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2126'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
"""
    if raw.count(marker)!=1:raise ValueError('exact whole RO post boundary required')
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("'unusedCandidate187Verified':True","'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    from pyflakes.api import check
    if check(raw,'<normal candidate RO whole post>'):raise ValueError('whole actual namespace required')
    compile(raw,'<normal candidate RO whole post>','exec');return raw


def main():
    actual=json.loads((prior.W/'pg2166-prepare-ro-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True:raise ValueError('actual normal candidate RO complete required')
    raw=inspect.getsource(prior.main).replace('pg2146-place-v1.safe.json','pg2166-prepare-ro-v1.safe.json')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual normal RO whole post entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
