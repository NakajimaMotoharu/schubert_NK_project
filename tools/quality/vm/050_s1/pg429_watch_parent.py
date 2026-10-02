"""Read-only finite external parent/API/Web observation. Never start/stop or renew budgets."""
import datetime, hashlib, http.client, json, pathlib, re, subprocess, sys, time
assert len(sys.argv)==3 and re.fullmatch(r'[0-9a-f]{40}',sys.argv[1]) and re.fullmatch(r'[0-9a-f]{64}',sys.argv[2])
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG429')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()==sys.argv[2]
FIELDS='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
UNITS={'morning':'schubert-nk-morning-controller.service','api':'schubert-nk-api.service','web':'schubert-nk-web.service'}
INFO={'commit':sys.argv[1],'app':'0.1.0-SNAPSHOT','config':'1','schema':'025','protocol':'0.1.0-SNAPSHOT'}
def actor(role):
    raw=subprocess.check_output(['/usr/bin/systemctl','show',UNITS[role],'--property='+FIELDS],text=True,timeout=5)
    result=dict(line.split('=',1) for line in raw.splitlines());assert len(result)==18
    if int(result['MainPID']):
        proc=pathlib.Path('/proc')/result['MainPID']
        try:
            result['startTicks']=int((proc/'stat').read_text().rpartition(')')[2].split()[19])
            result['process']={k:v.strip() for k,v in (line.split(':',1) for line in (proc/'status').read_text().splitlines() if ':' in line)
                if k in {'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}}
            entries={'dev.codex.schubert.nk.batch.file.RootServiceLauncher','dev.codex.schubert.nk.api.bootstrap.ApiProcessMain','dev.codex.schubert.nk.web.bootstrap.WebProcessMain','dev.codex.schubert.nk.batch.file.MorningProcessMain'}
            result['entry']=next((s.decode('ascii') for s in (proc/'cmdline').read_bytes().split(b'\0') if s.decode('ascii',errors='replace') in entries),'other')
        except (FileNotFoundError,ProcessLookupError):result['race']=True
    return result
def same(a,b):
    return all(a.get(k)==b.get(k) for k in ('MainPID','InvocationID','startTicks')) and not b.get('race')
def sockets(a,port):
    proc=pathlib.Path('/proc')/a['MainPID'];fds=set()
    for fd in (proc/'fd').iterdir():
        try:
            target=str(fd.readlink())
            if target.startswith('socket:['):fds.add(target[8:-1])
        except FileNotFoundError:pass
    result=set()
    for name,address in [('tcp',f'0100007F:{port:04X}'),('tcp6',f'0000000000000000FFFF00000100007F:{port:04X}')]:
        for line in (proc/'net'/name).read_text().splitlines()[1:]:
            f=line.split()
            if len(f)>=10 and f[1]==address and f[3]=='0A' and f[9] in fds:result.add(f[9])
    return result
def get(port,path):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=.5)
    try:
        c.request('GET',path);r=c.getresponse();body=r.read(4097);assert len(body)<=4096
        return r.status,body
    finally:c.close()
seen=False;roots={};ready=set();prior=None;deadline=time.monotonic()+1900;morning=None
while time.monotonic()<deadline:
    states={role:actor(role) for role in UNITS};m=states['morning']
    if int(m['MainPID']):
        seen=True
        if morning is None:
            morning=m;deadline=min(deadline,int(m['ExecMainStartTimestampMonotonic'])/1e6+1860)
        assert same(morning,m),'parent generation changed'
    for role in ['api','web']:
        a=states[role]
        if a.get('entry')=='dev.codex.schubert.nk.batch.file.RootServiceLauncher' and not a.get('race'):
            roots.setdefault(role,a)
        if role not in ready and a.get('entry')=='dev.codex.schubert.nk.'+role+'.bootstrap.'+role.capitalize()+'ProcessMain' and not a.get('race'):
            p=a['process'];account='schubert-'+role
            uid=subprocess.check_output(['id','-u',account],text=True).strip();gid=subprocess.check_output(['id','-g',account],text=True).strip()
            groups=sorted(set(subprocess.check_output(['id','-G',account],text=True).split()),key=int)
            assert p['Uid'].split()==[uid]*4 and p['Gid'].split()==[gid]*4 and p['Groups'].split()==groups and p['NoNewPrivs']=='1'
            assert all(p[k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
            try:
                port=8091 if role=='api' else 8081;before=sockets(a,port)
                if before:
                    health=get(port,'/actuator/health/readiness');info=get(port,'/actuator/info')
                    aa=actor(role);mm=actor('morning')
                    if health==(200,b'{"status":"UP"}') and info[0]==200 and json.loads(info[1])==INFO:
                        assert same(a,aa) and same(m,mm) and before.intersection(sockets(aa,port))
                        assert role in roots and same(roots[role],aa),'captured Root-to-ordinary generation missing'
                        ready.add(role)
                        print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready':role,'sameRootOrdinary':True,'sameParent':True,'ownedSocket':True,'info':INFO,'wholeMorningAccepted':False}),flush=True)
            except (OSError,http.client.HTTPException):pass
    key=json.dumps(states,sort_keys=True)
    if key!=prior:
        print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'states':states}),flush=True);prior=key
    if seen and all(a['MainPID']=='0' and a['ControlPID']=='0' and not a['Job'] for a in states.values()):
        print(json.dumps({'terminalObserved':True,'readyObserved':sorted(ready),'rootsCaptured':sorted(roots),'automaticStop':False,'wholeMorningAccepted':False}),flush=True);break
    time.sleep(.05)
else:print(json.dumps({'watchDeadline':True,'readyObserved':sorted(ready),'automaticStop':False,'wholeMorningAccepted':False}),flush=True)
