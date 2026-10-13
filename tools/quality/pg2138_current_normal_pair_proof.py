"""BUG1213 current normal-unused pair full read-only witness; no signal authority."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, SSH
from pg1650_retained_no_db_readonly_proof import BODY as ACTOR
from pg1651_retained_no_db_readonly_proof_v2 import BODY as LOCKS
from pg1664_current_unused_pair_readonly_proof import PAIR
from pg1885_publication_current_fd_proof import payload as historical_pair

SLOT = 'pg2138-current-normal-unused-pair-proof-v1'
PID, TICKS, CHILD, CHILD_TICKS, BACKEND = 676884, 12181426, 676916, 12181630, 676914
TOOLS = 'pg2132-current-normal-unused-tools-v1'
SAVE = 'pg2136-current-normal-unused-placement-v1'


class Current(ast.NodeTransformer):
    def visit_Constant(self, node):
        numbers = {289328: PID, 5627480: TICKS, 289326: 676882,
                   291213: PID, 5962776: TICKS, 291242: CHILD, 5962938: CHILD_TICKS, 291240: BACKEND}
        value = node.value
        if type(value) is int:
            value = numbers.get(value, value)
        elif type(value) is str:
            for old, new in numbers.items():
                value = value.replace(str(old), str(new))
            value = value.replace('pg1662-completed-unused-placement-v3', SAVE)
        elif type(value) is bytes:
            value = value.replace(b'pg1659-completed-unused-tools-v3/pg1640_native_refs.py',
                                  (TOOLS + '/pg2132_native_refs.py').encode())
            value = value.replace(b'291240', str(BACKEND).encode())
        return ast.copy_location(ast.Constant(value), node)


def helpers():
    old = ast.parse(historical_pair())
    relation = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == 'fd_relation')
    raw = ACTOR[:ACTOR.index('def owned_lock(')].replace('require(not children)',
                                                        'require(children=={291242})')
    raw += ast.unparse(relation) + '\n' + LOCKS + '\n' + PAIR
    tree = Current().visit(ast.parse(raw)); ast.fix_missing_locations(tree)
    return ast.unparse(tree) + '\n'


def payload():
    path = W / 'pg2130-current-normal-before-v1/payload.private.py'
    manifest = json.loads((path.parent / 'manifest.safe.json').read_bytes())
    raw = path.read_text()
    if manifest['actualExit'] != 0 or hashlib.sha256(raw.encode()).hexdigest() != manifest['payloadSha256']:
        raise ValueError('actual qualified independent full reader required')
    raw = raw[:raw.index("save=base/'pg2130-current-normal-before-v1'")]
    needle = "lines[-2:] == [b'0', b'0']"
    if raw.count(needle) != 1:
        raise ValueError('one current owned DB resource boundary required')
    raw = raw.replace(needle, "lines[-2:] == [b'1', b'1']")
    start = raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):")
    end = raw.index("        require(tree(pathlib.Path('/run/systemd/system'))", start)
    raw = raw[:start] + "        for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n" + raw[end:]
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('one full normal-scope reader required')
    raw = raw.replace(marker, '\n' + helpers() + marker)
    frozen = json.loads((W / 'pg2133-frozen-v1.safe.json').read_bytes())
    begin = json.loads((W / 'pg2134-place-v1.begin.safe.json').read_bytes())
    cp = '/var/lib/pgpt-s1-preservation/' + TOOLS
    cp += ':/opt/schubert-nk/releases/0.1.0-PG1846/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1846/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1846/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1846/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv = ['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg2132UnusedStage','place']
    if frozen['actualExit'] != 0 or begin['operatorSource'] != '7e519fe34b07beef24a3d943fddba639299842ed':
        raise ValueError('same immutable actual operator required')
    raw = 'EXPECTED_ARGV=' + repr(b'\0'.join(v.encode() for v in argv) + b'\0') + '\nFILES=' + repr(frozen['fileHashes']) + '\n' + raw
    raw += TAIL.replace('__SLOT__', SLOT).replace('__TOOLS__', TOOLS).replace('__SAVE__', SAVE)
    from pyflakes.api import check
    if check(raw, '<current normal unused full pair>'):
        raise ValueError('whole actual namespace required')
    compile(raw, '<current normal unused full pair>', 'exec')
    return raw


TAIL = r'''
tool=base/'__TOOLS__'
for name,digest in FILES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tool/'payload-sha256.json').read_bytes())==FILES)
failure=base/'__SAVE__';require({p.name for p in failure.iterdir()}=={'refs-prepare.private.log'})
require((failure/'refs-prepare.private.log').read_bytes()==b'PG2132_READBACK_UNKNOWN type=ValueError\nPG2132_FRAME method=<module> line=163\nPG2132_FRAME method=main line=94\nPG2132_FRAME method=capture_data line=61\nPG2132_FRAME method=require line=12\n')
require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126').exists()and not(base/'pg2126-manifest.sig').exists())
native_before=json.loads((base/'pg2130-current-normal-before-v1/native-before.private.json').read_bytes());require(native==native_before)
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'__SLOT__';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'originalAfterSha256':'75669b01c69e4ecc2459e73dbd3e0a6abcac7cdfaf6ce4095561314d533b1eb4','native':native,'toolHashes':FILES,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'normalNewRefScope':True,'candidateNotPlaced':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':676884,'childPid':676916,'backendPid':676914,'parentFdCount':101,'childFdCount':4,'samePeer':True,'ownedLocks':2,'allOriginalValuesUnchanged':True,'candidateNotPlaced':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077)
    out = W / SLOT; out.mkdir(mode=0o700)
    raw = payload().encode(); (out / 'payload.private.py').write_bytes(raw)
    r = subprocess.run(SSH + ['sudo','-n','python3','-B','-'], input=raw, capture_output=True, timeout=120)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if not r.returncode: value['guest'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value,sort_keys=True))
    print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
