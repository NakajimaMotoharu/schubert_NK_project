"""Completed PG522 code-only witness; every new scope normal, no old recovery/start."""
import ast
import hashlib
import json
import os
import pathlib
from pathlib import Path
import re
import sys
import time
import dbus
from pg543_runtime_readback import load,BOOT,RUNTIME
from pg549_completed_contract import OLD,NEXT,EPOCH,APPROVAL,NEW_APPROVAL,changed_only,phase_action,require


def main():
    require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]in('verify','activate')and sys.argv[2].isdigit())
    mode=sys.argv[1];backend=int(sys.argv[2]);require(backend>1);os.umask(0o077)
    save=Path('/var/lib/pgpt-s1-preservation/pg549-completed-'+mode+'-v5')
    boundary_raw=Path('/var/lib/pgpt-s1-preservation/pg543-runtime-retirement-v2/boundaries.private.json').read_bytes()
    require(hashlib.sha256(boundary_raw).hexdigest()=='0e7fe76e884f918d936842d8bf887c03f816099a11a9a988d022720a13c43726')
    env,baseline,initial,_,_,captured=load(post=True,caddy_before=json.loads(boundary_raw)['caddyExecStartPre'])
    raw=Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='owner')
    class Binding(ast.NodeTransformer):
        def visit_Constant(self,n):
            return ast.copy_location(ast.Constant(b'Pg549CompletedDeployment'),n)if n.value==b'Pg480BackupRecovery'else n
    node=Binding().visit(node);ast.fix_missing_locations(node)
    ownenv={'pathlib':pathlib,'os':os,'sys':sys,'require':require,**{n:env[n]for n in('strict','command')}}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed completed owner>','exec'),ownenv)
    held=ownenv['owner']()
    def owner():require(ownenv['owner']()==held)
    bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    live=True
    def connection():
        identity="a.usename='schubert_batch'and a.application_name='PG549-completed-codeonly'and a.state='idle in transaction'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted)"if live else'true'
        sql="select count(*)from pg_stat_activity a where a.pid="+str(backend)+" and a.datname='schubert_nk'and "+identity+";select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid not in("+str(backend)+",pg_backend_pid());select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
        require(env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==([b'1',b'0',b'1']if live else[b'0',b'0',b'0']))
    savefd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);startupfd=os.open(Path(EPOCH).parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    approvalfd=os.open(Path(APPROVAL).parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    dirs=[os.fstat(fd)for fd in(savefd,startupfd,approvalfd)]
    def directories():
        for fd,p,old in zip((savefd,startupfd,approvalfd),(save,Path(EPOCH).parent,Path(APPROVAL).parent),dirs):
            def identity(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink)
            require(identity(p.lstat())==identity(os.fstat(fd))==identity(old)and'system.posix_acl_access'not in os.listxattr(p))
    def file(p):
        a=env['metadata'](p);raw=p.read_bytes();require(a==env['metadata'](p));return {'metadata':a,'sha256':hashlib.sha256(raw).hexdigest()}
    def extras(value):
        value['current']=str(Path('/opt/schubert-nk/current').readlink());value['approval']=file(Path(APPROVAL))
        value['unitFiles']={p:file(Path(p))for p in captured};value['caddyPre']=env['show']('caddy.service',{'ExecStartPre'})['ExecStartPre']
        return value
    def snapshot():
        owner();directories();connection();require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
        paths={'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage','oldProofs':'/var/lib/pgpt-s1-preservation/pg526-native-stop-v1','bootstrapOldProofs':'/var/lib/pgpt-s1-preservation/pg535-bootstrap-existing-v1','bootstrapTools':'/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1'}
        value={k:env['tree'](Path(p))for k,p in paths.items()}
        value['units']={u:env['show'](u,env['FIELDS'])for u in env['UNITS']}
        for u in env['UNITS']:env['kernel'](u)
        value['configuration']={u:env['show'](u,set(c))for u,c in baseline['configuration'].items()}
        depraw=Path('/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1/pg529_dependency_graph.py').read_bytes()
        require(hashlib.sha256(depraw).hexdigest()=='5931ef9687aa24fa693f0d15d96d912b19c9ca7b365ffd25f4588d2c39f5de60')
        deps={'re':re};exec(compile(depraw,'<sealed dependency policy>','exec'),deps)
        value['dependencies']=deps['dependency_graph']({u:env['show'](u,set(deps['GRAPH_FIELDS']))for u in env['UNITS']},env['UNITS'])
        cmd=['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1']
        value['parentPid1']=[json.loads(l)for l in env['command']([*cmd,'UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=8f4514e19fd94c429f2587af71edb53a','-o','json','--no-pager']).splitlines()]
        value['pid1Stop']={}
        for u,stop in baseline['pid1Stop'].items():
            rows=[json.loads(l)for l in env['command']([*cmd,'UNIT='+u,'-o','json','--no-pager']).splitlines()]
            value['pid1Stop'][u]=[r for r in rows if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_ID')==stop[0]['JOB_ID']and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
        sql="begin isolation level repeatable read read only;set local timezone='UTC';"
        for table in baseline['rows']:
            require(re.fullmatch(r'(schubert|schubert_web_session)\.[a-z_]+',table)is not None)
            sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
        value['rows']={}
        for line in env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;']).splitlines():
            row=json.loads(line);require(row['table']not in value['rows']);value['rows'][row['table']]=row['rows']
        require(not os.path.lexists(RUNTIME)and not list(RUNTIME.parent.iterdir()));value['runtime']=None
        require(value['units']=={u:env['show'](u,env['FIELDS'])for u in env['UNITS']});connection();owner();return extras(value)
    def save_json(name,value):
        directories();fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=savefd)
        with os.fdopen(fd,'wb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
        os.fsync(savefd)
    connection();before=extras(initial());require(before==snapshot()==snapshot()and before['current']==OLD)
    old_epoch=env['strict'](Path(EPOCH),0o600,4096);save_json('before.private.json',before);print('REF_READY',flush=True)
    changed=False;state='READY'
    for line in sys.stdin.buffer:
        action=line.rstrip(b'\n').decode('ascii');require(action in('before','after','release'))
        state=phase_action(state,action)
        owner();directories()
        if action=='release':live=False
        now=snapshot()
        if mode=='verify' or action=='before':require(not changed and now==before)
        else:
            changed_only(before,now,old_epoch,env['strict'](Path(EPOCH),0o600,4096));require(env['strict'](Path(APPROVAL),0o400,192)==NEW_APPROVAL and now['current']==NEXT);changed=True
        if action=='release':
            require(mode=='verify' or changed);save_json('after.private.json',now)
            for unit in reversed(refs):manager.UnrefUnit(unit)
            bus.close()
            for fd in(approvalfd,startupfd,savefd):os.close(fd)
            print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
    raise ValueError('completed owner channel ended')


if __name__=='__main__':
    try:main()
    except Exception as failure:
        import traceback
        print('REF_FAILED',flush=True);print('PG549_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg549_'in frame.filename or'pg543_'in frame.filename:print('PG549_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
        while True:time.sleep(1)
