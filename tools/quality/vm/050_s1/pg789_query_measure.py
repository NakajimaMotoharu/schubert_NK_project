"""Read-only actual fixed Unit query cost; no acceptance or cause inferred from timing."""
import inspect
from pg784_stopped_baseline import main as prior_main

PAYLOAD=r'''
import pathlib,subprocess,time,json,os,hashlib,statistics
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG750')
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg789-query-measure-v1');assert not save.exists()
units=('schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','schubert-nk-cleanup.service')
fields=('Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup','Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic')
samples=[];started=time.monotonic_ns()
for _ in range(20):
 for unit in units:
  for field in fields:
   begin=time.monotonic_ns();r=subprocess.run(['/usr/bin/systemctl','--system','--no-pager','--no-ask-password','show','--property='+field,unit],capture_output=True,timeout=5)
   elapsed=time.monotonic_ns()-begin;assert r.returncode==0 and len(r.stdout)<=4096 and not r.stderr
   assert b'Id='+unit.encode()+b'\n'in r.stdout
   samples.append({'unit':unit,'fieldCount':len(field.split(',')),'nanoseconds':elapsed})
total=time.monotonic_ns()-started;value={'commands':len(samples),'samples':samples,'totalNanoseconds':total,'medianNanoseconds':int(statistics.median(x['nanoseconds']for x in samples))}
save.mkdir(mode=0o700)
with(save/'measurement.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'commands':len(samples),'elapsedSeconds':total/1e9,'medianMilliseconds':value['medianNanoseconds']/1e6,'notProvenCause':True,'productionPTAdded':0,'snapshotSha256':hashlib.sha256((save/'measurement.private.json').read_bytes()).hexdigest()}))
'''


if __name__=='__main__':
    import pg784_stopped_baseline as previous
    raw=inspect.getsource(prior_main).replace('pg784-stopped-current-v1','pg789-query-measure-v1')
    context={**previous.__dict__,'PAYLOAD':PAYLOAD}
    exec(compile(raw,'<new789 readonly cost measurement>','exec'),context);context['main']()
