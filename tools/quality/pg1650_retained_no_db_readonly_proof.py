"""Current fixed retained SIGNED_CURRENT owner, read-only proof; signals0.

Full original/DB/config/native checks are reused as independent logic. Only the
two FLOCKs are expected to belong to this exact no-child, before-DB Java owner.
All raw process/FD and original data stay in private host/guest evidence.
"""
import hashlib
import json
import os
import subprocess
import pg1641_completed_current_preflight_v2 as prior
from pg1446_current_cold_stage import SSH, W

PID = 289328
TICKS = 5627480
SLOT = 'pg1650-retained-no-db-proof-v1'

BODY = r'''
P=pathlib.Path('/proc/289328')
def actor():
 require(P.exists()and int((P/'stat').read_text().rpartition(')')[2].split()[19])==5627480)
 require(os.readlink(P/'exe')=='/opt/jdk-25.0.4/bin/java')
 require((P/'cmdline').read_bytes()==EXPECTED_ARGV)
 status=dict(line.split(':',1)for line in(P/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['PPid'].strip()=='289326')
 children={int(c)for t in(P/'task').iterdir()for c in(t/'children').read_text().split()};require(not children)
 fds={}
 for p in(P/'fd').iterdir():
  s=p.stat();fds[p.name]={'metadata':metadata9(s),'target':os.readlink(p)}
 return {'pid':289328,'ticks':5627480,'argvSha256':hashlib.sha256(EXPECTED_ARGV).hexdigest(),'authority':{k:status[k].strip()for k in ['Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid']},'cgroup':(P/'cgroup').read_text(),'fds':fds}
def owned_lock(name):
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 hits=[]
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)<8:continue
  d=f[5].split(':')
  if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(f)
 require(len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE','289328'])
 actual=actor();linked=[fd for fd,v in actual['fds'].items()if tuple(v['metadata'][:2])==(s.st_dev,s.st_ino)]
 require(len(linked)==1)
 info=(P/'fdinfo'/linked[0]).read_text();require(any(line.split()[2:6]==['FLOCK','ADVISORY','WRITE','289328']for line in info.splitlines()if line.startswith('lock:')))
 return {'name':name,'metadata':metadata9(s),'fd':linked[0]}
'''


def payload():
    raw = prior.payload()
    marker = "save=base/'pg1641-completed-current-before-v2'"
    if raw.count(marker) != 1:
        raise ValueError('one full current proof persistence boundary required')
    raw = raw[:raw.index(marker)]
    start = raw.index("  for name in ('maintenance.lock','startup-admission.lock'):")
    end = raw.index("  require(tree(pathlib.Path('/run/systemd/system'))", start)
    raw = raw[:start] + "  for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n" + raw[end:]
    place = raw.index('bus=dbus.SystemBus(private=True);manager=')
    raw = raw[:place] + BODY + '\n' + raw[place:]
    raw += r'''
tool=base/'pg1645-completed-unused-tools-v2'
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tool/'payload-sha256.json').read_bytes())==TOOL_HASHES)
require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
a=actor();require(a==actor());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'pg1650-retained-no-db-proof-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'actor':a,'locks':locks,'originalAfterSha256':'9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37','native':native,'toolHashes':TOOL_HASHES,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'clientAdvisory0':True,'nativeCurrent8Historical6Unchanged':True,'normalNewRefScope':True,'candidateNotPlaced':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'pid':289328,'ticks':5627480,'argvSha256':a['argvSha256'],'fdCount':len(a['fds']),'noChild':True,'ownedLocks':2,'clientAdvisory0':True,'allOriginalValuesUnchanged':True,'normalNewRefScope':True,'candidateNotPlaced':True,'signals0':True,'formalAccepted':False}))
'''
    cp = '/var/lib/pgpt-s1-preservation/pg1645-completed-unused-tools-v2:/opt/schubert-nk/releases/0.1.0-PG1544/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1544/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1544/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1544/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    expected = ['/opt/jdk-25.0.4/bin/java', '--enable-native-access=ALL-UNNAMED', '-cp', cp, 'Pg1640UnusedStage', 'place']
    pins = json.loads((W / 'pg1645-frozen-v1.safe.json').read_bytes())['fileHashes']
    raw = 'EXPECTED_ARGV=' + repr(b'\0'.join(x.encode() for x in expected) + b'\0') + '\nTOOL_HASHES=' + repr(pins) + '\n' + raw
    compile(raw, '<actual retained noDB owner full readonly proof>', 'exec')
    return raw


def main():
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-'], input=raw, capture_output=True, timeout=90)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'signals0': True, 'formalAccepted': False}
    if r.returncode == 0:
        value['guest'] = json.loads(r.stdout)
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
