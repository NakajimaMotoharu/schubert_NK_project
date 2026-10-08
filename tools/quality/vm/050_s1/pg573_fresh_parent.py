"""New one-shot ordinary parent campaign. Reuses immutable read-only libraries, no old run."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parent
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE = '969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
DIGEST = 'a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'
PAYLOAD = r'''
import ast,datetime,hashlib,importlib.util,json,os,pathlib,re,shutil,stat,subprocess,sys
os.umask(0o077)
def require(value):
 if not value:raise ValueError('fresh ordinary parent precondition refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
old=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/pg553_newrun_preflight.py')
require(hashlib.sha256(old.read_bytes()).hexdigest()=='e4cad29a26fb9592bc5cf6615fec79dc97ea6e73c05d8375a79b1767b7855423')
spec=importlib.util.spec_from_file_location('sealed_preflight_library',old);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
namespace={'__name__':'independent_cleanup_library'};exec(compile(ORACLE,'<independent SS cleanup selectors>','exec'),namespace)
guard={'__name__':'independent_prior_history_guard'};exec(compile(GUARD,'<fixed prior-history contract>','exec'),guard)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg573-fresh-parent-v1')
release=pathlib.Path('/opt/schubert-nk/current');raw=(release/'RELEASE-MANIFEST.json').read_bytes()
require(release.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG548')and hashlib.sha256(raw).hexdigest()==DIGEST and json.loads(raw)['source']['commit']==SOURCE)
def connection():
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 require(m.command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0'])
 for name in ('maintenance.lock','startup-admission.lock'):
  s=(pathlib.Path('/run/schubert-nk')/name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
def rows():
 q="begin isolation level repeatable read read only;set local timezone='UTC';"
 q+="select json_build_object('lower',now(),'upper',now()+interval '30 minutes','day',(now()at time zone 'Asia/Tokyo')::date);"
 for t in m.TABLES:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
 lines=m.command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines();require(len(lines)==25)
 result={}
 for line in lines[1:]:
  v=json.loads(line);require(v['table']not in result);result[v['table']]=v['rows']
 require(set(result)==set(m.TABLES));return json.loads(lines[0]),result
def capture():
 connection();units=m.stopped();bounds,data=rows()
 trees={k:m.tree(pathlib.Path(p))for k,p in [('backup','/srv/schubert-nk/backup'),('original','/var/lib/schubert-nk/maintenance'),('transfer','/srv/schubert-nk/data/transfer'),('startup','/run/schubert-nk/startup'),('native','/run/schubert-nk/pt-coverage')]}
 require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
 for name in ('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
 require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active')and not os.path.lexists('/var/lib/schubert-nk/maintenance/pending'))
 require(not any('intent' in n for n in trees['startup']))
 require(units==m.stopped());connection()
 return {'source':SOURCE,'manifestSha256':DIGEST,'bounds':bounds,'rows':data,'units':units,**trees}
def persist(name,value):
 with(root/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
if MODE=='prepare':
 require(not os.path.lexists(root));before=capture();again=capture();require(all(before[k]==again[k]for k in before if k!='bounds'))
 sealed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg570-bootstrap-existing-v1/after.private.json');proof=sealed.read_bytes()
 require(hashlib.sha256(proof).hexdigest()=='8cd3195cc3a326ba4a2a84ba2cd5abe6e931bcd2131c2609c29983e9c85bd164'and before['rows']==json.loads(proof)['rows'])
 require(len(before['rows']['schubert.batch_runs'])==472)
 require(guard['prior_history'](before['rows']['schubert.batch_runs'],before['bounds']['day']))
 retention=m.backup_upper_bound(pathlib.Path('/srv/schubert-nk/backup'))
 low=namespace['candidates'](before['rows'],before['bounds']['lower']);high=namespace['candidates'](before['rows'],before['bounds']['upper'])
 require(guard['empty_oracle'](low,high))
 root.mkdir(mode=0o700);persist('before.private.json',before);persist('cleanup-oracle.private.json',{'source':SOURCE,'manifestSha256':DIGEST,'expected':low,'sameThroughoutAdmissionWindow':True,'retention':retention,'originalBatchRows':472,'priorTodayRunPreserved':True})
 native=root/'native-before';shutil.copytree('/run/schubert-nk/pt-coverage',native,symlinks=False)
 for p in [native,*native.rglob('*')]:
  require(not p.is_symlink());os.chmod(p,0o700 if p.is_dir()else 0o600)
  if p.is_file():
   with p.open('rb')as f:os.fsync(f.fileno())
  else:
   fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 persist('prepared.private.json',{'beforeSha256':hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest(),'source':SOURCE,'starts0':True,'priorToday10Preserved':True})
 print(json.dumps({'actualExit':0,'prepared':True,'starts0':True,'beforeSha256':hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest(),'cleanupCandidates':0,'priorBatchRows':472,'backupEligibleUpperBound':retention['eligibleUpperBound']}))
else:
 require(MODE=='start'and root.is_dir()and not os.path.lexists(root/'external-start-guard.private.json'))
 before=json.loads((root/'before.private.json').read_bytes());prepared=json.loads((root/'prepared.private.json').read_bytes())
 require(prepared['beforeSha256']==hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest())
 current=capture();require(all(current[k]==before[k]for k in before if k!='bounds'))
 now=datetime.datetime.now(datetime.timezone.utc);require(datetime.datetime.fromisoformat(before['bounds']['lower'])<=now<=datetime.datetime.fromisoformat(before['bounds']['upper']))
 execstart=m.command(['systemctl','show','schubert-nk-morning-controller.service','--property=ExecStart']).decode();require('MorningProcessMain'in execstart and '--resume'not in execstart)
 persist('external-start-guard.private.json',{'at':now.isoformat(),'source':SOURCE,'ordinaryNoargs':True,'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
 r=subprocess.run(['systemctl','start','--no-block','schubert-nk-morning-controller.service'],capture_output=True,timeout=15)
 fields=m.command(['systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic']).decode();actual=dict(x.split('=',1)for x in fields.splitlines());actual.update(clientExit=r.returncode,clientSuccessIsNotParentSuccess=True)
 persist('external-start-issued.private.json',actual);print(json.dumps(actual));raise SystemExit(r.returncode)
'''


def main():
    os.umask(0o077)
    assert sys.argv[1:] in (['prepare'], ['start'])
    mode = sys.argv[1]
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R) == b''
    if mode == 'start':
        assert (W / 'pg573-prepare-v1.exit').read_bytes() == b'0\n'
        assert (W / 'pg574-observer-v1.started').exists() and not (W / 'pg574-observer-v1.exit').exists()
        first = json.loads((W / 'pg574-watch-private-v1.jsonl').open().readline())
        assert first == {'observerPrepared': True, 'source': SOURCE, 'manifestSha256': DIGEST, 'starts0': True}
    base = W / ('pg573-' + mode + '-v1')
    assert not any(os.path.lexists(str(base) + '.' + s) for s in ('private.log', 'exit', 'safe.json'))
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    prefix = 'MODE=' + repr(mode) + '\nSOURCE=' + repr(SOURCE) + '\nDIGEST=' + repr(DIGEST) + '\nORACLE=' + repr((R / 'pg478_cleanup_oracle.py').read_text()) + '\n'
    prefix += 'GUARD=' + repr((R / 'pg573_fresh_parent_contract.py').read_text()) + '\n'
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(ssh, input=(prefix + PAYLOAD).encode(), capture_output=True, timeout=90)
    with pathlib.Path(str(base) + '.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with pathlib.Path(str(base) + '.exit').open('x') as f: f.write(str(result.returncode) + '\n')
    if result.returncode == 0:
        value = json.loads(result.stdout)
        value.update(startedUTC=started, endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), operatorSource=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip())
        with pathlib.Path(str(base) + '.safe.json').open('x') as f: json.dump(value, f, sort_keys=True)
    print(json.dumps({'actualExit': result.returncode, 'mode': mode, 'privateLogSha256': hashlib.sha256(pathlib.Path(str(base) + '.private.log').read_bytes()).hexdigest(), 'clientSuccessIsNotParentSuccess': True}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
