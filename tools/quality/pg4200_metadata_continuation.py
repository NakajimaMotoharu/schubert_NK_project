"""SSC289 new-only single metadata retainer -> unchanged partial/post. No replay of old tools."""
import ast
import base64
import hashlib
import inspect
import json
import os
import shlex
import subprocess
import sys
from pyflakes.api import check
from lan_server import run
import pg3428_vm_candidate_preflight_readonly as identity
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg4168_retained_pair_keeper as predecessor
from pg4176_partial_coordinator import files
from pg4188_exact_partial_recover import bootstrap,process
from pg4182_bounded_pool_coordinator import GUEST as FIXED_TOOLS

SLOT='pg4200-metadata-continuation-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+SLOT
DESIGN_MAIN='e58ce46ac4117caa956583634b40db06d95112c9'


def failed_transport(receipt,terminal):
    if type(receipt)is not dict or type(terminal)is not dict:raise ValueError('two independent receipts required')
    if type(receipt.get('actualExit'))is not int or receipt['actualExit']!=255 or receipt.get('oldParentNormal')is not False or receipt.get('formalAccepted')is not False:
        raise ValueError('preserve original actual transport failure255')
    if receipt.get('source')!='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e' or receipt.get('payloadSha256')!='5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3':raise ValueError('fixed original required')
    if any(terminal.get(k)is not True for k in ['allOldPidsGone','allOldFlocksAdvisory0'])or any(terminal.get(k)is not False for k in ['old4152Normal','oldCloseNormal']):raise ValueError('guest terminal evidence independent of transport')
    return True


def same_retainer(old,now):
    if type(old)is not dict or type(now)is not dict or old!=now:raise ValueError('fresh complete five-FD identity required')
    if (now.get('pid'),now.get('ticks'),now.get('argvSha256'))!=(791348,14602179,'172536db0a293878cb1780e85aa687b825c625a75a9d95fec914ecdf608d1520'):raise ValueError('fixed retained metadata process only')
    if now.get('children')!=[]or now.get('cgroup')!='0::/user.slice/user-1000.slice/session-930.scope\n':raise ValueError('fixed childless metadata scope required')
    a=now.get('authority',{})
    if a.get('PPid')!='791346'or a.get('Uid','').split()!=['0']*4 or a.get('Gid','').split()!=['0']*4 or a.get('Groups','').split()!=['0']or a.get('NoNewPrivs')!='0':raise ValueError('fixed root authority required')
    if a.get('CapInh')!=a.get('CapAmb')or a.get('CapInh')!='0000000000000000'or any(a.get(k)!='000001ffffffffff'for k in ['CapBnd','CapEff','CapPrm']):raise ValueError('fixed capabilities required')
    fds=now.get('fds',{})
    if set(fds)!={'0','1','2','3','4'}:raise ValueError('no unknown FD')
    if [fds[n]['target']for n in ['0','1','2','3','4']]!=['pipe:[12618427]','pipe:[12618428]','pipe:[12618429]','/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0','socket:[12616611]']:raise ValueError('fixed metadata-only FD semantics')
    return True


def payload():
    raw=predecessor.payload();raw=raw[:raw.index('import time,signal,select,ctypes,dbus,traceback')]
    raw=raw.replace("save=base/('pg4180-retained-pair-keeper-v1-'+MODE)","save=base/('"+SLOT+"-'+MODE)")
    ordinary=next(n for n in ast.parse(predecessor.BODY).body if isinstance(n,ast.FunctionDef)and n.name=='ordinary')
    raw+='\n'+inspect.getsource(same_retainer)+'\n'+ast.get_source_segment(predecessor.BODY,ordinary)+'\n'
    hashes={n:hashlib.sha256(t.encode()).hexdigest()for n,t in files().items()}
    programs={k:bootstrap(k,hashes)for k in ['partial.py','post.py']}
    return raw+'\nPROGRAMS='+repr(programs)+'\nFIXED_TOOLS='+repr(FIXED_TOOLS)+'\n'+BODY


BODY=r'''
import dbus,time,signal,select,traceback,subprocess
signed={};exec(SIGNED_SOURCE,signed);pool={};exec(POOL_SOURCE,pool)
materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
reference_raw=Path('/var/lib/pgpt-s1-preservation/pg4196-partial-handoff-read-v1/observed.private.json').read_bytes()
require(hashlib.sha256(reference_raw).hexdigest()=='6758d930bc6fb6b295274a05d4b58aba7b535909af8f263afe05f0ff43eecef6');reference=json.loads(reference_raw)
def record(name,value):
 require('/'not in name)
 encoded=json.dumps(value,sort_keys=True).encode()
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return hashlib.sha256(encoded).hexdigest()
def invariant():
 require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
 require(not Path('/proc/790010').exists()and not Path('/proc/789928').exists())
 current=snapshot();expected=reference['current']
 for key in ['units','actors','durable','native','startup','runtime']:require(current[key]==expected[key])
 require(current['database']['rows']==expected['database']['rows']and not current['flocks']);ordinary(current)
 configuration=config();require(set(configuration)==set(reference['configuration']))
 require(all(CONFIG_CONTRACT['same'](reference['configuration'][u],v,exec_record)for u,v in configuration.items()))
 return current
def verify(pid,ticks):
 require((pid,ticks)==(791348,14602179));p=proc(pid);same_retainer(reference['keeper'],p)
 require(sorted(int(t.name)for t in Path('/proc/791348/task').iterdir())==[791348])
 require(Path('/proc/791348/exe').resolve()==Path('/usr/bin/python3').resolve()and Path('/proc/791348/root').readlink()==Path('/'))
 invariant();return p
def reserve(pid,value):
 record(str(pid)+'.term-reserved.private.json',{'pid':pid,'ticks':value['ticks'],'actor':value,'signal':'TERM','replayAllowed':False});require(verify(pid,value['ticks'])==value)
def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
def job(name,mode,label):
 with(save/(label+'.stdout.private.log')).open('xb')as output,(save/(label+'.stderr.private.log')).open('xb')as error:
  child=subprocess.Popen(['/usr/bin/python3','-B','-c',PROGRAMS[name]]+([mode]if mode else[]),stdin=subprocess.DEVNULL,stdout=output,stderr=error)
  record(label+'.process.private.json',{'pid':child.pid,'actor':proc(child.pid)})
  code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
 content=(save/(label+'.stdout.private.log')).read_bytes();record(label+'.exit.safe.json',{'actualExit':code,'stdoutSha256':hashlib.sha256(content).hexdigest()})
 require(code==0);value=json.loads(content.splitlines()[-1]);require(value['actualExit']==0 and value['source']==data['source']['commit']);return value
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[];issued=False
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 first=verify(791348,14602179);second=verify(791348,14602179);require(first==second)
 proof=record('proof.private.json',{'keeper':first,'current':invariant(),'old4152Normal':False})
 if MODE=='recover':
  issued=True;terminate(791348,14602179,verify,reserve,os.pidfd_open,send,wait,os.close)
  deadline=time.monotonic()+30
  while Path('/proc/791348').exists():require(time.monotonic()<deadline);time.sleep(.05)
  invariant();record('old-metadata-gone.private.json',{'oldRetainerGone':True,'oldRetainerNormalClose':False,'signalsIssued':1,'allOriginalPairGone':True})
  inspect_result=job('partial.py','inspect','partial-inspect');require(inspect_result['newScopeNormalClose']is True)
  result=job('partial.py','recover','partial-recover');require(result['newStopCount']==5 and result['caddyPriorStopAuthenticated']is True and result['old4152Normal']is False and result['recoverySixNormal']is True)
  post_result=job('post.py',None,'independent-post');require(post_result['newMARDDBTenRefNormalClose']is True and post_result['independentFailedDoneRecoveryPost']is True)
except BaseException as failure:
 if issued:
  try:record('failure.private.json',{'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]})
  except OSError:pass
  # No output-dependent escape: EPIPE cannot discard the retained metadata scope.
  try:print('SSC289_UNKNOWN metadataRetained=true',flush=True)
  except OSError:pass
  while True:time.sleep(1)
 raise
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':0,'source':data['source']['commit'],'boot':boot,'BOM':sha,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':MODE,'signalsIssued':1 if issued else 0,
 'old4152TransportExit':255,'old4152Normal':False,'oldMetadataCloseNormal':False,'newTenRefsNormalClose':True,
 'proofSha256':proof,'businessStopsIssued':5 if issued else 0,'caddyStopsReissued':0,'formalAccepted':False}
if MODE=='recover':value.update(partialInspect=inspect_result,partialRecover=result,independentPost=post_result)
record('manifest.safe.json',value);print(json.dumps(value))
'''


def main():
    if sys.argv[1:]not in (['stage'],['proof'],['recover']):raise SystemExit('one fixed action')
    mode=sys.argv[1];os.umask(0o077);out=W/(SLOT+'-'+mode)
    receipt=json.loads((W/'pg4152-exact-failed-done-recover-v1/manifest.safe.json').read_bytes())
    observed=json.loads((W/'pg4196-partial-handoff-read-v1/manifest.safe.json').read_bytes())
    if observed['actualExit']!=0 or observed['result']['oldPairGone']is not True:raise ValueError('fresh actual pair disappearance first')
    # Concrete guest terminal receipt is bound to the private4196 digest inside payload.
    failed_transport(receipt,{'allOldPidsGone':True,'allOldFlocksAdvisory0':observed['result']['oldManagementLocksAdvisory0'],'old4152Normal':False,'oldCloseNormal':False})
    raw=payload();digest=hashlib.sha256(raw.encode()).hexdigest()
    if check(raw,'<SSC289 full continuation>'):raise ValueError('complete emitted static closure required')
    if mode=='recover':
        if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
        subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
        for doc in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
            if subprocess.check_output(['git','show','origin/main:'+doc])!=subprocess.check_output(['git','show',DESIGN_MAIN+':'+doc]):raise ValueError('final published SSC289 changed; review first')
        proof=json.loads((W/(SLOT+'-proof')/'manifest.safe.json').read_bytes())
        if proof['actualExit']!=0 or proof['payloadSha256']!=digest or proof['result']['signalsIssued']!=0:raise ValueError('same-source actual no-signal qualification first')
        if process(20445)!={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:raise ValueError('same pinned forward required')
        code,text=run(identity.HOST,timeout=30)
        if code!=0 or json.loads(text)['boot']!='c7964823-c628-4ef2-99b5-07b0f0b62bba':raise ValueError('fresh same host VM ownership required')
    out.mkdir(mode=0o700)
    with management_gate(P/'current-management-critical.lock'):
        if mode=='stage':
            stage="import pathlib,base64,os,hashlib,json; assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28' and pathlib.Path('/opt/schubert-nk/current').resolve()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG3976'); os.umask(0o077); root=pathlib.Path("+repr(GUEST)+"); root.mkdir(mode=0o700); p=root/'continuation.py'; raw=base64.b64decode("+repr(base64.b64encode(raw.encode()).decode())+"); compile(raw,str(p),'exec')\nwith p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())\np.chmod(0o400)\nfd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)\nprint(json.dumps({'actualExit':0,'payloadSha256':hashlib.sha256(raw).hexdigest()}))"
            command=SSH+['sudo','-n','python3','-B','-'];stdin=stage.encode()
        else:
            stage=json.loads((W/(SLOT+'-stage')/'manifest.safe.json').read_bytes())
            if stage['actualExit']!=0 or stage['payloadSha256']!=digest:raise ValueError('fixed staged envelope required')
            code="import pathlib,hashlib,stat,os; p=pathlib.Path("+repr(GUEST+'/continuation.py')+"); s=p.lstat(); assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p); raw=p.read_bytes(); assert hashlib.sha256(raw).hexdigest()=="+repr(digest)+"; exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})"
            command=SSH+[shlex.join(['sudo','-n','python3','-B','-c',code,mode])];stdin=None
        (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','payloadSha256':digest,'mode':mode,'replayAllowed':False}))
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(command,stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,stdout=output,stderr=error)
            (out/'ssh.private.json').write_text(json.dumps(process(child.pid)))
            if stdin is not None:child.stdin.write(stdin);child.stdin.close()
            code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','payloadSha256':digest,'mode':mode,'old4152Normal':False,'formalAccepted':False}
    if code==0:value['result']=json.loads((out/'stdout.private.log').read_bytes().splitlines()[-1])
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
