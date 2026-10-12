"""SSC280 one current pair handoff; fresh shared directory/ordinary peers separated."""
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1788_warning_pair_once_handoff_v3 import payload as previous_payload
from pg1793_warning_fresh_history_contract import match_parent_history,match_peer_history

SLOT='pg1796-warning-fresh-pair-once-handoff-v1'


def once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('one explicit fresh retained boundary required')
    return raw.replace(old,new,1)


def payload():
    raw=previous_payload().replace('pg1788-warning-pair-once-handoff-v3',SLOT)
    raw=once(raw,"BASE/'pg1782-warning-live-peer-readonly-v1/proof.private.json'","BASE/'pg1794-warning-fresh-pair-readonly-v1/proof.private.json'")
    raw=once(raw,'4c226a4e958291f100b1b20e05ff854dda3e511e1cdc58d16cb11bfb85834a6d','0351bb0dd4943d5ffb4dcbe4270333b32819ac175374a6eb99715785001c3400')
    marker='CHILD_REAPED=False'
    raw=once(raw,marker,inspect.getsource(match_parent_history)+'\n'+inspect.getsource(match_peer_history)+'\n'+marker)
    raw=once(raw,"require(same(parent,retained_proof['parent']))","match_parent_history(retained_proof['parent'],parent)")
    raw=raw.replace("require(same(same_peer(),retained_proof['peer']))","match_peer_history(retained_proof['peer'],same_peer())")
    raw=once(raw,"require(same([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']],retained_proof['locks'])and same(same_peer(),retained_proof['peer']))","require(same([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']],retained_proof['locks']));match_peer_history(retained_proof['peer'],same_peer())")
    raw=once(raw,"require(all(same(v,fds[k])for k,v in actual.items()))","match_parent_history(retained_proof['parent'],{**current,'fds':{**fds,**actual}})")
    # Ordinary pool backend generations may renew normally; verify all current
    # socket endpoints by the same exact role/owner binding, not an old id list.
    start=raw.index(' # Standard daemon DB sockets are still bound')
    end=raw.index(" with(HANDOFF/'after.private.json')",start)
    raw=raw[:start]+r'''
 def sockets(pid):return {os.readlink(f)[8:-1]for f in(pathlib.Path('/proc')/str(pid)/'fd').iterdir()if os.readlink(f).startswith('socket:[')}
 import ipaddress
 def endpoint(v):
  a,p=v.split(':');b=bytes.fromhex(a);address=ipaddress.ip_address(b''.join(b[i:i+4][::-1]for i in range(0,len(b),4)))
  if isinstance(address,ipaddress.IPv6Address):address=address.ipv4_mapped
  return str(address),int(p,16)
 q="begin read only;select json_build_object('pid',pid,'port',client_port,'role',usename,'address',host(client_addr),'database',datname)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid()order by pid;commit;"
 peers=[json.loads(l)for l in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()]
 require(len(peers)==3 and sum(p['role']=='schubert_app'for p in peers)==2 and sum(p['role']=='schubert_web_session'for p in peers)==1)
 records=[l.split()for n in ['tcp','tcp6']for l in pathlib.Path('/proc/net',n).read_text().splitlines()[1:]]
 for row in peers:
  require(type(row['pid'])is int and row['pid']>1 and type(row['port'])is int and 1<=row['port']<=65535 and row['address']=='127.0.0.1'and row['database']=='schubert_nk')
  owner={'schubert_app':451130,'schubert_web_session':452144}[row['role']];client=sockets(owner);server=sockets(row['pid']);local=('127.0.0.1',row['port']);db=('127.0.0.1',5432)
  require(sum(len(r)>=10 and r[3]=='01'and r[9]in client and endpoint(r[1])==local and endpoint(r[2])==db for r in records)==1)
  require(sum(len(r)>=10 and r[3]=='01'and r[9]in server and endpoint(r[1])==db and endpoint(r[2])==local for r in records)==1)
'''+raw[end:]
    from pyflakes.api import check
    if check(raw,'<actual fresh pair once recovery>'):raise ValueError('emitted globals closed')
    compile(raw,'<actual once recovery fresh guards>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock')as fd:
        s=os.fstat(fd);gate={'pid':os.getpid(),'device':s.st_dev,'inode':s.st_ino,'held':True}
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=240)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'hostGate':gate,'oldNormalCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
