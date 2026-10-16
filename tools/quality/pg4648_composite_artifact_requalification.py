"""Fresh current/normalRef qualification of original three sealed images, not original exit0."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg4584_current_admission_image as admission
import pg4586_current_independent_acceptance as acceptance
from pg4442_failed_current_view_qualification import strict_equal
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg4152_exact_failed_done_recover import process

SLOT='pg4648-composite-artifact-qualified-v1'
IMAGE_SHA='2dee082d8630da377e47d2be284442cfa396c083d1444386729f37d9f6c0136e'


def helpers():
    raw=acceptance.seal_payload(admission.live(),admission.before());nodes=ast.parse(raw).body;selected=[]
    constants={'CAPTURE_BOUND','CONFIG_CONTRACT','CONFIG_FIELDS'}
    names={'require','command','metadata','tree','configuration_value','complete_configuration','exec_record','kernel_empty'}
    for n in nodes:
        take=isinstance(n,ast.FunctionDef)and n.name in names
        take|=isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in constants for t in n.targets)
        take|=isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='exec'and any(isinstance(v,ast.Name)and v.id in constants for v in n.value.args)
        if take:selected.append(ast.get_source_segment(raw,n))
    return '\n'.join(selected)+'\n'+inspect.getsource(strict_equal)


BODY=r'''
import dbus,datetime,hashlib,json,os,pathlib,re,stat,subprocess
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');os.umask(0o077);save=base/SLOT;require(not os.path.lexists(save));save.mkdir(mode=0o700)
def persist(name,blob):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def private(path):
 s=path.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(path));require(0<s.st_size<=67108864)
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  blob=os.pread(fd,s.st_size+1,0);require(len(blob)==s.st_size and metadata(path)==metadata_from_stat(s)and metadata_from_stat(os.fstat(fd))==metadata_from_stat(s))
 finally:os.close(fd)
 return blob
def metadata_from_stat(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
persist('owner.private.json',json.dumps({'pid':os.getpid(),'ppid':os.getppid(),'ticks':int(pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256(pathlib.Path('/proc/self/cmdline').read_bytes()).hexdigest(),'source':SOURCE,'originalExitUnknown':True,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},sort_keys=True).encode())
others=[]
for proc in pathlib.Path('/proc').iterdir():
 if not proc.name.isdecimal()or int(proc.name)==os.getpid():continue
 try:
  args=(proc/'cmdline').read_bytes().split(b'\0')
  if len(args)==4 and args[0]in [b'python3',b'/usr/bin/python3',b'python3.14',b'/usr/bin/python3.14']and args[1:]==[b'-B',b'-',b'']:others.append(int(proc.name))
 except(FileNotFoundError,ProcessLookupError):continue
persist('other-readers.private.json',json.dumps({'otherStdinPythonPids':others,'ownPid':os.getpid()}).encode());require(not others)
paths=[base/'pg4606-current-browser-composite-v1/before.private.json',*[base/'pg4606-current-browser-composite-v1-raw'/('complete-'+n+'.private')for n in ['first','second','final']]]
original=None
for path in paths:
 blob=private(path);require(hashlib.sha256(blob).hexdigest()==IMAGE_SHA)
 if original is None:original=blob
 else:require(blob==original)
image=json.loads(original);require(image['source']==SOURCE and image['manifestSha256']==BOM and image['run']==BINDING['run']and image['cutoff']==BINDING['cutoff']and image['activation']==BINDING['activation'])
require(image['businessOracle']['exactRootBrowserCurrentChain']is True and image['genuineCompletion']['genuineRootDone']is True and image['genuineCompletion']['completionCode']==10)
canonical=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
root_prefix=private(base/'pg4642-current-whole-seal-v1/before.private.json');require(hashlib.sha256(root_prefix).hexdigest()=='78fd9fe88e1dca5e24cbd8de86e8df3d28449be8e337340b7a628269595f0abc')
root_prefix=json.loads(root_prefix);require(root_prefix['source']==SOURCE and root_prefix['manifestSha256']==BOM and root_prefix['run']==BINDING['run']and canonical(root_prefix['rows'])==BROWSER_BEFORE_ROWS_SHA)
require(canonical(image['rows'])==BROWSER_AFTER_ROWS_SHA)
proof={};exec(GUARD,proof);require(strict_equal(proof['result'],image['genuineCompletion'])and strict_equal(proof['rows'],image['pid1']))
persist('before.private.json',original)
FIELDS=set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
require(len(image['units'])==10 and len(image['actors'])==4 and set(image['configuration'])==set(image['units']))
for row in image['units'].values():require(set(row)==FIELDS and all(type(v)is str for v in row.values()))
def show(unit):
 lines=command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],1048576).decode().splitlines();pairs=[v.split('=',1)for v in lines];v=dict(pairs)
 require(len(pairs)==len(v)and set(v)==FIELDS);return v
def current(label):
 units={u:show(u)for u in image['units']};require(strict_equal(units,image['units']));actors={}
 for unit,expected in image['actors'].items():
  pid=units[unit]['MainPID'];p=pathlib.Path('/proc')/pid;v=(p/'stat').read_text().rsplit(')',1)[1].split()
  status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
  actor={'ticks':int(v[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'cgroup':(p/'cgroup').read_text(),'process':{k:status[k].strip()for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']}}
  require(strict_equal(actor,expected));actors[unit]=actor
 for unit in set(units)-set(actors):kernel_empty(unit)
 configuration={u:complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode(),u)for u in units}
 for unit,value in configuration.items():require(CONFIG_CONTRACT['same'](image['configuration'][unit],value,exec_record))
 sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
 for table in image['rows']:
  require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
 sql+='commit;';r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=30)
 persist(label+'-sql.private.jsonl',r.stdout);persist(label+'-sql-error.private.log',r.stderr);require(r.returncode==0 and 0<len(r.stdout)<=67108864)
 rows={}
 for line in r.stdout.splitlines():
  value=json.loads(line);require(value['table']not in rows);rows[value['table']]=value['rows']
 persist(label+'-rows.private.json',json.dumps(rows,sort_keys=True).encode());require(strict_equal(rows,image['rows'])and len(rows)==24)
 files={}
 for path in image['unitFiles']:
  p=pathlib.Path(path);m=metadata(p);files[path]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(metadata(p)==m)
 durable={k:tree(pathlib.Path(os.path.commonpath(list(value))))for k,value in image['durable'].items()}
 runtime=tree(pathlib.Path('/run/systemd/system'));startup=tree(pathlib.Path('/run/schubert-nk/startup'));native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 actual={'unitFiles':files,'durable':durable,'runtime':runtime,'startup':startup,'native':native}
 persist(label+'-all-protected.private.json',json.dumps(actual,sort_keys=True).encode())
 for name,value in actual.items():require(strict_equal(value,image[name]))
 release=pathlib.Path('/opt/schubert-nk/current');raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==BOM and json.loads(raw)['source']['commit']==SOURCE and str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG4432')
 for record in json.loads(raw)['artifacts']:
  p=release/record['path'];m=metadata(p);require(m[6]==record['size']and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']and metadata(p)==m)
 command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg4432-manifest.sig')],4096)
 require(strict_equal(units,{u:show(u)for u in units}))
 return {unit:[units[unit]['MainPID'],units[unit]['InvocationID'],v['ticks'],v['argvSha256']]for unit,v in actors.items()}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
code=1;error_type=None;observed=None
try:
 for unit in sorted(image['units']):manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 observed=current('first');require(strict_equal(observed,current('second')))
 code=0
except Exception as error:error_type=type(error).__name__
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':code,'productionSource':SOURCE,'privateBeforeSha256':IMAGE_SHA,'currentFourOwnedLive':code==0,'observedOwned':observed,'genuineCompletion':image['genuineCompletion'],'doneEndUtc':image['doneEndUtc'],'sqlOracleQualified':code==0,'businessOracle':image['businessOracle'],
 'normalMetadataReferences':True,'newTenRefsNormalClose':len(refs)==10,'originalCompositeExitUnknown':True,'oldUnknownNormalized':False,'originalCompositeReplayed':False,'oldReadPythonAbsent':not others,'savedThreeImagesRequalified':code==0,'freshCurrentAll24AndOriginalsUnchanged':code==0,'sourceQualified':True,'errorType':error_type,'formalAccepted':False,'startsStopsSignalsSqlWrites0':True,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
# This durable receipt exists only AFTER every new Ref and bus close returned.
persist('terminal.safe.json',json.dumps(value,sort_keys=True).encode());print(json.dumps(value));raise SystemExit(code)
'''


def payload():
    term=acceptance.terminal_payload(admission.live());marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+acceptance.TERM+"')"
    if term.count(marker)!=1:raise ValueError('one qualified genuine prefix')
    cases=W/'pg4604-current-same-owner-browser-v1/cases'
    def row_sha(name):
        value=json.loads((cases/(name+'-rows.private.json')).read_bytes())
        return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    raw='SOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\nSLOT='+repr(SLOT)+'\nIMAGE_SHA='+repr(IMAGE_SHA)+'\nBINDING='+repr(admission.live())+'\nBROWSER_BEFORE_ROWS_SHA='+repr(row_sha('before'))+'\nBROWSER_AFTER_ROWS_SHA='+repr(row_sha('after'))+'\nGUARD='+repr(term[:term.index(marker)])+'\n'+helpers()+'\n'+BODY
    if check(raw,'<small current artifact qualification and fresh normal scope>'):raise ValueError('full emitted static0')
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed artifact qualifier first')
    browser=json.loads((W/'pg4604-current-same-owner-browser-v1/manifest.safe.json').read_bytes())
    if browser['actualExit']!=0 or browser['productionSource']!=admission.SOURCE or not(browser['sourceQualified']and browser['passedCases']==12 and browser['all24IndependentPost']and browser['sameFourOrdinaryOwnersBeforeAfter']):raise ValueError('same-source original real Browser12/current owners required')
    original=W/'pg4606-current-browser-composite-v1/payload.private.py'
    if original.stat().st_size!=86888040 or hashlib.sha256(original.read_bytes()).hexdigest()!='553b1e60bc711c7d8e79dcd8ce2fbd72f04887a042871c43abaab096beefb314':raise ValueError('original timedout payload unchanged')
    raw=payload();admission.authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'ssh':process(child.pid),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'source':admission.SOURCE,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'replayAllowed':False,'oldCompositeNotReplayed':True}))
            child.stdin.write(raw.encode());child.stdin.close();code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':admission.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False,'oldCompositeExitUnknown':True,'oldCompositeReplayed':False}
    if code==0:value['result']=json.loads((out/'stdout.private.log').read_bytes())
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
