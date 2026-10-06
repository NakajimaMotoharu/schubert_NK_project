"""PT-OPS-PG487004/BUG788: read-only failure capture, no ownership inference/repair/start."""
import os,pathlib,subprocess,json,hashlib
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
payload=r'''import ast,pathlib,os,json,hashlib,stat,subprocess,shutil
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG486')
saved=pathlib.Path('/var/lib/pgpt-s1-preservation/pg486-completed-codeonly/after.private.json');assert hashlib.sha256(saved.read_bytes()).hexdigest()=='a189a4b029d9a2d66b6767aa86bd85c63879438d84b99b5a86b36ac3093d4ba5'
baseline=json.loads(saved.read_text());raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
def require(v):
 if not v:raise ValueError('readonly capture refused')
nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in {'metadata','tree'}];assert len(nodes)==2;exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pinned preservation primitives>','exec'),globals())
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg487-parent-failure-v1');assert not save.exists()
units={}
for u in baseline['units']:
 raw=subprocess.check_output(['/usr/bin/systemctl','show',u,'--property=Id,MainPID,ControlPID,InvocationID,ActiveState,SubState,Job,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic'],text=True,timeout=5);units[u]=dict(l.split('=',1) for l in raw.splitlines())
parent=units['schubert-nk-morning-controller.service'];assert parent['InvocationID']=='86142754043b476aa46e33916eb1b1a1' and parent['MainPID']==parent['ControlPID']=='0' and parent['Job']=='' and parent['ExecMainCode']=='1' and parent['ExecMainStatus']=='30' and parent['Result']=='exit-code'
q="begin isolation level repeatable read read only;set local timezone='UTC';"
for t in baseline['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
q+='commit;';rows={}
for line in subprocess.check_output(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],timeout=30).splitlines():
 v=json.loads(line);assert v['table'] not in rows;rows[v['table']]=v['rows']
assert len(rows)==24 and all(all(r in rows[t] for r in old) for t,old in baseline['rows'].items())
trees={root:tree(pathlib.Path(root)) for root in baseline['trees']}
assert trees=={root:tree(pathlib.Path(root)) for root in baseline['trees']}
save.mkdir(mode=0o700)
def write(name,raw):
 with (save/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
write('snapshot.private.json',json.dumps({'units':units,'trees':trees,'rows':rows},sort_keys=True).encode())
native=save/'native-private';native.mkdir(mode=0o700)
for name,v in trees['/run/schubert-nk/pt-coverage'].items():
 if v['sha256'] is None:continue
 p=pathlib.Path(name);target=native/p.relative_to('/run/schubert-nk/pt-coverage');target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with p.open('rb') as inp,target.open('xb') as out:os.fchmod(out.fileno(),0o600);shutil.copyfileobj(inp,out);out.flush();os.fsync(out.fileno())
 assert hashlib.sha256(target.read_bytes()).hexdigest()==v['sha256']
for u in ['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service']:
 raw=subprocess.check_output(['/usr/bin/journalctl','--boot=e07aa7061acd4e65b309d7f330f79d54','--since=2026-10-06 12:06:12 UTC','--until=2026-10-06 12:09:00 UTC','--unit='+u,'-o','json','--no-pager'],timeout=15);assert len(raw)<=4194304;write(u+'.journal.private.jsonl',raw)
for d in [p for p in native.rglob('*') if p.is_dir()]+[native,save,save.parent]:
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({'failureCapture':True,'parentExit':30,'old423AllRowsRetained':True,'other23TablesSame':all(rows[t]==v for t,v in baseline['rows'].items() if t!='schubert.batch_runs'),'batchRows':len(rows['schubert.batch_runs']),'snapshotSha256':hashlib.sha256((save/'snapshot.private.json').read_bytes()).hexdigest(),'captureIsNotNormalScopeReceipt':True,'starts0':True,'repairs0':True,'rawExported':False}))
'''
r=subprocess.run(SSH+['sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg487-failure-capture-v1.private.log').open('xb') as f:f.write(r.stdout);f.write(r.stderr)
with (W/'pg487-failure-capture-v1.exit').open('x') as f:f.write(str(r.returncode)+'\n')
if r.returncode==0:print(r.stdout.decode(),end='')
else:print('PG487_FAILURE_CAPTURE_REFUSED actual='+str(r.returncode)+' logsPrivate=true')
raise SystemExit(r.returncode)
