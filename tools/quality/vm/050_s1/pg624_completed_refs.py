"""SSC227 new M/A/peer/ten-Ref completed code-only witness, no business actions."""
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
from pg624_completed_contract import OLD,NEXT,EPOCH,APPROVAL,NEW_APPROVAL,changed_only,phase_action,require,same_value
from pg604_unit_sources import sources

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
            return ast.copy_location(ast.Constant(b'Pg624CompletedDeployment'),n)if n.value==b'Pg480BackupRecovery'else n
    bound=Binding().visit(ast.Module(body=constants+defs,type_ignores=[]));ast.fix_missing_locations(bound)
    env={'pathlib':pathlib,'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'stat':stat,'subprocess':subprocess,'sys':sys,'time':time,'require':require}
    exec(compile(bound,'<pinned current namespace and owner>','exec'),env)
    return env


def main():
    require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]in('verify','activate')and sys.argv[2].isdigit())
    mode=sys.argv[1];backend=int(sys.argv[2]);require(backend>1);os.umask(0o077)
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
    save=BASE/('pg624-completed-'+mode+'-v1')
    env=library();command,show,tree,metadata,strict,kernel=(env[k]for k in('command','show','tree','metadata','strict','kernel'))
    held=env['owner']()
    def owner():require(env['owner']()==held)
    baseline_path=BASE/'pg611-native-stop-v1/after.private.json';s=baseline_path.lstat()
    require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1))
    baseline_raw=baseline_path.read_bytes();require(s==baseline_path.lstat()and hashlib.sha256(baseline_raw).hexdigest()=='a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849')
    baseline=json.loads(baseline_raw);require(len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==492)
    require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active')and not os.path.lexists('/var/lib/schubert-nk/maintenance/pending'))
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    live=True
    def connection():
        conditions="a.usename='schubert_batch' and a.application_name='PG624-completed-codeonly' and a.state='idle in transaction' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted)"if live else'true'
        sql="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.datname='schubert_nk' and "+conditions+";select count(*) from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in("+str(backend)+",pg_backend_pid());select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;"
        require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==([b'1',b'0',b'1']if live else[b'0',b'0',b'0']))
    paths=(save,pathlib.Path(EPOCH).parent,pathlib.Path(APPROVAL).parent)
    fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)for p in paths]
    original=[os.fstat(fd)for fd in fds]
    def directories():
        def identity(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink)
        for p,fd,before in zip(paths,fds,original):
            require(identity(p.lstat())==identity(os.fstat(fd))==identity(before)and'system.posix_acl_access'not in os.listxattr(p))
    def file(p):
        before=metadata(p);raw=p.read_bytes();require(before==metadata(p))
        return {'metadata':before,'sha256':hashlib.sha256(raw).hexdigest()}
    def snapshot():
        owner();directories();connection();require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
        value={}
        for key,path in {'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage','oldProofs':str(BASE/'pg611-native-stop-v1'),'bootstrapOldProofs':str(BASE/'pg570-bootstrap-existing-v1'),'bootstrapTools':str(BASE/'pg570-bootstrap-tools-v1')}.items():value[key]=tree(pathlib.Path(path))
        value['units']={u:show(u,env['FIELDS'])for u in env['UNITS']}
        value['configuration']={u:show(u,env['configuration_fields']())for u in env['UNITS']}
        for u,v in value['units'].items():require(v['MainPID']==v['ControlPID']=='0'and not v['Job']);kernel(u)
        require(same_value(value['units'],baseline['units'])and same_value(value['configuration'],baseline['configuration']))
        value['dependencies']={u:{k:sorted(v.split())for k,v in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()}for u in env['UNITS']}
        value['parentPid1']=baseline['pid1']
        receipt_raw=(pathlib.Path(__file__).parent/'pg611_parent_receipt.py').read_bytes()
        require(hashlib.sha256(receipt_raw).hexdigest()=='29ea92cd6befc7fd26e1ed23b8785bc7ce616d0cc36247cdb0b2f30c83564676')
        receipt_source=receipt_raw.decode();receipt_env={'datetime':datetime}
        parsed=ast.parse(receipt_source);body=[n for n in parsed.body if isinstance(n,(ast.Assign,ast.FunctionDef))]
        exec(compile(ast.Module(body=body,type_ignores=[]),'<fixed genuine parent receipt>','exec'),receipt_env)
        journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=5a1acaa0c35e484c979401e3b6dfb36a','-o','json','--no-pager'])
        observed=[json.loads(l)for l in journal.splitlines()]
        done=strict(pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/970bbce1-6bba-4db0-ace1-680ee7dfde92.done'),0o600,141)
        require(receipt_env['completed'](observed,done)['endMonotonicUs']==87761979588 and same_value(observed,baseline['pid1']))
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
        require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
        require(not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()))
        for name in('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
        value['runtime']=None;value['current']=str(pathlib.Path('/opt/schubert-nk/current').readlink())
        value['approval']=file(pathlib.Path(APPROVAL))
        unit_files=[pathlib.Path(p)for p in sources({u:show(u,{'FragmentPath','DropInPaths'})for u in env['UNITS']})]
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
    if mode=='activate':
        verified=BASE/'pg624-completed-verify-v1'
        require(strict(verified/'complete.private',0o600,4096)==b'completedCurrentVerified=true\nmode=verify\nallNewScopesReturnedNormally=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n')
        require(same_value(before,json.loads(strict(verified/'after.private.json',0o600,67108864))))
    old_epoch=strict(pathlib.Path(EPOCH),0o600,4096);persist('before.private.json',before)
    print('REF_READY',flush=True);state='READY';changed=False
    for line in sys.stdin.buffer:
        action=line.rstrip(b'\n').decode('ascii');state=phase_action(state,action)
        owner();directories()
        if action=='release':live=False
        now=snapshot()
        if mode=='verify'or action=='before':require(not changed and same_value(now,before))
        else:
            changed_only(before,now,old_epoch,strict(pathlib.Path(EPOCH),0o600,4096))
            require(strict(pathlib.Path(APPROVAL),0o400,192)==NEW_APPROVAL and now['current']==NEXT);changed=True
        if action=='release':
            require(mode=='verify'or changed);persist('after.private.json',now)
            for u in reversed(refs):manager.UnrefUnit(u)
            bus.close()
            for fd in reversed(fds):os.close(fd)
            print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
    raise ValueError('current completed owner channel ended')


if __name__=='__main__':
    try:main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True);print('PG624_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if'pg604_'in frame.filename:print('PG624_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
