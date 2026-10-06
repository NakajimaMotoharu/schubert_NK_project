"""BUG766/SSC191 read-only partial completion proof and exact two-actor handoff.
No repeat deployment, new epoch/permit, DB update, service start or stop.
"""
import ast,hashlib,json,os,pathlib,select,signal,stat,subprocess,sys,time
import dbus
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg475-native-tools-v1')
from pg466_term_witness import FIELDS,unique
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-partial-handoff-v3')
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-partial-tools-v3')
PID=3412034;TICKS=21968172
CHILD=3412055;CHILD_TICKS=21968211
META_PID=3413981;META_TICKS=22093029
META_SOURCE='63c6823f3ba04b63f4807f7341775cf28796932c979c4c96f01c8eaadc5008ae'
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
CLASS='0e70b9f43113fb9084a0dd59635624f5852aaf7a4889d165d229a81636ddb82d'
CHILD_SOURCE='e3e0da8108d5fff740076cf75055ae48cf35b617ade491d8de5cdecdf811b934'
ALL=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
CP="/var/lib/pgpt-s1-preservation/pg477-partial-tools-v3:/var/lib/pgpt-s1-preservation/pg475-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg474-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg473-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg471-readback-tools-v3:/var/lib/pgpt-s1-preservation/pg471-completed-tools-v2:/var/lib/pgpt-s1-preservation/pg469-current-tools-v3:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2:/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG477/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG477/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG477/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG477/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar"
def require(b):
    if not b:raise ValueError('fixed handoff refused')
def command(args,timeout=5,limit=4194304):
    result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
    require(result.returncode==0 and len(result.stdout)<=limit);return result.stdout
def save(name,data):
    require('/' not in name);p=ROOT/name
    with p.open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def holder():
    require(tick(PID)==TICKS)
    p=pathlib.Path('/proc')/str(PID);argv=(p/'cmdline').read_bytes().split(b'\0');require(argv[-3:]==[b'Pg477StoppedDeployment',b'activate',b''])
    require(argv[0]==b'/opt/jdk-25.0.4/bin/java' and len(argv)==7 and argv[1]==b'--enable-native-access=ALL-UNNAMED' and argv[2]==b'-cp')
    require(hashlib.sha256(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3/Pg477StoppedDeployment.class').read_bytes()).hexdigest()==CLASS)
    locks={};fd_targets={}
    for fd in (p/'fd').iterdir():
        try:target=str(fd.readlink())
        except FileNotFoundError:continue
        fd_targets[fd.name]=target
    raw=pathlib.Path('/proc/locks').read_text().splitlines()
    for name in ('maintenance.lock','startup-admission.lock'):
        target=pathlib.Path('/run/schubert-nk')/name;st=target.stat();require(st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1)
        require(str(target) in fd_targets.values());identity=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)
        matches=[]
        for line in raw:
            fields=line.split()
            if len(fields)>=8 and fields[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
                device=fields[5].split(':')
                if len(device)==3 and (int(device[0],16),int(device[1],16),int(device[2]))==identity:matches.append(line)
        require(len(matches)==1);locks[name]=list(identity)
    # A logical JDBC object is not a proof of a live server session/advisory lease.
    database=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c',"select pid,usename,state,client_port from pg_catalog.pg_stat_activity where usename in ('schubert_batch','schubert_migration') order by pid"]).decode('ascii')
    return {'pid':PID,'startTicks':TICKS,'boot':BOOT,'classSha256':CLASS,'locks':locks,'observedOldDatabaseSessions':database,'oldCloseUnknown':True}
def no_sessions():
    value=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c',"select count(*) from pg_catalog.pg_stat_activity where usename in ('schubert_batch','schubert_migration')"]).strip()
    require(value==b'0')

def policy():
    tree=ast.parse((TOOLS/'pg477_unit_references.py').read_text())
    config=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONFIG' for t in n.targets))
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['show','kernel','effective_rw','exec_record','after_exec','same_declaration','signed_declaration']]
    require(len(functions)==7)
    import re
    env={'FIELDS':FIELDS,'UNITS':ALL,'require':require,'command':command,'pathlib':pathlib,'re':re}
    exec(compile(ast.Module(body=[config,*functions],type_ignores=[]),'<fixed partial policy>','exec'),env)
    return env
def states(env):
    before={}
    for unit in ALL:
        value=env['show'](unit)
        require(value['MainPID']==value['ControlPID']=='0' and not value['Job'] and value['ActiveState'] in ['inactive','failed'])
        env['kernel'](unit);require(value==env['show'](unit));before[unit]=value
    return before
def owned_children(pid):
    before=tick(pid);top=pathlib.Path('/proc')/str(pid)/'task';tasks=sorted(x.name for x in top.iterdir());values=[]
    require(tasks and all(x.isdigit() for x in tasks))
    for task in tasks:
        children=(top/task/'children').read_text().split()
        require(all(x.isdigit() and int(x)>0 for x in children));values.extend(children)
    require(len(values)==len(set(values)) and tasks==sorted(x.name for x in top.iterdir()) and tick(pid)==before)
    return sorted(values,key=int)
def child():
    require(tick(CHILD)==CHILD_TICKS)
    p=pathlib.Path('/proc')/str(CHILD)
    argv=(p/'cmdline').read_bytes().split(b'\0')
    require(argv==[b'/usr/bin/python3',b'-B',b'/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3/pg477_unit_references.py',b'activate',b''])
    require(int((p/'stat').read_text().rpartition(')')[2].split()[1])==PID)
    require(hashlib.sha256(pathlib.Path(argv[2].decode()).read_bytes()).hexdigest()==CHILD_SOURCE)
    require(not owned_children(CHILD))
    require(owned_children(PID)==[str(CHILD)])
    return {'pid':CHILD,'ticks':CHILD_TICKS,'sourceSha256':CHILD_SOURCE}
def metadata_actor():
    require(tick(META_PID)==META_TICKS);p=pathlib.Path('/proc')/str(META_PID)
    script=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-partial-tools-v2/pg477_partial_handoff.py')
    require((p/'cmdline').read_bytes().split(b'\0')==[b'/usr/bin/python3',b'-B',str(script).encode(),b'handoff',b''])
    require(hashlib.sha256(script.read_bytes()).hexdigest()==META_SOURCE and not owned_children(META_PID))
    require(not any(line.split()[4:5]==[str(META_PID)] for line in pathlib.Path('/proc/locks').read_text().splitlines()))
    require(not list(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-partial-handoff-v2').iterdir()))
    return {'pid':META_PID,'ticks':META_TICKS,'sourceSha256':META_SOURCE,'maintenanceAuthority':False}
def configuration(env,proof):
    unchanged=set(ALL)-{'schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service','schubert-nk-morning-controller.service'}
    after={}
    for unit in ALL:
        value=env['show'](unit,env['CONFIG']);old=proof['configuration'][unit];require(set(value)==set(old))
        allowed=set() if unit in unchanged else {'ExecStart','DropInPaths','ReadWritePaths'}
        require(all(value[k]==old[k] for k in set(value)-allowed-{'ExecStart'}))
        require(env['signed_declaration'](unit,old['ExecStart'],value['ExecStart']))
        if unit not in unchanged:
            require(env['effective_rw'](unit,old['ReadWritePaths'],value['ReadWritePaths']))
            require('--resume' not in value['ExecStart'] and '/opt/pgpt-tools-pg390/schubert-nk-inbox-inspector' not in value['ExecStart'])
            if 'morning' in unit:
                require(value['DropInPaths']=='/etc/systemd/system/'+unit+'.d/pg477-native-coverage.conf')
            else:
                require(value['DropInPaths']=='')
                installed=pathlib.Path('/etc/systemd/system')/unit
                require(not installed.is_symlink() and installed.read_bytes()==(pathlib.Path('/opt/schubert-nk/current/systemd')/unit).read_bytes())
            if 'bootstrap' in unit:require('sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary' in value['ExecStart'])
            if 'inspector' in unit:require('/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector' in value['ExecStart'])
        after[unit]=value
    return after
def readback(mode,label):
    p=ROOT/(label+'.private.log')
    with p.open('xb') as f:
        os.fchmod(f.fileno(),0o600)
        result=subprocess.run(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',CP,'Pg477PartialReadback',mode],stdin=subprocess.DEVNULL,stdout=f,stderr=f,timeout=90)
        f.flush();os.fsync(f.fileno())
    require(result.returncode==0 and p.stat().st_size<=1048576 and b'PG477_PARTIAL_READBACK allReadOnlyScopesReturnedNormally=true' in p.read_bytes())
def native(label):
    p=ROOT/(label+'.private.log')
    with p.open('xb') as f:
        os.fchmod(f.fileno(),0o600)
        result=subprocess.run(['/usr/bin/python3','-B',str(TOOLS/'pg477_partial_native.py'),'after'],stdin=subprocess.DEVNULL,stdout=f,stderr=f,timeout=60)
        f.flush();os.fsync(f.fileno())
    require(result.returncode==0 and p.read_bytes()==b'PG477_STOPPED_NATIVE action=after sameSavedCohort=true allNineKernelEmpty=true ordinary143IsStopData=true currentMatched=true starts0=true stops0=true\n')
def signal_one(pid,ticks,proof):
    require(tick(pid)==ticks)
    fd=os.pidfd_open(pid,0)
    try:
        require(tick(pid)==ticks);save(proof,b'fixedIdentityRechecked=true\noldNormalCloseNotInferred=true\n')
        signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
        poll=select.poll();poll.register(fd,select.POLLIN);require(poll.poll(15000))
    finally:os.close(fd)
    end=time.monotonic()+15
    while (pathlib.Path('/proc')/str(pid)).exists() and time.monotonic()<end:time.sleep(.01)
    require(not (pathlib.Path('/proc')/str(pid)).exists())
def main():
    require(os.geteuid()==0 and sys.argv[1:] in [['inspect'],['handoff']])
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
    require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG477'))
    require(not ROOT.exists());ROOT.mkdir(mode=0o700)
    for target in ['timers.target','paths.target']:
        require(command(['/usr/bin/systemctl','show',target,'--property=LoadState']).strip()==b'LoadState=masked')
    original=holder();require(not original['observedOldDatabaseSessions'].strip());child_before=child();meta_before=metadata_actor()
    proof=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3/refs-activate-before.private.json').read_text(),object_pairs_hook=unique)
    env=policy();bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    try:
        for unit in ALL:manager.RefUnit(unit);refs.append(unit)
        value=states(env);require(value==proof['stopped']);configs=configuration(env,proof)
        save('holder-before.private.json',json.dumps(original,sort_keys=True).encode());save('child-before.private.json',json.dumps(child_before,sort_keys=True).encode())
        save('metadata-actor-before.private.json',json.dumps(meta_before,sort_keys=True).encode())
        save('unit-before.private.json',json.dumps(value,sort_keys=True).encode());save('configuration-before.private.json',json.dumps(configs,sort_keys=True).encode())
        native('native-before');readback('snapshot','before-handoff');no_sessions()
        require(holder()==original and child()==child_before and metadata_actor()==meta_before and states(env)==value and configuration(env,proof)==configs)
        if sys.argv[1]=='handoff':
            signal_one(META_PID,META_TICKS,'metadata-actor-term-request.private')
            require(holder()==original and child()==child_before and states(env)==value)
            signal_one(CHILD,CHILD_TICKS,'child-term-request.private')
            require(holder()==original and states(env)==value and not owned_children(PID))
            native('native-after-child')
            require(holder()==original and states(env)==value and configuration(env,proof)==configs)
            signal_one(PID,TICKS,'parent-term-request.private')
            require(not any(line.split()[4:5]==[str(PID)] for line in pathlib.Path('/proc/locks').read_text().splitlines()))
            no_sessions();require(states(env)==value);readback('verify','after-handoff');no_sessions();require(states(env)==value and configuration(env,proof)==configs)
            save('interrupted.private',b'oldOperationInterrupted=true\nexpectedExit143=true\noldCloseUnknown=true\npartialCurrentNotReplayed=true\nnewOwnershipRequired=true\n')
        for unit in reversed(refs):manager.UnrefUnit(unit)
        bus.close()
        print('PG477_PARTIAL_'+sys.argv[1].upper()+' allReadOnlyScopesReturnedNormally=true fullOldValuesPreserved=true starts0=true deployReplay0=true oldCloseNotInferred=true',flush=True)
    except Exception:
        print('PG477_PARTIAL_UNKNOWN senderRetained=true nextStartIsolated=true',file=sys.stderr,flush=True)
        while True:time.sleep(1)
if __name__=='__main__':main()
