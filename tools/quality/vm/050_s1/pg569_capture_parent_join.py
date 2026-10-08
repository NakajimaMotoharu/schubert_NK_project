"""Readonly actual sealed PID1/NKDONE1 join; no ownership or business action."""
import hashlib,json,os,pathlib,subprocess,sys
os.umask(0o077)
R=pathlib.Path(__file__).parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
payload=r'''import hashlib,json,os,pathlib,sys
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg566-bootstrap-tools-v1')
helper=pathlib.Path(sys.path[0],'pg556_parent_receipt.py');assert hashlib.sha256(helper.read_bytes()).hexdigest()=='726d0a3197505429cdabfc25be7a2d436c5af676805aeb9ab0f94855d436e16d'
env={};exec(compile(JOIN_SRC,'<independent strict typed join>','exec'),env)
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg559-terminal-readback-v2/after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677'
expected=json.loads(raw)['parentPid1'];journal=b''.join(json.dumps(row).encode()+b'\n'for row in expected)
done=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/12f1af04-180e-405c-8738-853bbd875443.done').read_bytes()
rows,receipt=env['completed_journal'](journal,done);assert rows==expected and receipt['endMonotonicUs']==46382089521
for bad in (expected,None,b'',b'[]\n',journal+journal):
 try:env['completed_journal'](bad,done)
 except ValueError:pass
 else:raise AssertionError('actual typed negative unexpectedly admitted')
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg569-parent-join-v1');assert not save.exists();save.mkdir(mode=0o700)
safe={'actualExit':0,'actualSealedParentRowsJoin':True,'negativeRejected':5,'originalsWritten':False,'businessActions':0,'rawExported':False,'joinSourceSha256':hashlib.sha256(JOIN_SRC.encode()).hexdigest(),'formalAccepted':False}
with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);print(json.dumps(safe,sort_keys=True))
'''
log=W/'pg569-parent-join-v1.private.log';receipt=W/'pg569-parent-join-v1.safe.json';code=W/'pg569-parent-join-v1.exit';assert not any(p.exists()for p in(log,receipt,code))
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
with log.open('xb')as f:
 run=subprocess.run(ssh,input=('JOIN_SRC='+repr((R/'pg569_parent_join.py').read_text())+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=f);f.flush();os.fsync(f.fileno())
with code.open('x')as f:f.write(str(run.returncode)+'\n');f.flush();os.fsync(f.fileno())
if run.returncode==0:
 safe=json.loads(run.stdout)
 with receipt.open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':run.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'rawExported':False}));sys.exit(run.returncode)
