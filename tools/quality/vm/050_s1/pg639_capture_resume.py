"""Read-only full-row/Backup same-run post capture under original parent budget."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD = r'''
import ast,datetime,hashlib,json,os,pathlib,re,stat,subprocess,time
os.umask(0o077)
def require(v):
 if not v:raise ValueError('current resume readonly capture refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');fresh=base/'pg637-fresh-resume-v2';root=base/'pg639-resume-post-v1'
raw=(fresh/'before.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='c946eaae7147aff0fb328bfabda0d779133f7c04cc30a9a0427d58ae7da76d2e');old=json.loads(raw)
issued=json.loads((fresh/'external-start-issued.private.json').read_bytes());require(issued['MainPID']=='1522744'and issued['InvocationID']=='293d218b06454bd1a8ff350bb93de2d5'and issued['Job']=='104329'and issued['ExecMainStartTimestampMonotonic']=='103062293730')
helper=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(helper).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
defs=[n for n in ast.parse(helper).body if isinstance(n,ast.FunctionDef)and n.name in ('command','metadata','tree','strict')];require(len(defs)==4);exec(compile(ast.Module(body=defs,type_ignores=[]),'<pinned readonly functions>','exec'),globals())
env={};exec(compile(ORACLE,'<independent fixed resume oracle>','exec'),env)
def parent():
 d=dict(l.split('=',1)for l in command(['systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,ControlPID,InvocationID,Job,Result,ExecMainStatus,ExecMainStartTimestampMonotonic']).decode().splitlines())
 require(d['ExecMainStartTimestampMonotonic']=='103062293730'and d['InvocationID']=='293d218b06454bd1a8ff350bb93de2d5')
 require(d['MainPID']=='1522744'and d['Job']=='104329'or d['MainPID']==d['ControlPID']=='0'and not d['Job']and d['Result']=='success'and d['ExecMainStatus']=='0')
 return d
def rows():
 q="begin isolation level repeatable read read only;set local timezone='UTC';"
 for t in old['rows']:
  require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
  q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
 data={}
 for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
  v=json.loads(line);require(v['table']not in data);data[v['table']]=v['rows']
 return data
require(not os.path.lexists(root));deadline=103062293730/1e6+1800
while time.monotonic()<deadline:
 p=parent();n=rows()
 if len(n['schubert.batch_runs'])==504 and all(r['status']=='SKIPPED'for r in n['schubert.batch_runs']if r['id']not in {s['id']for s in old['rows']['schubert.batch_runs']}):break
 require(len(n['schubert.batch_runs'])<=504);time.sleep(.5)
else:raise ValueError('original parent budget exhausted')
backup=tree(pathlib.Path('/srv/schubert-nk/backup'));summary=env['validate'](old['rows'],n,old['backup'],backup)
require(n==rows()and backup==tree(pathlib.Path('/srv/schubert-nk/backup')));parent()
release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG631'and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe')
root.mkdir(mode=0o700)
with(root/'full-rows.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump({'rows':n,'backup':backup,'parent':p,'summary':summary},f,sort_keys=True);f.flush();os.fsync(f.fileno())
for d in(root,root.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
summary.update(actualExit=0,productionSource='36fe7a0b938489d61d17d49c1c30a6fbbef699d5',run='PG639-resume-post-v1',snapshotSha256=hashlib.sha256((root/'full-rows.private.json').read_bytes()).hexdigest(),sameParentGeneration=True)
print(json.dumps(summary))
'''


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    assert (W/'pg637-start-v2.exit').read_bytes() == b'0\n'
    ssh = ['ssh', '-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    payload = 'ORACLE='+repr((R/'pg639_resume_oracle.py').read_text())+'\n'+PAYLOAD
    with (W/'pg639-post-v1.private.log').open('xb') as log:
        result = subprocess.run(ssh, input=payload.encode(), stdout=subprocess.PIPE, stderr=log)
        log.flush(); os.fsync(log.fileno())
    with (W/'pg639-post-v1.exit').open('x') as f: f.write(str(result.returncode)+'\n')
    if result.returncode == 0:
        safe = json.loads(result.stdout)
        safe['operatorSource'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        with (W/'pg639-post-v1.safe.json').open('x') as f: json.dump(safe, f, sort_keys=True)
        print(json.dumps(safe))
    else:
        print(json.dumps({'actualExit': result.returncode,
                          'privateLogSha256': hashlib.sha256((W/'pg639-post-v1.private.log').read_bytes()).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
