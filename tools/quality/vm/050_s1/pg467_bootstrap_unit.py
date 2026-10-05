"""PG467/BOOT007 fixed initial ADMIN one-shot; private observer precedes one nonblocking start.
No secret output; all actual manager/kernel/SQL data remains root-private.
"""
import hashlib,json,os,pathlib,subprocess,sys,time
import dbus
from pg457_stable_actor import stable_actor,ENTRIES
ENTRY='dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain';ENTRIES.add(ENTRY)
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg467-bootstrap-existing-ref')
UNIT='schubert-nk-bootstrap-admin.service'
FIELDS='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
def require(b):
    if not b:raise ValueError('fixed bootstrap Unit refused')
def save(name,data):
    with (ROOT/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
def show():
    raw=subprocess.check_output(['/usr/bin/systemctl','show',UNIT,'--property='+FIELDS],timeout=5).decode('ascii');values={}
    for line in raw.splitlines():
        k,v=line.split('=',1);require(k not in values);values[k]=v
    require(set(values)==set(FIELDS.split(',')));return values
def sql(query):return subprocess.check_output(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c',query],timeout=5).strip()
require(os.geteuid()==0 and sys.argv[1:]==['existing'] and not ROOT.exists())
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54')
current=pathlib.Path('/opt/schubert-nk/current');require(current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG465'))
require(hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e')
require((current/'systemd'/UNIT).read_bytes()==pathlib.Path('/etc/systemd/system',UNIT).read_bytes())
before=show();require(before['LoadState']=='loaded' and before['ActiveState']=='inactive' and before['MainPID']==before['ControlPID']=='0' and not before['Job'])
require(sql('select count(*) from schubert.app_users')==b'1' and (pathlib.Path('/var/lib/pgpt-s1-preservation/pg467-bootstrap')/'start-reserved.private').exists())
digest_sql="select md5(coalesce(string_agg(row_to_json(t)::text, E'\\n' order by id),'')) from schubert.app_users t union all select md5(coalesce(string_agg(row_to_json(t)::text, E'\\n' order by id),'')) from schubert.app_logs t"
prior_db=sql(digest_sql)
ROOT.mkdir(mode=0o700);save('before.private.json',json.dumps(before,sort_keys=True).encode());save('database-before-digest.private',prior_db);save('start-reserved.private',b'oneExistingOnlyStart=true\n')
parent_fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY);os.fsync(parent_fd);os.close(parent_fd)
# Same live D-Bus sender retains only observation metadata, not runtime/DB authority.
# No Unit property/directive/reset is changed. Process disconnect also releases the reference.
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');manager.RefUnit(UNIT)
result=subprocess.run(['/usr/bin/systemctl','start','--no-block',UNIT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5);require(result.returncode==0)
deadline=time.monotonic()+35;actor=None;generation=None;states=[]
while time.monotonic()<deadline:
    state=stable_actor('bootstrap',lambda role:show());states.append(state)
    if state.get('race'):time.sleep(.01);continue
    if state['InvocationID']:
        if generation is None:generation=state['InvocationID']
        require(generation==state['InvocationID'])
    if int(state['MainPID']) and state.get('entry')==ENTRY and actor is None:
        proc=pathlib.Path('/proc')/state['MainPID']
        try:
            status={k:v.strip() for k,v in (line.split(':',1) for line in (proc/'status').read_text().splitlines())}
            uid=subprocess.check_output(['id','-u','schubert-api'],text=True).strip();gid=subprocess.check_output(['id','-g','schubert-api'],text=True).strip();groups=sorted(set(subprocess.check_output(['id','-G','schubert-api'],text=True).split()),key=int)
            tick=(proc/'stat').read_text().rpartition(')')[2].split()[19];cgroup=(proc/'cgroup').read_text();args=(proc/'cmdline').read_bytes()
            require(status['Uid'].split()==[uid]*4 and status['Gid'].split()==[gid]*4 and sorted(set(status['Groups'].split()),key=int)==groups and status['NoNewPrivs']=='1' and all(int(status[k],16)==0 for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')) and cgroup=='0::/system.slice/'+UNIT+'\n' and b'dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain\0' in args)
            require(show()['MainPID']==state['MainPID'] and show()['InvocationID']==generation)
            actor={'pid':state['MainPID'],'startTicks':tick,'invocation':generation,'ordinaryZeroCapabilities':True,'sameUnitCgroup':True};save('actor.private.json',json.dumps(actor,sort_keys=True).encode())
        except FileNotFoundError:pass
    if generation and state['MainPID']==state['ControlPID']=='0' and not state['Job'] and state['ActiveState'] in ('inactive','failed'):break
    time.sleep(.01)
save('states.private.json',json.dumps(states,sort_keys=True).encode());require(actor is not None)
require(state['ActiveState']=='inactive' and state['Result']=='success' and state['ExecMainCode']=='1' and state['ExecMainStatus']=='20' and state['InvocationID']==generation and int(state['ExecMainExitTimestampMonotonic'])>=int(state['ExecMainStartTimestampMonotonic'])>0)
require(not pathlib.Path('/proc',actor['pid']).exists())
cg=pathlib.Path('/sys/fs/cgroup/system.slice')/UNIT
if cg.exists():
    for p in [cg,*[x for x in cg.rglob('*') if x.is_dir()]]:require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
require(sql("select count(*) from schubert.app_users where username='pgpt_admin_467' and role='ADMIN' and status='ACTIVE' and version=0 and created_by is null and updated_by is null and created_at=updated_at and password_changed_at=created_at")==b'1')
require(sql('select count(*) from schubert.app_users')==b'1')
require(sql(digest_sql)==prior_db)
require(sql("select count(*) from schubert.app_logs where service='API' and action='USER_CREATED' and message='USER_CREATED' and category in ('ACTION','SECURITY') and actor_user_id is null and details->>'source'='BOOTSTRAP' and details->>'outcome'='SUCCESS' and details->>'targetUserId'=(select id::text from schubert.app_users where username='pgpt_admin_467')")==b'2')
raw=subprocess.check_output(['/usr/bin/journalctl','_SYSTEMD_INVOCATION_ID='+generation,'-o','json','--no-pager'],timeout=5);require(len(raw)<=4194304);save('full-journal.private.jsonl',raw)
rows=[json.loads(line) for line in raw.decode('utf-8').splitlines()];messages=[r.get('MESSAGE') for r in rows];require(messages.count('Initial ADMIN bootstrap finished')==1 and 'Initial ADMIN bootstrap failed' not in messages)
manager.UnrefUnit(UNIT);bus.close()
save('complete.private',b'normalOwnedReturnAndExit20=true\nexistingAdmin1=true\nuserAndLogsUnchanged=true\nordinarySameActor=true\nobservationReferenceReleased=true\noldCloseUnknown=true\n')
print('PG467_BOOTSTRAP_EXISTING_ACCEPTED actualExit20=true ordinarySameActor=true kernelEmpty=true admin1=true userAndLogsUnchanged=true audit2=true oldCloseNotInferred=true secretsPrinted=false')
