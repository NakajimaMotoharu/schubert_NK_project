"""BUG1150 current retained pair: complete readonly proof, no signal authority.

Reuse full independent 24/32/187/original/native oracle, permitting only the
exact currently owned DB peer and two FLOCKs. Raw identities stay private.
"""
import inspect
import json
import pg1651_retained_no_db_readonly_proof_v2 as prior
from pg1446_current_cold_stage import W

SLOT = 'pg1664-current-unused-pair-proof-v1'
PID = 291213
TICKS = 5962776
CHILD = 291242
CHILD_TICKS = 5962938
BACKEND = 291240

PAIR = r'''
def refs_actor():
 p=pathlib.Path('/proc/291242');st=(p/'stat').read_text().rpartition(')')[2].split()
 require(int(st[19])==5962938 and int(st[1])==291213)
 argv=(p/'cmdline').read_bytes()
 require(argv==b'/usr/bin/python3\x00-B\x00/var/lib/pgpt-s1-preservation/pg1659-completed-unused-tools-v3/pg1640_native_refs.py\x00place\x00291240\x00')
 require(os.readlink(p/'exe')=='/usr/bin/python3.14')
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 children={int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()};require(not children)
 fds={}
 for f in(p/'fd').iterdir():fds[f.name]={'metadata':metadata9(f.stat()),'target':os.readlink(f)}
 require(set(fds)=={'0','1','2','3'} and fds['0']['target'].startswith('pipe:[')and fds['1']['target'].startswith('pipe:[')and fds['3']['target'].startswith('socket:['))
 require(fds['2']['target']=='/var/lib/pgpt-s1-preservation/pg1662-completed-unused-placement-v3/refs-prepare.private.log')
 bus=dbus.SystemBus(private=True)
 try:
  daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
  names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==291242]
  require(len(names)==1 and not any(str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==291213 for n in daemon.ListNames()))
 finally:bus.close()
 return {'pid':291242,'ticks':5962938,'argvSha256':hashlib.sha256(argv).hexdigest(),'authority':{k:status[k].strip()for k in ['Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid']},'cgroup':(p/'cgroup').read_text(),'fds':fds,'busNames':names}
def same_peer():
 sql="begin read only;select json_build_object('pid',pid,'port',client_port,'address',host(client_addr),'role',usename,'app',application_name,'database',datname,'state',state,'backendStart',backend_start)from pg_stat_activity where pid=291240;select count(*)from pg_locks where pid=291240 and locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock'and granted;commit;"
 lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines();require(len(lines)==2 and lines[1]==b'1')
 peer=json.loads(lines[0]);require(peer['pid']==291240 and peer['address']=='127.0.0.1'and type(peer['port'])is int and 1<=peer['port']<=65535 and peer['role']=='schubert_batch'and peer['app']=='PG998-native-stage'and peer['database']=='schubert_nk'and peer['state']=='idle in transaction')
 def sockets(pid):
  return {os.readlink(f)[8:-1]for f in(pathlib.Path('/proc')/str(pid)/'fd').iterdir()if os.readlink(f).startswith('socket:[')}
 def endpoint(v):
  import ipaddress
  a,p=v.split(':');raw=bytes.fromhex(a);decoded=b''.join(raw[i:i+4][::-1]for i in range(0,len(raw),4));ip=ipaddress.ip_address(decoded)
  if isinstance(ip,ipaddress.IPv6Address):ip=ip.ipv4_mapped
  return (str(ip),int(p,16))
 records=[l.split()for n in ['tcp','tcp6']for l in pathlib.Path('/proc/net',n).read_text().splitlines()[1:]]
 client=sockets(291213);server=sockets(291240);local=('127.0.0.1',peer['port']);database=('127.0.0.1',5432)
 left=[r for r in records if len(r)>=10 and r[3]=='01'and r[9]in client and endpoint(r[1])==local and endpoint(r[2])==database]
 right=[r for r in records if len(r)>=10 and r[3]=='01'and r[9]in server and endpoint(r[1])==database and endpoint(r[2])==local]
 require(len(left)==len(right)==1)
 return {'activity':peer,'clientInode':left[0][9],'serverInode':right[0][9]}
def pair():
 a=actor();require(len(a['fds'])==101)
 return {'parent':a,'child':refs_actor(),'peer':same_peer()}
'''


def payload():
    raw = prior.payload()
    for a, b in [('289328', str(PID)), ('5627480', str(TICKS)), ('289326', '291211'), ('pg1645-completed-unused-tools-v2', 'pg1659-completed-unused-tools-v3'), ('pg1651-retained-no-db-proof-v2', SLOT)]:
        raw = raw.replace(a, b)
    raw = raw.replace('require(not children)', 'require(children=={291242})')
    raw = raw.replace("lines[-2:]==[b'0',b'0']", "lines[-2:]==([b'0',b'0']if PEER_CLOSED else[b'1',b'1'])")
    marker = 'bus=dbus.SystemBus(private=True);manager='
    index = raw.index(marker)
    raw = raw[:index] + PAIR + '\n' + raw[index:]
    # The old noDB persistence tail is never executed for a pair.
    index = raw.index('a=actor();require(a==actor());locks=')
    raw = raw[:index] + TAIL
    fixed = json.loads((W / 'pg1660-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit'] != 0:
        raise ValueError('actual frozen current tool required')
    raw = raw.replace('TOOL_HASHES=' + repr(json.loads((W / 'pg1645-frozen-v1.safe.json').read_bytes())['fileHashes']), 'TOOL_HASHES=' + repr(fixed['fileHashes']))
    raw = 'PEER_CLOSED=False\n' + raw
    compile(raw, '<current full readonly unused pair>', 'exec')
    return raw


TAIL = r'''
save=base/'pg1664-current-unused-pair-proof-v1';require(not os.path.lexists(save))
private=base/'pg1662-completed-unused-placement-v3'
require({p.name for p in private.iterdir()}=={'before.private.json','refs-prepare.private.log'})
before=(private/'before.private.json').read_bytes();require(hashlib.sha256(before).hexdigest()=='9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37')
failure=(private/'refs-prepare.private.log').read_bytes();require(b'FileNotFoundError'in failure and b'method=place_candidate line=111'in failure)
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'originalAfterSha256':'9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37','native':native,'toolHashes':TOOL_HASHES,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'normalNewRefScope':True,'candidateNotPlaced':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':291213,'childPid':291242,'backendPid':291240,'parentFdCount':101,'childFdCount':4,'samePeer':True,'ownedLocks':2,'allOriginalValuesUnchanged':True,'candidateNotPlaced':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    ns = {**prior.prior.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(prior.prior.main), '<new readonly pair transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
