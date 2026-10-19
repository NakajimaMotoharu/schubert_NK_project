"""BUG1470 original failedRoot/API private journals and current ownership; never restart/stop."""
import pg5644_current_admission_image as admission

SLOT='pg5696-failed-root-readonly-v1'


def payload(binding):
    return 'BINDING='+repr(binding)+'\nSOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\nSLOT='+repr(SLOT)+r'''
import datetime,hashlib,json,os,pathlib,re,subprocess
def require(value):
 if value is not True:raise ValueError('original failedRoot ownership read refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==BINDING['boot'])
mr=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(mr).hexdigest()==BOM and json.loads(mr)['source']['commit']==SOURCE)
out=pathlib.Path('/var/lib/pgpt-s1-preservation')/SLOT;os.umask(0o077);out.mkdir(mode=0o700)
def preserve(name,raw):
 with(out/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def command(name,args,timeout):
 r=subprocess.run(args,capture_output=True,timeout=timeout)
 preserve(name+'-stdout.private',r.stdout);preserve(name+'-stderr.private',r.stderr)
 preserve(name+'-exit.private.json',json.dumps({'actualExit':r.returncode}).encode());require(r.returncode==0)
 return r.stdout
names=['schubert-nk-morning-controller.service','schubert-nk-backup.service','artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service']
units={};kernel={}
for i,name in enumerate(names):
 raw=command('unit-'+str(i),['systemctl','show',name,'--property=MainPID,ControlPID,Job,ActiveState,SubState,InvocationID,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,ExecMainStatus,Result'],10)
 units[name]=dict(s.split('=',1)for s in raw.decode().splitlines())
 group=pathlib.Path('/sys/fs/cgroup/system.slice')/name
 values={}
 if group.exists():
  for p in [group,*[d for d in group.rglob('*')if d.is_dir()]]:values[str(p)]=(p/'cgroup.procs').read_text()
 preserve('kernel-'+str(i)+'.private.json',json.dumps(values,sort_keys=True).encode());kernel[name]=sum(len(v.split())for v in values.values())
root=units[names[0]];require(root['InvocationID']==BINDING['invocation']and root['ExecMainStartTimestampMonotonic']==str(BINDING['start'])and root['MainPID']=='0'and root['ControlPID']=='0'and root['Job']==''and root['ExecMainStatus']=='30')
api=units['schubert-nk-api.service'];require(api['InvocationID']=='4bf2830c7f7f4a56b6168c8b6f815a39')
summaries={}
for role,invocation in [('root',root['InvocationID']),('api',api['InvocationID'])]:
 raw=command(role+'-journal',['journalctl','--no-pager','-o','json','_SYSTEMD_INVOCATION_ID='+invocation],30)
 rows=[json.loads(line)for line in raw.splitlines()];preserve(role+'-journal-count.private.json',json.dumps({'rows':len(rows)}).encode())
 messages=[r.get('MESSAGE','')for r in rows if type(r.get('MESSAGE'))is str]
 classes=sorted({m.group(1)for text in messages for m in re.finditer(r'(?<![\w$])([A-Za-z_$][\w.$]*(?:Exception|Error))(?=:|\s|$)',text)})
 frames=sorted({m.group(0).strip()for text in messages for m in re.finditer(r'(?m)^\s*at (?:dev\.codex\.schubert\.nk|java|jdk|org\.springframework)[\w.$/]+\([A-Za-z0-9_$. :]+\)',text)})
 schemas=set()
 for text in messages:
  if text.startswith('{')and text.endswith('}'):
   try:value=json.loads(text)
   except json.JSONDecodeError:continue
   if type(value)is dict:schemas.add(','.join(sorted(value)))
 summaries[role]={'journalRows':len(rows),'rawSha256':hashlib.sha256(raw).hexdigest(),'exceptionClasses':classes,'stackFrames':frames,'messageSchemas':sorted(schemas)}
records={};maintenance=pathlib.Path('/var/lib/schubert-nk/maintenance')
for directory,ident in [('attempts',BINDING['activation']),('runs',BINDING['run'])]:
 for p in sorted((maintenance/directory).glob(ident+'*')):
  require(p.is_file()and not p.is_symlink());raw=p.read_bytes();preserve('record-'+p.name+'.private',raw)
  header=raw.splitlines()[0].decode('ascii',errors='replace')if raw.splitlines()else''
  records[directory+'/'+p.name]={'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'header':header if re.fullmatch(r'NK[A-Z0-9_]{1,20}',header)else'NOT_PUBLIC_HEADER'}
sql="begin isolation level repeatable read read only;set local statement_timeout='5s';select json_build_object('clients',(select count(*)from pg_stat_activity where datname='schubert_nk'and pid<>pg_backend_pid()),'advisoryLocks',(select count(*)from pg_locks where locktype='advisory'and database=(select oid from pg_database where datname='schubert_nk')));commit;"
# psql input is kept off command-line; no credentials or row data leave private capture.
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=15)
preserve('db-count-stdout.private',r.stdout);preserve('db-count-stderr.private',r.stderr);require(r.returncode==0);db=json.loads(r.stdout)
command('locks',['lslocks','-J','-o','PID,COMMAND,TYPE,MODE,PATH'],15)
preserve('current-summary.private.json',json.dumps({'units':units,'kernelCounts':kernel,'records':records,'dbCounts':db,'journalSummary':summaries},sort_keys=True).encode())
require(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()==mr)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':SOURCE,'BOM':BOM,'units':units,'kernelProcessCounts':kernel,'maintenanceRecords':records,'dbCounts':db,'journalSummary':summaries,'newLifecycleActions':0,'dbWrites':0,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(admission.live()),240))
