"""Bounded readonly mid-run original/same-day DB projection, not parent completion."""
import hashlib
import json
import os
import pathlib
import subprocess

R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import datetime,hashlib,json,os,pathlib,re,stat,subprocess
os.umask(0o077)
def require(value):
 if not value:raise ValueError('independent same-day readonly projection refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg573-fresh-parent-v2');raw=(root/'before.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='557ae9688c03162fe1962cd81d93eb9e4a70eb9acca998a02040afb96f0ec505');before=json.loads(raw)
issued=json.loads((root/'external-start-issued.private.json').read_bytes())
def parent():
 fields='MainPID,InvocationID,ExecMainStartTimestampMonotonic,Job,ControlPID'
 v=dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show','schubert-nk-morning-controller.service','--property='+fields],text=True).splitlines())
 require(v['MainPID']==issued['MainPID']=='909808'and v['InvocationID']==issued['InvocationID']=='267003d6e12845dd8690cd9bd5afcad0'and v['ExecMainStartTimestampMonotonic']==issued['ExecMainStartTimestampMonotonic']);return v
def strict(p):
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(p))
 raw=p.read_bytes();require(len(raw)==72 and p.lstat()==s);return raw
anchor=pathlib.Path('/var/lib/schubert-nk/maintenance/runs/b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e.run');new=strict(anchor)
require(re.fullmatch(rb'NKRUN1\nb62b6984-ffc2-4c9d-aea9-e232d9d1ec9e\n[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z\n',new)is not None)
cutoff=new.decode('ascii').splitlines()[2];c=datetime.datetime.fromisoformat(cutoff.replace('Z','+00:00'))
require(datetime.datetime.fromisoformat(before['bounds']['lower'])<=c<=datetime.datetime.fromisoformat(before['bounds']['upper']))
oldAnchor=pathlib.Path('/var/lib/schubert-nk/maintenance/runs/b7e73994-b951-4696-bdd1-cfbc8a10e734.run')
require(hashlib.sha256(strict(oldAnchor)).hexdigest()==before['original'][str(oldAnchor)]['sha256'])
oracle={'__name__':'independent_same_day_oracle'};exec(compile(ORACLE,'<SS331 same-day literal>','exec'),oracle)
def snapshot():
 q="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in before['rows']:
  require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',table)is not None)
  q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
 r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;'],capture_output=True,timeout=30);require(r.returncode==0 and not r.stderr)
 data={}
 for line in r.stdout.splitlines():
  v=json.loads(line);require(v['table']not in data);data[v['table']]=v['rows']
 require(set(data)==set(before['rows'])and all(data[t]==v for t,v in before['rows'].items()if t!='schubert.batch_runs'))
 return data
actor=parent();a=snapshot();result=oracle['verify'](before['rows']['schubert.batch_runs'],a['schubert.batch_runs'],cutoff)
require(a==snapshot()and actor==parent()and new==strict(anchor))
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg577-same-day-projection-v1');require(not os.path.lexists(save));save.mkdir(mode=0o700)
with(save/'full-rows.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(a,f,sort_keys=True);f.flush();os.fsync(f.fileno())
result.update(actualExit=0,run='PG577-same-day-projection-v1',productionSource=before['source'],unchangedNonBatchTables=23,expired115SessionsPreserved=True,currentAnchorCutoffBoundedAndOldAnchorUnchanged=True,readonlySnapshots=2,parentWholeAccepted=False,fullRowsSha256=hashlib.sha256((save/'full-rows.private.json').read_bytes()).hexdigest(),rawValuesExported=False)
with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps(result))
'''


def main():
    os.umask(0o077)
    assert not os.path.lexists(W/'pg577-same-day-projection-v1.private.log')
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    result=subprocess.run(ssh,input=('ORACLE='+repr((R/'pg577_same_day_oracle.py').read_text())+'\n'+PAYLOAD).encode(),capture_output=True,timeout=75)
    with(W/'pg577-same-day-projection-v1.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with(W/'pg577-same-day-projection-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout)
        with(W/'pg577-same-day-projection-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps({'actualExit':result.returncode,'parentWholeAccepted':False,'privateLogSha256':hashlib.sha256((W/'pg577-same-day-projection-v1.private.log').read_bytes()).hexdigest()}));raise SystemExit(result.returncode)


if __name__=='__main__':main()
