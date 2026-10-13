"""SS343/QA047/052: new boot read-only proof, not an old owned-stop receipt.

PT-OPS-2204-001. Private sealed rows/trees stay in guest. No permit/run replay.
"""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg2186_newsource_full_live_seal import payload as live_payload
from pg2176_newsource_normal_observer import SOURCE,BOM

SLOT='pg2204-outage-cold-reauthentication-v1'
SEALED='f109a515cbd67998aeee38de102c0cceacdb9b95fbe0e4b7b09645d83821f27a'


def payload():
    v=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
    raw=live_payload({**v['binding'],'rootPid':v['rootPid']});t=ast.parse(raw)
    wanted={'configuration_value','complete_configuration','require','command','metadata','tree','show','cold','exec_record'}
    nodes=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    if len(nodes)!=len(wanted):raise ValueError('qualified read-only helper closure required')
    configs=[];bounds=[]
    for n in t.body:
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='exec' and len(n.value.args)==2:
            a=n.value.args[1]
            if isinstance(a,ast.Name) and a.id=='CONFIG_CONTRACT':configs.append(ast.get_source_segment(raw,n))
            if isinstance(a,ast.Name) and a.id=='CAPTURE_BOUND':bounds.append(ast.get_source_segment(raw,n))
    if len(configs)!=1 or len(bounds)!=1:raise ValueError('qualified config/capture contract required')
    prefix='import os,pathlib,stat,subprocess,json,hashlib,re,dbus\nCONFIG_CONTRACT={}\nCAPTURE_BOUND={}\n'+configs[0]+'\n'+bounds[0]+'\n'
    prefix+="CONFIG_FIELDS=CONFIG_CONTRACT['FIELDS']\nFIELDS=set('Id LoadState ActiveState SubState Job MainPID ControlPID InvocationID Type Restart RemainAfterExit Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL'.split())\n"
    prefix+=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'
    prefix+='SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\nSEALED='+repr(SEALED)+'\nSLOT='+repr(SLOT)+'\n'
    body=r'''
os.umask(0o077)
require(os.geteuid()==0)
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation')
raw=(BASE/'pg2186-newsource-full-live-seal-v1/before.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()==SEALED)
old=json.loads(raw);require(old['source']==SOURCE and old['manifestSha256']==BOM)
boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
require(boot!='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
UNITS=sorted(old['units']);require(len(UNITS)==10)
def observe():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
 units={};configuration={}
 for n in UNITS:
  state=show(n);require(cold(state))
  c=pathlib.Path('/sys/fs/cgroup/system.slice')/n
  if c.exists():
   for d in [c,*[p for p in c.rglob('*') if p.is_dir()]]:
    require(not(d/'cgroup.procs').read_text().strip() and 'populated 0\n' in(d/'cgroup.events').read_text())
  units[n]=state
  value=complete_configuration(command(['systemctl','show',n,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode(),n)
  require(CONFIG_CONTRACT['same'](old['configuration'][n],value,exec_record));configuration[n]=value
 rows={};sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in old['rows']:
  require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
 sql+='commit;'
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],67108864).splitlines():
  v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
 require(rows==old['rows'] and len(rows)==24)
 durable={k:tree(pathlib.Path(os.path.commonpath(list(v)))) for k,v in old['durable'].items()}
 require(durable==old['durable'])
 require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))
 unitfiles={}
 for name,v in old['unitFiles'].items():
  p=pathlib.Path(name);m=metadata(p);h=hashlib.sha256(p.read_bytes()).hexdigest()
  require(m==v['metadata'] and h==v['sha256'] and m==metadata(p));unitfiles[name]=v
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126')
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==release)
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM)
 data=json.loads(manifest);require(data['source']['commit']==SOURCE and len(data['artifacts'])==187)
 command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(BASE/'pg2126-manifest.sig')],4096)
 for v in data['artifacts']:
  name=pathlib.PurePosixPath(v['path']);require(not name.is_absolute() and '..'not in name.parts)
  p=release/name;m=metadata(p)
  require(stat.S_ISREG(m[4]) and m[2]==0 and m[5]==1 and m[6]==v['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'] and m==metadata(p))
 peers=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"],4096)
 require(peers.splitlines()==[b'0',b'0'])
 for name in ['startup','pt-coverage','backup-request','cleanup-request','expiry-request','maintenance']:
  require(not os.path.lexists('/run/schubert-nk/'+name))
 return {'boot':boot,'source':SOURCE,'manifestSha256':BOM,'units':units,'configuration':configuration,'rows':rows,'durable':durable,'unitFiles':unitfiles}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for n in UNITS:manager.LoadUnit(n);manager.RefUnit(n);refs.append(n)
 first=observe();require(first==observe())
finally:
 for n in reversed(refs):manager.UnrefUnit(n)
 bus.close()
out=BASE/SLOT;out.mkdir(mode=0o700)
raw=json.dumps(first,sort_keys=True).encode()
with(out/'after.private.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'boot':boot,'source':SOURCE,'tables':24,'configurationFields':32,'signedArtifacts':187,'allDurableUnchanged':True,'newBootTenColdTwice':True,'metadataRefsClosed':True,'oldRunPermitNativeRestored':False,'businessStartStopWrites0':True,'oldOwnedStopAccepted':False,'formalAccepted':False,'privateAfterSha256':hashlib.sha256(raw).hexdigest()}))
'''
    code=prefix+body
    from pyflakes.api import check
    if check(code,'<actual outage cold readonly closure>'):raise ValueError('whole actual namespace required')
    compile(code,'<actual outage cold readonly closure>','exec');return code


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean observer required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);code=payload().encode()
    with(out/'observer.private.log').open('xb')as log:
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=code,stdout=log,stderr=log,timeout=90)
    value={'actualExit':result.returncode,'source':SOURCE,'payloadSha256':hashlib.sha256(code).hexdigest(),'formalAccepted':False}
    if not result.returncode:value.update(json.loads((out/'observer.private.log').read_bytes()))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
