"""Independent actual candidate host-mount RO and retained current whole post."""
import inspect
from pyflakes.api import check
import pg2522_current_strict_candidate_post as current

SLOT = 'pg2530-strict-candidate-ro-post-v1'


def payload(candidate=None):
    raw = current.payload(candidate).replace(current.SLOT, SLOT).replace(
        'pg2520-current-strict-placement-v1', 'pg2528-strict-candidate-host-ro-v1').replace(
        'unusedCandidatePlaced=true', 'candidateReadOnlyVerified=true')
    marker = "save=base/'" + SLOT + "'"
    if raw.count(marker) != 1:
        raise ValueError('one independent whole candidate readonly post required')
    extra = """require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
mounts=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2512'],4096).decode('ascii').strip().split(',')
require(len(mounts)==len(set(mounts))and 'ro'in mounts and 'rw'not in mounts)
"""
    raw = raw.replace(marker, extra + marker).replace("'unusedCandidate187Verified':True",
        "'unusedCandidate187Verified':True,'candidateHostReadonlyVerified':True")
    if check(raw, '<actual new candidate independent RO post>'):
        raise ValueError('complete RO post namespace required')
    compile(raw, '<new candidate RO post>', 'exec')
    return raw


def main():
    raw = inspect.getsource(current.engine.main).replace('pg2146-place-v1.safe.json', 'pg2526-prepare-ro-v1.safe.json')
    ns = {**current.engine.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<new actual candidate RO post entry>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
