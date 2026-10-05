"""SSC191 bounded operator isolation/handoff, not startup/permit/old close authority.
Usage inspect|isolate|terminate; each mutating phase is new-only and independently reauthenticated.
Runs as root in the fixed PG/PT VM. TERM only after all-nine stop/readback isolation receipt.
"""
import hashlib,json,os,pathlib,select,signal,stat,subprocess,sys,time
from pg466_term_witness import witness,FIELDS,unique
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg466-handoff-v2')
PID=1438705;TICKS=12405848
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
SOURCE='e4c7f0b84b02a2124a0aba2a7b682ad482d5cd45'
CLASS='fcbd363e811e45dbb9bf3cd7bfef1a9c47f5199dcb7e1ac0dbd7c1bec6651ed8'
EXPECTED={'schubert-nk-api.service':('1338494','9269078370384fdaab05ca9a0fcd50bd'),'artemis.service':('1227864','c784737af61e48778d0c8fa2c4f68037')}
ORDER=['schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']
ALL=['caddy.service','schubert-nk-web.service',*ORDER,'schubert-nk-morning-controller.service']
CP='/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG465/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG465/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG465/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG465/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
def require(b):
    if not b:raise ValueError('fixed handoff refused')
def command(args,timeout=5,limit=4194304):
    result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
    require(result.returncode==0 and len(result.stdout)<=limit);return result.stdout
def save(name,data):
    require('/' not in name);p=ROOT/name
    with p.open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
def show(unit):
    require(unit in ALL);raw=command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode('ascii');values={}
    for line in raw.splitlines():
        k,v=line.split('=',1);require(k not in values);values[k]=v
    require(set(values)==FIELDS and values['Id']==unit and values['LoadState']=='loaded');return values
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def empty_kernel(unit):
    c=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
    if c.exists():
        for p in [c,*[x for x in c.rglob('*') if x.is_dir()]]:
            require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
def holder():
    require(tick(PID)==TICKS)
    p=pathlib.Path('/proc')/str(PID);argv=(p/'cmdline').read_bytes().split(b'\0');require(argv[-3:]==[b'Pg465CompletedDeployment',b'activate',b''])
    require(argv[0]==b'/opt/jdk-25.0.4/bin/java' and len(argv)==7 and argv[1]==b'--enable-native-access=ALL-UNNAMED' and argv[2]==b'-cp')
    require(hashlib.sha256(pathlib.Path('/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2/Pg465CompletedDeployment.class').read_bytes()).hexdigest()==CLASS)
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
def all_terminal():
    first={unit:show(unit) for unit in ALL}
    for unit,v in first.items():
        require(v['MainPID']==v['ControlPID']=='0' and not v['Job'] and v['ActiveState'] in ('inactive','failed'));empty_kernel(unit)
    require(first=={unit:show(unit) for unit in ALL});return first
def web_stopped():
    p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg466-tool-v1/pg466-web-before18.private.json');st=p.stat()
    require(st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o400 and st.st_nlink==1 and st.st_size<=4096)
    b=json.loads(p.read_text());a=show('schubert-nk-web.service')
    require(b['MainPID']=='1340568' and b['InvocationID']=='716bd4789cde40af97775e48641159fe')
    raw=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+b['InvocationID'],'-o','json','--no-pager'])
    data=witness('WEB',b,a,raw,'1340568','997');require(not pathlib.Path('/proc/1340568').exists());empty_kernel('schubert-nk-web.service')
    require(a==show('schubert-nk-web.service'));return raw,data
def readback(mode,label):
    name=label+'.private.log';p=ROOT/name
    with p.open('xb') as f:
        os.fchmod(f.fileno(),0o600)
        result=subprocess.run(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',CP,'Pg466HandoffReadback',mode],stdin=subprocess.DEVNULL,stdout=f,stderr=f,timeout=90)
        f.flush();os.fsync(f.fileno())
    require(result.returncode==0 and p.stat().st_size<=1048576 and b'PG466_HANDOFF_READBACK allReadOnlyScopesReturnedNormally=true' in p.read_bytes())
def isolate():
    require(not (ROOT/'isolation-start.private').exists());before=holder();save('isolation-start.private',json.dumps(before,sort_keys=True).encode())
    web_raw,web_data=web_stopped();save('web-full-journal.private.jsonl',web_raw);save('web-stop-witness.private',json.dumps(web_data).encode())
    # Fresh private snapshot was independently completed before entering this controller.
    # Its successful read-only closure is not old-tool closure or new M/A ownership.
    readback('verify','before-isolation')
    require(holder()['locks']==before['locks']);captures={unit:show(unit) for unit in ORDER}
    for unit,v in captures.items():
        require(v['ControlPID']=='0' and not v['Job'] and v['Result']=='success')
        if unit in EXPECTED:require((v['MainPID'],v['InvocationID'])==EXPECTED[unit] and v['ActiveState']=='active' and v['SubState']=='running')
        else:require(v['MainPID']=='0' and v['ActiveState'] in ('active','inactive'));empty_kernel(unit)
    save('captured-before.private',json.dumps(captures,sort_keys=True).encode())
    for unit in ORDER:
        require(holder()['locks']==before['locks'] and captures[unit]==show(unit))
        if unit not in EXPECTED and captures[unit]['ActiveState']=='inactive':continue
        result=subprocess.run(['/usr/bin/systemctl','stop',unit],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120);require(result.returncode==0)
        after=show(unit);require(after['MainPID']==after['ControlPID']=='0' and not after['Job']);empty_kernel(unit)
        if unit=='schubert-nk-api.service':
            raw=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+captures[unit]['InvocationID'],'-o','json','--no-pager']);save('api-full-journal.private.jsonl',raw)
            data=witness('API',captures[unit],after,raw,captures[unit]['MainPID'],'999');save('api-stop-witness.private',json.dumps(data).encode())
            require(not (pathlib.Path('/proc')/captures[unit]['MainPID']).exists())
        else:require(after['ActiveState']=='inactive' and after['Result']=='success')
        save(unit+'.stopped.private',json.dumps(after,sort_keys=True).encode());print('PG466_OWNED_ISOLATED unit='+unit+' nextStart=false',flush=True)
    states=all_terminal();readback('verify','after-isolation');require(holder()['locks']==before['locks'])
    save('isolated.private',json.dumps({'allNine':states,'holder':holder(),'newStarts':0,'oldActivated':False,'oldCloseUnknown':True},sort_keys=True).encode())
    print('PG466_ISOLATED allNineKernelEmpty=true originalAllValuesPreserved=true oldHolderStillAuthenticated=true oldCloseUnknown=true',flush=True)
def terminate():
    require((ROOT/'isolated.private').exists() and not (ROOT/'term-request.private').exists());all_terminal();readback('verify','before-holder-term');before=holder()
    fd=os.pidfd_open(PID,0)
    try:
        require(holder()==before);save('term-request.private',json.dumps(before,sort_keys=True).encode());signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
        poll=select.poll();poll.register(fd,select.POLLIN);require(poll.poll(15000))
    finally:os.close(fd)
    deadline=time.monotonic()+15
    while (pathlib.Path('/proc')/str(PID)).exists() and time.monotonic()<deadline:
        try:require(tick(PID)==TICKS)
        except FileNotFoundError:break
        time.sleep(.01)
    complete_interruption()
def complete_interruption():
    # May finalize the already-issued TERM after a reaping observation failed; no signal.
    require((ROOT/'term-request.private').exists() and (ROOT/'isolated.private').exists())
    require(not (pathlib.Path('/proc')/str(PID)).exists());all_terminal()
    database=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c',"select count(*) from pg_catalog.pg_stat_activity where usename in ('schubert_batch','schubert_migration')"]).strip();require(database==b'0')
    require(not any(line.split()[4:5]==[str(PID)] for line in pathlib.Path('/proc/locks').read_text().splitlines()))
    save('interrupted.private',b'interrupted=true\nexpectedExit143=true\noldCloseUnknown=true\noldActivated=false\noldPhysicalHolderAbsent=true\nnewOwnershipNotYetAcquired=true\n')
    print('PG466_OLD_TOOL_INTERRUPTED normalCloseNotInferred=true oldPhysicalHolderAbsent=true newOwnershipRequired=true',flush=True)
def broker_witness(before,after,raw):
    require(before['MainPID']=='1227864' and before['InvocationID']=='c784737af61e48778d0c8fa2c4f68037')
    require(after['InvocationID']==before['InvocationID'] and after['ExecMainStartTimestampMonotonic']==before['ExecMainStartTimestampMonotonic'] and after['Result']=='success' and after['ExecMainCode']=='1' and after['ExecMainStatus']=='143')
    require(0<len(raw)<=4194304 and raw.endswith(b'\n'));cursors=set();stopped=0
    for line in raw.decode('utf-8',errors='strict').splitlines():
        row=json.loads(line,object_pairs_hook=unique)
        for key in ('__CURSOR','__MONOTONIC_TIMESTAMP','__REALTIME_TIMESTAMP','_BOOT_ID','_SYSTEMD_UNIT','_SYSTEMD_INVOCATION_ID','PRIORITY','MESSAGE'):require(isinstance(row.get(key),str))
        require(row['_BOOT_ID']==BOOT.replace('-','') and row['_SYSTEMD_UNIT']=='artemis.service' and row['_SYSTEMD_INVOCATION_ID']==before['InvocationID'])
        require(row['PRIORITY'] in ('4','5','6','7') and row['__CURSOR'] and row['__CURSOR'] not in cursors);cursors.add(row['__CURSOR'])
        require(row['__MONOTONIC_TIMESTAMP'].isdigit() and row['__REALTIME_TIMESTAMP'].isdigit() and int(before['ExecMainStartTimestampMonotonic'])<=int(row['__MONOTONIC_TIMESTAMP'])<=int(after['ExecMainExitTimestampMonotonic']))
        message=row['MESSAGE'];require('AMQ224' not in message and not any(x in message.split() for x in ('ERROR','FATAL')))
        if 'AMQ221002: Apache Artemis Message Broker version 2.56.0' in message and ' stopped, uptime ' in message:stopped+=1
    require(stopped==1 and not pathlib.Path('/proc/1227864').exists());return {'rows':len(cursors),'sha256':hashlib.sha256(raw).hexdigest(),'vendorStopData':True,'oldCloseSuccess':False}
def finalize_isolation():
    # BUG724 exact partial: API+Cleanup explicit stops, Broker/Expiry dependent stops.
    require(not (ROOT/'isolated.private').exists() and (ROOT/'captured-before.private').exists())
    require(set(p.name for p in ROOT.iterdir())=={'isolation-start.private','web-full-journal.private.jsonl','web-stop-witness.private','before-isolation.private.log','captured-before.private','api-full-journal.private.jsonl','api-stop-witness.private','schubert-nk-api.service.stopped.private','schubert-nk-cleanup.service.stopped.private'})
    before=holder();captures=json.loads((ROOT/'captured-before.private').read_text(),object_pairs_hook=unique);states=all_terminal()
    require(set(captures)==set(ORDER));web_stopped()
    for unit in ORDER:
        old=captures[unit];current=states[unit];require(set(old)==FIELDS and old['InvocationID']==current['InvocationID'] and old['ExecMainStartTimestampMonotonic']==current['ExecMainStartTimestampMonotonic'])
        if unit=='schubert-nk-api.service':
            raw=(ROOT/'api-full-journal.private.jsonl').read_bytes();witness('API',old,current,raw,'1338494','999');require(not pathlib.Path('/proc/1338494').exists())
        elif unit=='artemis.service':
            raw=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+old['InvocationID'],'-o','json','--no-pager']);data=broker_witness(old,current,raw)
            save('broker-full-journal.private.jsonl',raw);save('broker-stop-witness.private',json.dumps(data).encode())
        else:require(current['ActiveState']=='inactive' and current['Result']=='success' and current['ExecMainCode']==old['ExecMainCode'] and current['ExecMainStatus']==old['ExecMainStatus'])
    readback('verify','after-dependent-isolation');require(holder()['locks']==before['locks'] and states==all_terminal())
    save('isolated.private',json.dumps({'allNine':states,'holder':holder(),'newStarts':0,'oldActivated':False,'oldCloseUnknown':True,'explicitStops':['API','Cleanup'],'dependentStops':['Artemis','Expiry']},sort_keys=True).encode())
    print('PG466_ISOLATED allNineKernelEmpty=true originalAllValuesPreserved=true oldHolderStillAuthenticated=true dependentStopsAuthenticated=true oldCloseUnknown=true',flush=True)
def main():
    require(os.geteuid()==0 and len(sys.argv)==2 and sys.argv[1] in ('inspect','isolate','finalize-isolation','terminate','finalize-term','closed'))
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
    if sys.argv[1]!='closed':require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG464'))
    for target in ('timers.target','paths.target'):
        require(command(['/usr/bin/systemctl','show',target,'--property=LoadState']).strip()==b'LoadState=masked')
    # BUG722 first attempt failed before any capture/stop issuance; do not erase its guard.
    prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg466-handoff')
    require(set(p.name for p in prior.iterdir())=={'isolation-start.private','web-full-journal.private.jsonl','web-stop-witness.private','before-isolation.private.log'})
    prior_log=(prior/'before-isolation.private.log').read_bytes()
    require(len(prior_log)<4096 and b'Pg466HandoffReadback.main(Pg466HandoffReadback.java:55)' in prior_log)
    # Administrative starts/namespace updates are prohibited for this entire controlled
    # operator sequence; the fixed VM has no production automatic scheduling enabled.
    if sys.argv[1]=='inspect':print(json.dumps(holder(),sort_keys=True));return
    if not ROOT.exists():ROOT.mkdir(mode=0o700)
    require(stat.S_IMODE(ROOT.stat().st_mode)==0o700 and ROOT.stat().st_uid==0)
    if sys.argv[1]=='isolate':isolate()
    elif sys.argv[1]=='finalize-isolation':finalize_isolation()
    elif sys.argv[1]=='finalize-term':
        readback('verify','after-already-issued-term');complete_interruption()
    elif sys.argv[1]=='closed':
        require((ROOT/'interrupted.private').exists() and not (pathlib.Path('/proc')/str(PID)).exists())
        saved=json.loads((ROOT/'isolated.private').read_text(),object_pairs_hook=unique)
        require(all_terminal()==saved['allNine'] and not any(line.split()[4:5]==[str(PID)] for line in pathlib.Path('/proc/locks').read_text().splitlines()))
        print('PG466_CLOSED allNineUnchanged=true oldPhysicalHolderAbsent=true oldCloseUnknown=true',flush=True)
    else:terminate()
if __name__=='__main__':main()
