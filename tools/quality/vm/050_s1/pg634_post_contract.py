"""Independent postcondition calculation; no Production or deployment helper import."""
import hashlib
import json
import stat


def finite(before, after, mode):
    def require(v):
        if not v: raise ValueError('independent pending post refused')
    fields = set('backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split())
    require(type(before) is dict and type(after) is dict and set(before) == set(after) == fields)
    require(before['runtime'] is None and after['runtime'] is None)
    require(mode in ('verify', 'activate'))
    def exact(a, b):
        return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)
    if mode == 'verify':
        require(exact(before, after)); return True
    require(all(exact(before[k], after[k]) for k in fields - {'current', 'approval'}))
    require(before['current'] == '/opt/schubert-nk/releases/0.1.0-PG621' and after['current'] == '/opt/schubert-nk/releases/0.1.0-PG631')
    raw = b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG631\nmanifest_sha256=57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe\n'
    old, new = before['approval'], after['approval']
    require(type(old) is dict and type(new) is dict and set(old) == set(new) == {'metadata', 'sha256'})
    a, b = old['metadata'], new['metadata']
    require(type(a) is list and type(b) is list and len(a) == len(b) == 9 and all(type(x) is int for x in a + b))
    require(a[0] == b[0] > 0 and a[1] > 0 and b[1] > 0 and a[1] != b[1])
    require(a[2:6] == b[2:6] == [0, 0, stat.S_IFREG | 0o400, 1])
    require(b[6] == len(raw) and new['sha256'] == hashlib.sha256(raw).hexdigest())
    return True


def fresh_join(after, current, approval, runtime_names, unit_paths):
    def require(v):
        if not v: raise ValueError('independent fresh post join refused')
    require(type(after) is dict and type(current) is str and current == after['current'])
    require(type(approval) is dict and json.dumps(approval, sort_keys=True, allow_nan=False)
            == json.dumps(after['approval'], sort_keys=True, allow_nan=False))
    require(type(runtime_names) is list and not runtime_names)
    require(type(unit_paths) is list and len(unit_paths) == 18
            and all(type(p) is str for p in unit_paths)
            and len(set(unit_paths)) == 18 and set(unit_paths) == set(after['unitFiles']))
    return True
