"""Read-only finite external parent/API/Web observation. Never start/stop or renew budgets."""
import datetime, hashlib, http.client, json, pathlib, re, ssl, subprocess, sys, time
assert len(sys.argv)==4 and sys.argv[3]=='PG489' and re.fullmatch(r'[0-9a-f]{40}',sys.argv[1]) and re.fullmatch(r'[0-9a-f]{64}',sys.argv[2])
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG489')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()==sys.argv[2]
FIELDS='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
UNITS={'morning':'schubert-nk-morning-controller.service','api':'schubert-nk-api.service','web':'schubert-nk-web.service','caddy':'caddy.service'}
INFO={'commit':sys.argv[1],'app':'0.1.0-SNAPSHOT','config':'1','schema':'028','protocol':'0.1.0-SNAPSHOT'}
from pg457_stable_actor import stable_actor
from pg462_observer_identity import authenticate_ready
def manager(role):
    raw=subprocess.check_output(['/usr/bin/systemctl','show',UNITS[role],'--property='+FIELDS],text=True,timeout=5)
    values={}
    for line in raw.splitlines():
        key,value=line.split('=',1);assert key not in values;values[key]=value
    assert set(values)==set(FIELDS.split(',')) and values['LoadState']=='loaded';return values
def actor(role):
    return stable_actor(role,manager)
def same(a,b):
    return all(a.get(k)==b.get(k) for k in ('MainPID','InvocationID','startTicks')) and not b.get('race')
def sockets(a,port,host='0100007F'):
    proc=pathlib.Path('/proc')/a['MainPID'];fds=set()
    for fd in (proc/'fd').iterdir():
        try:
            target=str(fd.readlink())
            if target.startswith('socket:['):fds.add(target[8:-1])
        except FileNotFoundError:pass
    result=set()
    for name,address in [('tcp',f'{host}:{port:04X}'),('tcp6',f'0000000000000000FFFF0000{host}:{port:04X}')]:
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
seen=False;roots={};ready=set();proxy=False;prior=None;deadline=time.monotonic()+1900;morning=None
while time.monotonic()<deadline:
    states={role:actor(role) for role in UNITS};m=states['morning']
    # BUG671/YKT476: unstable manager/kernel sandwich is neither a generation proof
    # nor a stable violation. Reobserve before binding the parent or validating a child.
    if m.get('race'):
        time.sleep(.01);continue
    if int(m['MainPID']):
        seen=True
        if morning is None:
            morning=m;deadline=min(deadline,int(m['ExecMainStartTimestampMonotonic'])/1e6+1860)
        assert same(morning,m),'parent generation changed'
    for role in ['api','web']:
        a=states[role]
        if a.get('entry')=='dev.codex.schubert.nk.batch.file.RootServiceLauncher' and not a.get('race') and a['process']['Uid'].split()==['0']*4:
            roots.setdefault(role,a)
        if role not in ready and a.get('entry')=='dev.codex.schubert.nk.'+role+'.bootstrap.'+role.capitalize()+'ProcessMain' and not a.get('race'):
            p=a['process'];account='schubert-'+role
            uid=subprocess.check_output(['id','-u',account],text=True).strip();gid=subprocess.check_output(['id','-g',account],text=True).strip()
            groups=sorted(set(subprocess.check_output(['id','-G',account],text=True).split()),key=int)
            try:
                port=8091 if role=='api' else 8081;before=sockets(a,port)
                if before:
                    health=get(port,'/actuator/health/readiness');info=get(port,'/actuator/info')
                    aa=actor(role);mm=actor('morning')
                    if aa.get('race') or mm.get('race'):continue
                    if authenticate_ready(p,aa.get('process',{}),health,(info[0],json.loads(info[1]) if info[0]==200 else {}),INFO,uid,gid,groups):
                        assert same(a,aa) and same(m,mm) and before.intersection(sockets(aa,port))
                        assert role in roots and same(roots[role],aa),'captured Root-to-ordinary generation missing'
                        ready.add(role)
                        print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready':role,'sameRootOrdinary':True,'sameParent':True,'ownedSocket':True,'info':INFO,'wholeMorningAccepted':False}),flush=True)
            except (OSError,http.client.HTTPException):pass
    key=json.dumps(states,sort_keys=True)
    if key!=prior:
        print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'states':states}),flush=True);prior=key
    if not proxy and ready=={'api','web'}:
        try:
            ca=pathlib.Path('/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt')
            before=ca.stat();context=ssl.create_default_context(cafile=str(ca))
            cc=actor('caddy');owned=sockets(cc,55160,'0F02000A')
            c=http.client.HTTPSConnection('10.0.2.15',55160,timeout=1,context=context)
            try:
                c.request('GET','/login');response=c.getresponse();body=response.read(65537)
                aa=actor('api');ww=actor('web');ccc=actor('caddy')
                zero=all(cc.get('process',{}).get(k)=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
                if response.status==200 and len(body)<=65536 and b'schubert NK' in body and before==ca.stat() and same(states['api'],aa) and same(states['web'],ww) and same(cc,ccc) and owned.intersection(sockets(ccc,55160,'0F02000A')) and zero and cc.get('process',{}).get('NoNewPrivs')=='1':
                    proxy=True
                    print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caddyTlsLogin200':True,'sameApiWeb':True,'sameCaddySocket':True,'caddyZeroCaps':True,'publicCaValidated':True,'bodyLogged':False,'wholeMorningAccepted':False}),flush=True)
            finally:c.close()
        except (OSError,http.client.HTTPException,ssl.SSLError):pass
    if seen and m['MainPID']=='0' and m['ControlPID']=='0' and not m['Job']:
        print(json.dumps({'terminalObserved':True,'parentResult':m['Result'],'parentCode':m['ExecMainCode'],'parentExit':m['ExecMainStatus'],'readyObserved':sorted(ready),'rootsCaptured':sorted(roots),'caddyTlsLogin200':proxy,'backendAlive':{r:states[r]['MainPID']!='0' for r in ('api','web')},'automaticStop':False,'wholeMorningAccepted':False}),flush=True);break
    time.sleep(.05)
else:print(json.dumps({'watchDeadline':True,'readyObserved':sorted(ready),'automaticStop':False,'wholeMorningAccepted':False}),flush=True)
