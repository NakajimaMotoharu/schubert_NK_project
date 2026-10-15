"""SSC285 complete fresh39/24/32/18/187/ordinary-TCP proof, signal-free."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg3502_signed_current_retained_readonly as diagnostic
import pg3504_signed_current_profile_contract as contract
import pg3509_tcp_pair_contract as tcp_contract
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate

SLOT = 'pg3506-signed-current-full-proof-v2'


def helpers(slot=SLOT):
    raw = diagnostic.payload()
    raw = raw[:raw.index('a=actors();require(not a[0][\'children\'])')]
    raw = raw.replace(diagnostic.SLOT, slot)
    raw = raw.replace('import hashlib,json,os,pathlib,stat,subprocess,datetime',
                      'import hashlib,json,os,pathlib,stat,subprocess')
    # All frozen independent profile functions are data in this one connection.
    profile = inspect.getsource(contract)
    raw += '\nimport re\n' + '\n'.join(ast.get_source_segment(profile, n) for n in ast.parse(profile).body
                                         if isinstance(n, (ast.Assign, ast.FunctionDef))) + '\n'
    source = (W / 'pg3476-outbox-current-full-seal-v1/payload.private.py').read_text()
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name in ['configuration_value', 'complete_configuration']:
            raw += '\n' + ast.get_source_segment(source, node) + '\n'
    module = W.parent.parent / 'toolchain/jdk-25.0.4/lib/modules'
    raw += '\nEXPECTED_MODULE_SHA=' + repr(hashlib.sha256(module.read_bytes()).hexdigest()) + '\n'
    raw += '\nimport ipaddress\n' + inspect.getsource(tcp_contract.endpoint) + '\n' + inspect.getsource(tcp_contract.tcp_pair)
    return raw + HELPERS


HELPERS = r'''
import ctypes,time,dbus
old_raw=(base/'pg3502-signed-current-retained-readonly-v1/proof.private.json').read_bytes()
require(hashlib.sha256(old_raw).hexdigest()=='16145fbc02e111358b6b3c64bc7e4964361ae23d222b39774a9805c55ad84ec1')
old_proof=json.loads(old_raw);old_actor=old_proof['actors'][0]
CONFIG_FIELDS=set(next(iter(seal['configuration'].values())))
def command(args,limit=67108864):
 r=subprocess.run(args,capture_output=True,timeout=30);require(r.returncode==0 and len(r.stdout)<=limit);return r.stdout
def kcmp(left,right):
 c=ctypes.CDLL(None,use_errno=True);c.syscall.restype=ctypes.c_long
 value=c.syscall(312,410196,410196,0,left,right)
 require(value>=0);return value==0
def sockets(pid):
 result=set()
 for f in pathlib.Path('/proc',str(pid),'fd').iterdir():
  try:v=os.readlink(f)
  except(FileNotFoundError,ProcessLookupError):continue
  if v.startswith('socket:['):result.add(v[8:-1])
 return result
def tcp_peers(peers):
 expected={'schubert_app':('schubert-nk-api','schubert-nk-api.service',2,8),'schubert_web_session':('schubert-nk-web','schubert-nk-web.service',1,2)}
 require(all(p['role']in expected and p['application']==expected[p['role']][0]and p['address']=='127.0.0.1'and p['state']in {'idle','idle in transaction','active'}for p in peers))
 table=[line.split()for family in ['tcp','tcp6']for line in pathlib.Path('/proc/net',family).read_text().splitlines()[1:]]
 result={}
 for role,(app,unit,lo,hi)in expected.items():
  rows=[p for p in peers if p['role']==role];require(lo<=len(rows)<=hi)
  client=sockets(seal['units'][unit]['MainPID']);matches=[]
  for p in rows:
   outbound,inbound=tcp_pair(table,p['port'],client,sockets(p['pid']))
   matches.append({'activity':p,'clientInode':outbound,'serverInode':inbound})
  result[unit]=matches
 return result
def snapshot():
 actor=actors()[0];fresh39(old_actor,actor,time.time_ns())
 require(not os.path.lexists(base/'pg3490-native-stop-v1'))
 module=pathlib.Path('/opt/jdk-25.0.4/lib/modules');require(hashlib.sha256(module.read_bytes()).hexdigest()==EXPECTED_MODULE_SHA)
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG3420');mr=(release/'RELEASE-MANIFEST.json').read_bytes()
 require(hashlib.sha256(mr).hexdigest()=='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72')
 manifest=json.loads(mr);signed={str(release/v['path']):v for v in manifest['artifacts']};require(len(signed)==187)
 for path,v in signed.items():
  p=pathlib.Path(path);s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and s.st_uid==0 and s.st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
 command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg3420-manifest.sig')],4096)
 for n,v in actor['fds'].items():
  if n in {'0','1','2'}:continue
  p=pathlib.Path(v['target']);s=p.lstat();linked=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
  require(linked==v['metadata']and not p.is_symlink()and not os.listxattr(p))
  if n in {str(i)for i in range(4,28)}:require(str(p)in signed)
 require(kcmp(43,128)and not kcmp(30,33))
 locks=[]
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
  rows=[l.split()for l in pathlib.Path('/proc/locks').read_text().splitlines()if len(l.split())>=8 and l.split()[5]==key]
  require(len(rows)==1 and rows[0][1:5]==['FLOCK','ADVISORY','WRITE','410196'])
  locks.append({'name':name,'metadata':metadata(p),'owner':410196})
 units={};configuration={}
 for name,old in seal['units'].items():
  text=command(['systemctl','show',name,'--property='+','.join(sorted(old))],1048576).decode();units[name]=dict(x.split('=',1)for x in text.splitlines());require(units[name]==old)
  cfg=complete_configuration(command(['systemctl','show',name,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode(),name)
  require(cfg==seal['configuration'][name]);configuration[name]=cfg
 for name,v in seal['actors'].items():
  p=pathlib.Path('/proc')/seal['units'][name]['MainPID'];s=(p/'stat').read_text().rsplit(')',1)[1].split()
  require(int(s[19])==v['ticks']and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==v['argvSha256']and(p/'cgroup').read_text()==v['cgroup'])
 sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
 for t in seal['rows']:sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+' t)q;'
 sql+="select json_build_object('peer',json_build_object('pid',pid,'role',usename,'application',application_name,'state',state,'backendStart',backend_start,'address',client_addr,'port',client_port))from pg_stat_activity where datname='schubert_nk'and pid<>pg_backend_pid();select json_build_object('advisory',json_build_object('pid',pid,'granted',granted))from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1;commit;"
 values=[json.loads(x)for x in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines()]
 rows={v['table']:v['rows']for v in values if 'table'in v};peers=[v['peer']for v in values if 'peer'in v]
 require(len(rows)==24 and rows==seal['rows']and not any('advisory'in v for v in values))
 tcp=tcp_peers(peers)
 unit_files={}
 for path,v in seal['unitFiles'].items():
  p=pathlib.Path(path);require(metadata(p)==v['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']);unit_files[path]=v
 durable={k:tree(pathlib.Path(os.path.commonpath(list(v))))for k,v in seal['durable'].items()};require(durable==seal['durable'])
 native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'));require(native==seal['native'])
 runtime=tree(pathlib.Path('/run/systemd/system'));require(runtime==seal['runtime'])
 startup=tree(pathlib.Path('/run/schubert-nk/startup'));require(startup==seal['startup'])
 after=actors()[0];fresh39(actor,after,time.time_ns());require(canonical_actor(actor)==canonical_actor(after))
 return {'actor':actor,'locks':locks,'units':units,'configuration':configuration,'rows':rows,'peers':peers,'ordinaryTcp':tcp,'unitFiles':unit_files,'durable':durable,'native':native,'runtime':runtime,'startup':startup,'OFD43_128_same':True,'OFD30_33_distinct':True}
'''


TAIL = r'''
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in seal['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 a=snapshot();b=snapshot();require(a==b)
 save.mkdir(mode=0o700);encoded=json.dumps(a,sort_keys=True).encode()
 with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 for p in [save,base]:
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'actorPid':410196,'actorFdCount':39,'all24And32And18And187Unchanged':True,'allOriginalBackupRuntimeStartupNativeUnchanged':True,'fourOrdinaryOwnersAndAllTcpVerified':True,'managementDbAndAdvisory0':True,'soleM_A':True,'OFD43_128_same':True,'OFD30_33_distinct':True,'freshProofSaved':True,'newTenRefsReturnedNormally':True,'signals0':True,'formalAccepted':False}))
'''


def payload():
    raw = helpers() + TAIL
    if check(raw, '<complete signedcurrent39 full proof>'):
        raise ValueError('all fullproof exports required')
    compile(raw, '<fresh39 full proof>', 'exec')
    return raw


def main():
    for name in ['343_設定file・directory・初期data・migration・切戻し設計.md']:
        path = 'documents/300_SS/340_batch・基盤/' + name
        if 'SSC-285' not in subprocess.check_output(['git','show','origin/main:' + path],text=True):
            raise ValueError('published current SSC285 profile required')
    os.umask(0o077);out=W/SLOT;out.mkdir()
    raw=payload();(out/'payload.private.py').write_text(raw)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P/'current-management-critical.lock',validate_owner=diagnostic.host_owner,require_completion=lambda:False):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
        diagnostic.host_owner(P/'current-management-critical.lock')
    (out/'stderr.private.log').write_bytes(result.stderr);(out/'stdout.private.json').write_bytes(result.stdout)
    v={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'signals0':True,'oldUnknown':True,'formalAccepted':False}
    if result.returncode==0:v['guest']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return result.returncode


if __name__=='__main__':raise SystemExit(main())
