"""Independent once-only postcondition capture after783 normal existing-pair retirement."""
import inspect
from pathlib import Path
from pg784_stopped_baseline import main as prior_main
from pg785_exec_history import accepted

R=Path(__file__).resolve().parent


def preserved(before,after):
    import copy
    left=copy.deepcopy(before);right=copy.deepcopy(after);root='/run/schubert-nk/startup'
    intents={root+'/permit-start.intent',root+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent',root+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent'}
    if not intents<=set(left['trees'][root])or set(right['trees'][root])!=set(left['trees'][root])-intents:return False
    for name in intents:left['trees'][root].pop(name)
    if left['trees'][root][root]['metadata'][:6]!=right['trees'][root][root]['metadata'][:6]:return False
    right['trees'][root][root]=left['trees'][root][root]
    return left==right


PAYLOAD=r'''
import sys,pathlib,json,os,hashlib,ast,re,stat
os.umask(0o077);assert os.geteuid()==0
base=pathlib.Path('/var/lib/pgpt-s1-preservation');retired=base/'pg783-existing-pair-retire-v1'
pins={'snapshot-before.private.json':'b6165c75ccc067991654d0b43db272096fc05019029d7e15e31af157cf35ad23','units-before.private.json':'c5253c6d1e8c842e944b85b9f4a3e6d7c1f5ccd0ac947c6d5bf2333285e40da5','complete.private':'25a2f3f50701e1613a8add466d70410369427248ce541e00b0a717644e745c26','retired.private.json':'10e852955793564cee0cab836930326aadf0b3ca24b374a71cf60ad841121ed7'}
for name,digest in pins.items():assert hashlib.sha256((retired/name).read_bytes()).hexdigest()==digest
old=json.loads((retired/'snapshot-before.private.json').read_bytes());closed=json.loads((retired/'units-before.private.json').read_bytes())
sys.path.insert(0,str(base/'pg783-existing-pair-tools-v1'));import pg783_owned as h
from pg777_reference_capability import CaptureReferences
h.load_definitions();h.parent();save=base/'pg787-retired-post-v1';assert not os.path.lexists(save)
policy=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();assert hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4'
definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re};exec(compile(ast.Module(body=[definition],type_ignores=[]),'<strict declaration>','exec'),env)
observed={}
def configuration(unit):
 actual=h.complete_configuration(h.command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),unit)
 expected=old['configuration'][unit];left=env['exec_record'](expected['ExecStart']);right=env['exec_record'](actual['ExecStart'])
 assert accepted(left,right,h.show(unit),closed[unit]);assert all(actual[k]==expected[k]for k in actual if k!='ExecStart')
 observed[unit]=actual;value=dict(actual);value['ExecStart']=expected['ExecStart'];return value
h.configuration=configuration
def resources():
 for u in h.ORDER+h.EXTRA:
  v=h.show(u);assert v['MainPID']==v['ControlPID']=='0'and v['Job']==''and v['ActiveState']in ('inactive','failed');h.kernel_empty(u)
 for proc in pathlib.Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:args=(proc/'cmdline').read_bytes().split(b'\0')
  except(FileNotFoundError,PermissionError,ProcessLookupError):continue
  assert b'Pg783ExistingPairRetirement'not in args and not any(a.endswith(b'/pg783_refs.py')for a in args)
 for name in ('maintenance.lock','startup-admission.lock'):
  s=(pathlib.Path('/run/schubert-nk')/name).lstat();assert s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   fields=line.split()
   if len(fields)<8:continue
   d=fields[5].split(':')
   assert len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino)
 db=h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"])
 assert db.splitlines()==[b'0',b'0'];h.parent()
with CaptureReferences():
 after=h.snapshot();assert after==h.snapshot()and preserved(old,after);resources()
 assert len(after['rows'])==24 and len(after['rows']['schubert.batch_runs'])==544
 assert len(after['trees']['/run/schubert-nk/startup'])==40
 assert h.epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True)
 save.mkdir(mode=0o700)
 for name,value in [('after.private.json',after),('observed-configuration.private.json',observed)]:
  with(save/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
resources()
for directory in(save,save.parent):
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'readonly':True,'allTenKernel0':True,'all24Preserved':True,'batchRows':544,'startupEntries':39,'sameEpochInvalid':True,'oldCloseUnknown':True,'newScopesReturnedNormally':True,'newOwnerGone':True,'databaseSessions0':True,'advisory0':True,'M_A_OFD0':True,'snapshotSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest()}))
'''


if __name__=='__main__':
    raw=inspect.getsource(prior_main).replace('pg784-stopped-current-v1','pg787-retired-post-v1')
    payload=inspect.getsource(accepted)+'\n'+inspect.getsource(preserved)+'\n'+PAYLOAD
    import pg784_stopped_baseline as previous
    context={**previous.__dict__,'PAYLOAD':payload}
    exec(compile(raw,'<new787 independent post capture>','exec'),context);context['main']()
