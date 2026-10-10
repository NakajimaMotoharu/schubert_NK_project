"""Fresh legal noargs current before; preserve all rows/native, never edit history."""
import inspect
import pg1222_completed_retirement_preflight as transport
import pg1236_completed_runtime_retired_post as previous
from pg870_ordinary_policy import ordinary_argv

def payload():
    s=previous.payload();s=s[:s.index("save=base/'pg1236-completed-runtime-retired-post-v1'")]
    s=s.replace("'run':'PG1236-completed-runtime-retired-post-v1'","'run':'PG1238-fresh-day-ordinary-before-v1'")
    s+='\n'+inspect.getsource(ordinary_argv)+'\n'+BODY
    compile(s,'<actual fresh ordinary source and new day before>','exec');return s

BODY=r'''
morning='schubert-nk-morning-controller.service'
base_bytes=(release/'systemd/schubert-nk-morning-controller.service').read_bytes()
native_bytes=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes()
argv=ordinary_argv(base_bytes,native_bytes);declaration=env['exec_record'](after['configuration'][morning]['ExecStart'])
require(declaration is not None and declaration[:3]==('/usr/bin/java',argv,'no')and '--resume'not in argv)
require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()and not pathlib.Path(retirement.TARGET).exists())
day=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat();require(day>'2026-10-10')
same_day=[r for r in after['rows']['schubert.batch_runs']if r['business_date']==day and r['step']=='CLEAN_INBOX_OUTBOX'and r['status']in ['SUCCESS','WARNING']]
require(not same_day)
available={str(p):os.statvfs(p).f_bavail*os.statvfs(p).f_frsize for p in [base,pathlib.Path('/srv/schubert-nk/backup')]}
require(min(available.values())>=805306368)
save=base/'pg1238-fresh-day-ordinary-before-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'current':after,'native':native,'ordinaryNoargs':True,'newJstDate':day,'existingSuccessfulInspectorStepsForDate':0,'availableBytes':available,'requiredGuestWriteAndCloseBytes':805306368}
blob=json.dumps(value,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result.update(privateBeforeSha256=hashlib.sha256(blob).hexdigest(),ordinaryNoargs=True,newJstDate=day,existingSuccessfulInspectorStepsForDate=0,guestAvailableBytes=available,requiredGuestWriteAndCloseBytes=805306368,newMetadataNormalClose=True,starts0=True)
result.pop('proofHashes',None);result.pop('toolHashes',None)
print(json.dumps(result))
'''

def main():
    # Current retired post has a different immutable tool scope from1222.
    entry=inspect.getsource(previous.main).replace('pg1236-completed-runtime-retired-post-v1','pg1238-fresh-day-ordinary-before-v1')
    env=dict(previous.__dict__);env['payload']=payload
    exec(compile(entry,'<fresh ordinary full before transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
