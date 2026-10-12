"""New SSC279 live peer profile; old cold1 proof failure remains immutable."""
import ast
import inspect
import json
import os
import pathlib
import subprocess
import pg1777_warning_retained_pair_readonly_proof as prior
from pg553_inbox_oracle import require

SLOT='pg1780-warning-live-peer-readonly-v1'


def command(args,limit):
    r=subprocess.run(args,stdin=subprocess.DEVNULL,capture_output=True,timeout=5)
    require(r.returncode==0 and len(r.stdout)<=limit)
    return r.stdout


def validate_peers(rows,lock_count):
    if type(rows)is not list or len(rows)!=4 or type(lock_count)is not int or lock_count!=1:raise ValueError('exact live peer set/sole management lock required')
    roles={'schubert_app':2,'schubert_web_session':1,'schubert_batch':1}
    if {r.get('role')for r in rows}!=set(roles)or any(sum(r['role']==k for r in rows)!=v for k,v in roles.items()):raise ValueError('exact role populations required')
    pids=[]
    for r in rows:
        if type(r.get('pid'))is not int or r['pid']<=1 or type(r.get('port'))is not int or not 1<=r['port']<=65535 or r.get('address')!='127.0.0.1'or r.get('database')!='schubert_nk'or type(r.get('backendStart'))is not str or not r['backendStart']:raise ValueError('typed current loopback DB identity required')
        pids.append(r['pid'])
    if len(set(pids))!=4:raise ValueError('unique current backend required')
    batch=next(r for r in rows if r['role']=='schubert_batch')
    if batch['pid']!=476114 or batch.get('app')!='PG998-native-stop'or batch.get('state')!='idle in transaction':raise ValueError('current retained management peer required')
    return batch


def same_peer():
    import ipaddress
    q="begin read only;select json_build_object('pid',pid,'port',client_port,'address',host(client_addr),'role',usename,'app',application_name,'database',datname,'state',state,'backendStart',backend_start)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid()order by pid;select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock'and granted;commit;"
    lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],16384).splitlines()
    require(len(lines)==5 and lines[-1]==b'1');rows=[json.loads(line)for line in lines[:-1]];batch=validate_peers(rows,1)
    require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"begin read only;select count(*)from pg_locks where pid=476114 and locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"],4096).strip()==b'1')
    def sockets(pid):
        return {os.readlink(f)[8:-1]for f in(pathlib.Path('/proc')/str(pid)/'fd').iterdir()if os.readlink(f).startswith('socket:[')}
    def endpoint(v):
        a,p=v.split(':');b=bytes.fromhex(a);address=ipaddress.ip_address(b''.join(b[i:i+4][::-1]for i in range(0,len(b),4)))
        if isinstance(address,ipaddress.IPv6Address):address=address.ipv4_mapped
        return str(address),int(p,16)
    records=[l.split()for n in ['tcp','tcp6']for l in pathlib.Path('/proc/net',n).read_text().splitlines()[1:]]
    owners={'schubert_app':451130,'schubert_web_session':452144,'schubert_batch':476087};bindings=[]
    for row in rows:
        owner=owners[row['role']];client=sockets(owner);server=sockets(row['pid']);local=('127.0.0.1',row['port']);db=('127.0.0.1',5432)
        left=[r for r in records if len(r)>=10 and r[3]=='01'and r[9]in client and endpoint(r[1])==local and endpoint(r[2])==db]
        right=[r for r in records if len(r)>=10 and r[3]=='01'and r[9]in server and endpoint(r[1])==db and endpoint(r[2])==local]
        require(len(left)==len(right)==1);bindings.append({'ownerPid':owner,'backendPid':row['pid'],'clientInode':left[0][9],'serverInode':right[0][9],'role':row['role']})
    return {'activity':batch,'allPeers':rows,'bindings':bindings,'liveDaemonPeersPreserved':True}


def payload():
    raw=prior.payload();node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='same_peer')
    raw=raw.replace(ast.get_source_segment(raw,node),inspect.getsource(validate_peers)+'\n'+inspect.getsource(same_peer))
    raw=raw.replace(prior.SLOT,SLOT)
    raw=raw.replace("'ownedLocks':2,","'ownedLocks':2,'allFourCurrentPeersSocketBound':True,'liveDaemonPeersPreserved':True,")
    from pyflakes.api import check
    if check(raw,'<actual live peer closure>'):raise ValueError('all emitted global dependencies required')
    compile(raw,'<live peer exact four proof>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1766-next-day-independent-candidates-v1',SLOT)
    # prior.main constructs transport source using its SLOT global.
    ns={**prior.__dict__,'payload':payload,'SLOT':SLOT}
    exec(compile(raw,'<fresh readonly live peer proof>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
