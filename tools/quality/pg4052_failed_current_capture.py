"""BUG1332: failed-parent preservation only; live ordinary pools are not cold-zero."""
import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path
from lan_server import run
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg3428_vm_candidate_preflight_readonly as identity
from pg4002_literal_invariant_publication_sources import SOURCE, BOM

SLOT = 'pg4052-failed-current-capture-v1'


def payload():
    initial = identity.GUEST[:identity.GUEST.index('units={}')]
    for old, new in [('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25', SOURCE),
                     ('37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863', BOM),
                     ('PG2802', 'PG3976'), ('pg2802-manifest.sig', 'pg3976-manifest.sig')]:
        initial = initial.replace(old, new)
    old = (W / 'pg3476-outbox-current-full-seal-v1/payload.private.py').read_text()
    helpers = '\n'.join(ast.get_source_segment(old, n) for n in ast.parse(old).body
                        if isinstance(n, ast.FunctionDef) and n.name in {'metadata', 'tree'})
    return initial + '\nimport stat,re\n' + helpers + '\n' + BODY


BODY = r'''
def require(value):
 if not value:raise ValueError('failed-current read-only authentication refused')
base=Path('/var/lib/pgpt-s1-preservation');save=base/'pg4052-failed-current-capture-v1';require(not os.path.lexists(save));os.umask(0o077);save.mkdir(mode=0o700)
oldraw=(base/'pg4008-literal-invariant-publication-independent-post-v1/after.private.json').read_bytes();require(hashlib.sha256(oldraw).hexdigest()=='33b24b767326879adff27c1ee38aaa08102e347d04d631947047ef667f3352c6');old=json.loads(oldraw)
fields='Id,LoadState,ActiveState,SubState,MainPID,ControlPID,Job,InvocationID,ControlGroup,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic'
expected_inv={'schubert-nk-api.service':'c9444dbf2e6a43dca0d52ab220d59b1d','schubert-nk-web.service':'af0eb750d72443739bead6a879a51e13','caddy.service':'a0c7fb91c4da42f09faec0f065a87767','artemis.service':'9cb091b80682402aaed1d2d1d2d2a5d7'}
def command(args,bound=67108864):
 r=subprocess.run(args,capture_output=True,timeout=45);require(r.returncode==0 and len(r.stdout)<=bound);return r.stdout
def units():
 result={};actors={}
 for name in old['units']:
  v=dict(l.split('=',1)for l in command(['systemctl','show',name,'--property='+fields],65536).decode().splitlines());result[name]=v
  if name in expected_inv:require(v['InvocationID']==expected_inv[name] and v['ActiveState']=='active' and v['SubState']=='running')
  if int(v['MainPID'])>1:
   p=Path('/proc')/v['MainPID'];ticks=int((p/'stat').read_text().rsplit(')',1)[1].split()[19]);argv=hashlib.sha256((p/'cmdline').read_bytes()).hexdigest();actors[name]={'pid':int(v['MainPID']),'ticks':ticks,'argvSha256':argv,'exe':str((p/'exe').readlink()),'cgroup':(p/'cgroup').read_text()}
 m=result['schubert-nk-morning-controller.service'];require(m['InvocationID']=='820851b8291a4c958bb34f6c48430ca3' and m['Result']=='timeout' and m['ExecMainStatus']=='143' and m['ExecMainCode']=='1' and m['MainPID']==m['ControlPID']=='0' and m['Job']=='')
 return result,actors
sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='10s';"
for table in old['rows']:
 require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None);sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
sql+="select json_build_object('peers',coalesce(jsonb_agg(jsonb_build_object('pid',pid,'user',usename,'application',application_name,'address',client_addr,'port',client_port,'state',state,'backendStart',backend_start)order by pid),'[]'::jsonb))from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select json_build_object('locks',coalesce(jsonb_agg(to_jsonb(t)order by pid),'[]'::jsonb))from(select pid,classid,objid,objsubid,mode,granted from pg_locks where locktype='advisory')t;commit;"
def database():
 rows={};meta={}
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
  value=json.loads(line)
  if 'table'in value:require(value['table']not in rows);rows[value['table']]=value['rows']
  else:meta.update(value)
 require(len(rows)==24);return {'rows':rows,**meta}
def durable():
 return {'originals':tree(Path('/var/lib/schubert-nk/maintenance')),'backup':tree(Path(os.path.commonpath(list(old['backup'])))),**{k:tree(Path(os.path.commonpath(list(v))))for k,v in old['extraDurable'].items()}}
def snapshot():
 u,a=units();d=database();locks=[]
 for name in ['maintenance.lock','startup-admission.lock']:
  p=Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}';locks += [l for l in Path('/proc/locks').read_text().splitlines()if len(l.split())>=8 and l.split()[5]==key]
 return {'units':u,'actors':a,'database':d,'flocks':locks,'durable':durable(),'native':tree(Path('/run/schubert-nk/pt-coverage')),'startup':tree(Path('/run/schubert-nk/startup')),'runtime':tree(Path('/run/systemd/system'))}
import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 first=snapshot();second=snapshot();require(first['units']==second['units'] and first['actors']==second['actors'])
finally:
 try:
  for unit in reversed(refs):manager.UnrefUnit(unit)
 finally:bus.close()
done=Path('/var/lib/schubert-nk/maintenance/attempts/d9d58371-bf80-49f6-bad9-3d1e0916fb04.done');done_sha=hashlib.sha256(done.read_bytes()).hexdigest();require(done_sha=='ca7829dbf4f1f215bc9bc6c60dd02c94137e2157a665ee57905b3c2aa5f0d090')
for filename,expected in old['unitFilesActual'].items():
 p=Path(filename);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==expected)
require(manifest.read_bytes()==raw and current.resolve(strict=True)==root and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
private={'first':first,'second':second,'source':data['source']['commit'],'BOM':sha,'boot':boot,'doneSha256':done_sha};encoded=json.dumps(private,sort_keys=True).encode()
with(save/'observed.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateSha256':hashlib.sha256(encoded).hexdigest(),'parentFailed143':True,'done10NotParentSuccess':True,'whole187SignatureVerified':True,'sameActorsTwice':True,'actorCount':len(first['actors']),'all24ReadTwice':True,'all24EqualTwice':first['database']['rows']==second['database']['rows'],'dbPeerCounts':[len(v['database']['peers'])for v in [first,second]],'advisoryCounts':[len(v['database']['locks'])for v in [first,second]],'flockCounts':[len(v['flocks'])for v in [first,second]],'durableEqualTwice':first['durable']==second['durable'],'nativeStableDuringCapture':first['native']==second['native'],'nativeExecCount':sum(Path(p).suffix=='.exec'for p in second['native']),'metadataRefsClosed':len(refs)==10,'signalStartStopReloadDbWrites':0,'authorityIssued':False,'formalAccepted':False}
(save/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result))
'''


def main():
    os.umask(0o077); out = W / SLOT; out.mkdir()
    p = Path('/proc/20445'); forward = {'ticks': int((p / 'stat').read_text().rsplit(')', 1)[1].split()[19]), 'argvSha256': hashlib.sha256((p / 'cmdline').read_bytes()).hexdigest()}
    assert forward == {'ticks': 104194, 'argvSha256': 'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}
    code, text = run(identity.HOST, timeout=30); assert code == 0
    host = json.loads(text.strip()); raw = payload(); compile(raw, '<failed-parent live-pool capture>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=200)
    (out / 'stdout.safe.json').write_bytes(r.stdout); (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'source': SOURCE, 'host': host, 'localForward': forward, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if r.returncode == 0: value['result'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
