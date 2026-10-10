"""New full before for legal ordinary noargs; no fabricated new-day requirements."""
import inspect
import pg1315_ordinary_publication_independent_post as previous
from pg870_ordinary_policy import ordinary_argv

BODY=r'''
parser_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
n=next(n for n in ast.parse(parser_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re}
exec(compile(ast.Module(body=[n],type_ignores=[]),'<strict actual declaration parser>','exec'),env)
morning='schubert-nk-morning-controller.service'
base_bytes=(release/'systemd/schubert-nk-morning-controller.service').read_bytes()
native_bytes=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes()
argv=ordinary_argv(base_bytes,native_bytes);declaration=env['exec_record'](pub_after['configuration'][morning]['ExecStart'])
require(declaration is not None and declaration[:3]==('/usr/bin/java',argv,'no')and '--resume'not in argv)
require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg492-once-resume.conf').exists())
day=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
same_day=[r for r in pub_after['rows']['schubert.batch_runs']if r['business_date']==day and r['step']=='CLEAN_INBOX_OUTBOX'and r['status']in ['SUCCESS','WARNING']]
available={str(p):os.statvfs(p).f_bavail*os.statvfs(p).f_frsize for p in [base,pathlib.Path('/srv/schubert-nk/backup')]}
require(min(available.values())>=805306368)
save=base/'pg1319-published-ordinary-before-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'current':pub_after,'native':native,'ordinaryNoargs':True,'jstDate':day,'existingSuccessfulInspectorStepsForDate':len(same_day),'availableBytes':available,'requiredGuestWriteAndCloseBytes':805306368}
blob=json.dumps(value,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result.update(run='PG1319-published-ordinary-before-v1',privateBeforeSha256=hashlib.sha256(blob).hexdigest(),ordinaryNoargs=True,jstDate=day,existingSuccessfulInspectorStepsForDate=len(same_day),guestAvailableBytes=available,requiredGuestWriteAndCloseBytes=805306368,newMetadataNormalClose=True,starts0=True,oldRootAuthorityIsNotNewSourceRootDone=True)
result.pop('proofHashes',None);result.pop('toolHashes',None)
print(json.dumps(result))
'''


def payload():
    code=previous.payload()
    if code.count('print(json.dumps(result))')!=1:raise ValueError('closed independent observation result required')
    code=code.replace('print(json.dumps(result))','')+'\n'+inspect.getsource(ordinary_argv)+'\n'+BODY
    compile(code,'<new source ordinary before>','exec');return code


def main():
    env=dict(previous.__dict__);env['payload']=payload
    code=inspect.getsource(previous.main).replace('pg1315-ordinary-publication-independent-v1','pg1319-published-ordinary-before-v1')
    exec(compile(code,'<new-only full before transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
