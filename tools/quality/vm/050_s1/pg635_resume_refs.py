"""SSC228 new M/A/peer/ten-Ref failed30 pending code-only witness, no business actions."""
import ast
import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess
import sys
import time
import datetime
import dbus
from pg635_resume_contract import RUNTIME,NAME,TARGET,NATIVE,fixed_dropin,unit_sources,changed_only,require
from pg633_pending_contract import EPOCH,APPROVAL,same_value
OLD='/opt/schubert-nk/releases/0.1.0-PG631'

BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation')


def library():
    raw=(BASE/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    parsed=ast.parse(raw);wanted={'command','metadata','strict','show','tree','configuration_fields','kernel','owner'}
    defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in wanted]
    require(len(defs)==len(wanted))
    constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
    require(len(constants)==2)
    class Binding(ast.NodeTransformer):
        def visit_Constant(self,n):
            return ast.copy_location(ast.Constant(b'Pg635ResumePreparation'),n)if n.value==b'Pg480BackupRecovery'else n
    bound=Binding().visit(ast.Module(body=constants+defs,type_ignores=[]));ast.fix_missing_locations(bound)
    env={'pathlib':pathlib,'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'stat':stat,'subprocess':subprocess,'sys':sys,'time':time,'require':require}
    exec(compile(bound,'<pinned current namespace and owner>','exec'),env)
    return env


def main():
    require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='prepare'and sys.argv[2].isdigit())
    backend=int(sys.argv[2]);require(backend>1);os.umask(0o077)
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
    save=BASE/'pg635-resume-preparation-v1'
    env=library();command,show,tree,metadata,strict,kernel=(env[k]for k in('command','show','tree','metadata','strict','kernel'))
    held=env['owner']()
    def owner():require(env['owner']()==held)
    baseline_path=BASE/'pg633-pending-activate-v2/after.private.json';s=baseline_path.lstat()
    require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1))
    baseline_raw=baseline_path.read_bytes();require(s==baseline_path.lstat()and hashlib.sha256(baseline_raw).hexdigest()=='4d77bd92b7a7c3c85481b342659375e9be5fb7a50c0cd19f72363efb0f719879')
    baseline=json.loads(baseline_raw);require(len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==494)
    require(strict(pathlib.Path('/var/lib/schubert-nk/maintenance/active'),0o600,109)==b'NKACT1\ne49243d5-de84-4714-8612-6912ddc17e9e\n2026-10-08T18:32:42.140966Z\n7d381b67-b37b-48c6-99ac-e04a336f887d\n'and not os.path.lexists('/var/lib/schubert-nk/maintenance/pending'))
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    live=True
    def connection():
        conditions="a.usename='schubert_batch' and a.application_name='PG635-fixed-resume' and a.state='idle in transaction' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted)"if live else'true'
        sql="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.datname='schubert_nk' and "+conditions+";select count(*) from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in("+str(backend)+",pg_backend_pid());select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;"
        require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==([b'1',b'0',b'1']if live else[b'0',b'0',b'0']))
    paths=(save,pathlib.Path(EPOCH).parent,pathlib.Path(APPROVAL).parent,pathlib.Path(RUNTIME))
    fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)for p in paths]
    original=[os.fstat(fd)for fd in fds]
    def directories():
        def identity(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink)
        for p,fd,before in zip(paths,fds,original):
            require(identity(p.lstat())==identity(os.fstat(fd))==identity(before)and not {'system.posix_acl_access','system.posix_acl_default'}.intersection(os.listxattr(p)))
    def file(p):
        before=metadata(p);raw=p.read_bytes();require(before==metadata(p))
        return {'metadata':before,'sha256':hashlib.sha256(raw).hexdigest()}
    changed=False
    def snapshot():
        owner();directories();connection();require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
        require(not pathlib.Path('/proc/1511808').exists())
        value={}
        for key,path in {'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage','oldProofs':str(BASE/'pg611-native-stop-v1'),'bootstrapOldProofs':str(BASE/'pg570-bootstrap-existing-v1'),'bootstrapTools':str(BASE/'pg570-bootstrap-tools-v1')}.items():value[key]=tree(pathlib.Path(path))
        value['units']={u:show(u,env['FIELDS'])for u in env['UNITS']}
        value['configuration']={u:show(u,env['configuration_fields']())for u in env['UNITS']}
        for u,v in value['units'].items():require(v['MainPID']==v['ControlPID']=='0'and not v['Job']);kernel(u)
        require(same_value(value['units'],baseline['units']))
        if not changed:require(same_value(value['configuration'],baseline['configuration']))
        value['dependencies']={u:{k:sorted(v.split())for k,v in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()}for u in env['UNITS']}
        value['parentPid1']=baseline['parentPid1']
        receipt_raw=(pathlib.Path(__file__).parent/'pg629_failed_receipt.py').read_bytes()
        require(hashlib.sha256(receipt_raw).hexdigest()=='0b36b3310aa261ee80b2f0cf9831f4c99ba666116f2c4473135d5ac3b67db2de')
        receipt_source=receipt_raw.decode();receipt_env={'datetime':datetime}
        parsed=ast.parse(receipt_source);body=[n for n in parsed.body if isinstance(n,(ast.Assign,ast.FunctionDef))]
        exec(compile(ast.Module(body=body,type_ignores=[]),'<fixed genuine parent receipt>','exec'),receipt_env)
        journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=3a2de24f931544c0a2fd83556a659cd0','-o','json','--no-pager'])
        observed=[json.loads(l)for l in journal.splitlines()]
        require(receipt_env['failed30'](observed)['endMonotonicUs']==97094171993 and same_value(observed,baseline['parentPid1']))
        stopped={'caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'}
        require({p.name for p in (BASE/'pg611-native-stop-v1').glob('*.stopped.private')}=={u+'.stopped.private'for u in stopped})
        value['pid1Stop']={u:file(BASE/'pg611-native-stop-v1'/(u+'.stopped.private'))for u in sorted(stopped)}
        sql="begin isolation level repeatable read read only;set local timezone='UTC';"
        for table in baseline['rows']:
            require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',table)is not None)
            sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
        value['rows']={}
        for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;']).splitlines():
            row=json.loads(line);require(row['table']not in value['rows']);value['rows'][row['table']]=row['rows']
        require(same_value(value['rows'],baseline['rows']))
        names=[p.name for p in pathlib.Path(RUNTIME).iterdir()];require(set(names)==({NAME}if changed else set()))
        runtime_meta=metadata(pathlib.Path(RUNTIME));require(runtime_meta[2:6]==[0,0,stat.S_IFDIR|0o755,2])
        for name in('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
        value['runtime']=file(pathlib.Path(TARGET))if changed else None;value['current']=str(pathlib.Path('/opt/schubert-nk/current').readlink())
        value['approval']=file(pathlib.Path(APPROVAL))
        unit_files=[pathlib.Path(p)for p in unit_sources({u:show(u,{'FragmentPath','DropInPaths'})for u in env['UNITS']},changed)]
        value['unitFiles']={str(p):file(p)for p in unit_files}
        value['caddyPre']=show('caddy.service',{'ExecStartPre'})['ExecStartPre']
        require(value['units']=={u:show(u,env['FIELDS'])for u in env['UNITS']});owner();connection();directories()
        return value
    def persist(name,value):
        directories();fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fds[0])
        with os.fdopen(fd,'wb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
        os.fsync(fds[0])
    before=snapshot();require(same_value(before,snapshot())and before['current']==OLD)
    require(all(same_value(before[k],baseline[k])for k in('rows','units','configuration','startup','originals','backup')))
    require(same_value(before,baseline))
    base_path=pathlib.Path(OLD)/'systemd/schubert-nk-morning-controller.service';base_before=metadata(base_path)
    base_raw=base_path.read_bytes();require(base_before==metadata(base_path))
    native=strict(pathlib.Path(NATIVE),0o644,4096)
    dropin=fixed_dropin(base_raw,native)
    persist('before.private.json',before)
    print('REF_READY',flush=True);state='READY'
    for line in sys.stdin.buffer:
        action=line.rstrip(b'\n').decode('ascii')
        require(action in ({'before','prepare'}if state=='READY'else {'release'}))
        owner();directories()
        if action=='prepare':
            require(not changed and same_value(snapshot(),before))
            target=pathlib.Path(TARGET);require(not os.path.lexists(target))
            fd=os.open(NAME,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644,dir_fd=fds[3])
            with os.fdopen(fd,'wb')as f:os.fchmod(f.fileno(),0o644);f.write(dropin);f.flush();os.fsync(f.fileno())
            os.fsync(fds[3]);require(strict(target,0o644,4096)==dropin)
            command(['/usr/bin/systemctl','daemon-reload'],4096);changed=True;state='CHECKED'
        if action=='release':live=False
        now=snapshot()
        if not changed:require(same_value(now,before))
        else:changed_only(before,now,dropin);require(strict(pathlib.Path(TARGET),0o644,4096)==dropin)
        if action=='release':
            require(changed);persist('after.private.json',now)
            for u in reversed(refs):manager.UnrefUnit(u)
            bus.close()
            for fd in reversed(fds):os.close(fd)
            print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
    raise ValueError('current pending owner channel ended')


if __name__=='__main__':
    try:main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True);print('PG635_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if'pg635_'in frame.filename or 'pg604_unit_sources' in frame.filename:print('PG635_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
