"""Current eight native streams only + frozen PG630 host. No old-source import/actions."""
import ast
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
CATALOG = r'''
import hashlib,json,pathlib,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg642-native-stop-v1');raw=(r/'before.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65';before=json.loads(raw)
names=['backup/backup.exec','cleanup/cleanup.exec','expiry/expiry.exec','parent/parent.exec']
for role,unit in [('api','schubert-nk-api.service'),('web','schubert-nk-web.service')]:
 inv=before['units'][unit]['InvocationID'];assert len(inv)==32;names.extend(['ordinary-'+role+'193/'+inv+'.terminal.exec','root-'+role+'193/'+inv+'.before-exec.exec'])
root=pathlib.Path('/run/schubert-nk/pt-coverage');result={}
def meta(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
for name in names:
 p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and 0<s.st_size<=16777216
 raw=p.read_bytes();assert meta(s)==meta(p.lstat());result[name]=hashlib.sha256(raw).hexdigest()
assert len(result)==8;print(json.dumps(result))
'''


def code(hashes):
    value = (R/'pg614_native_counter.py').read_text()
    node = next(n for n in ast.parse(value).body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'HASHES' for t in n.targets))
    old = ast.get_source_segment(value, node.value)
    value = value.replace(old, repr(hashes), 1)
    for old, new in (
        ('23b14a44b10504172e030bbd6625926bf049fb5c', '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('pg611-native-stop-v1', 'pg642-native-stop-v1'), ('pg611-native-stop-v1.exit', 'pg642-native-stop-v1.exit'),
        ('a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849', '011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c'),
        ('19b7e618ef04f79aff6cde2c2dbf45269c1f9651efaa44f04d81d84d02b85912', 'c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65'),
        ('87863', '104329'), ('5a1acaa0c35e484c979401e3b6dfb36a', '293d218b06454bd1a8ff350bb93de2d5'),
        ('86264628081', '103062293730'), ('87761979588', '104759573609'),
        ('pg613-terminal-final-v1', 'pg643-terminal-final-v2'),
        ('pg599-candidate-bootstrap-six-host-v1', 'pg630-retention-factory-six-host-v1'),
        ('cdd971634fe0f5acabe091db476f25838a55730172d3cc07244180e708f4e47d', '067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b'),
        ("tests']==3457", "tests']==3468"),
        ('pg614-current-eight-native-v1', 'pg644-current-eight-native-v1'), ('PG614-current-eight-native-v1', 'PG644-current-eight-native-v1'),
    ):
        value = value.replace(old, new)
    assert '23b14a44' not in value and 'pg599-candidate' not in value
    return value


def main():
    os.umask(0o077)
    assert (W/'pg643-terminal-final-v2.exit').read_bytes() == b'0\n'
    ssh = ['ssh', '-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    hashes = json.loads(subprocess.check_output(ssh, input=CATALOG.encode(), timeout=30))
    assert len(hashes) == 8
    env = {'__name__': 'fixed_current_native_counter', '__file__': str(Path(__file__).resolve())}
    exec(compile(code(hashes), '<same independent counter and sessions; new fixed cohort>', 'exec'), env)
    env['main']()


if __name__ == '__main__': main()
