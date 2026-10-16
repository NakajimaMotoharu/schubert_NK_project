"""Independent current failed PID1/done read and data-only classification; no recovery authority."""
import inspect
import pg4304_current_failed_parent_contract as contract
from pg4260_stable_admission_image import execute,live,SOURCE,BOM

SLOT='pg4302-current-failed-parent-read-v1'


def payload():
    return 'SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\nBINDING='+repr(live())+'\nSLOT='+repr(SLOT)+'\nCONTRACT='+repr(inspect.getsource(contract))+'\n'+BODY


BODY=r'''
from pathlib import Path
import os,hashlib,json,subprocess,stat
require=lambda v:None if v else(_ for _ in()).throw(ValueError('current failed parent read refused'))
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();require(os.geteuid()==0 and boot=='79a3260a-e16d-42bf-942a-b914ed144c28')
manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json');raw=manifest.read_bytes();require(hashlib.sha256(raw).hexdigest()==BOM and json.loads(raw)['source']['commit']==SOURCE)
props='Id,LoadState,ActiveState,SubState,InvocationID,MainPID,ControlPID,Job,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic'
def state():return dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show','schubert-nk-morning-controller.service','--property='+props],text=True,timeout=10).splitlines())
first=state();require(not Path('/proc',str(BINDING['rootPid'])).exists())
args=['journalctl','--boot='+BINDING['boot'],'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+BINDING['invocation'],'-o','json','--no-pager']
journal=subprocess.check_output(args,timeout=15);require(0<len(journal)<=2097152)
def unique(pairs):
 result={}
 for k,v in pairs:
  require(k not in result);result[k]=v
 return result
keys=['MESSAGE_ID','UNIT','INVOCATION_ID','JOB_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP','_PID','_UID','_BOOT_ID']
rows=[{k:v[k]for k in keys if k in v}for v in[json.loads(l,object_pairs_hook=unique)for l in journal.splitlines()]]
donepath=Path('/var/lib/schubert-nk/maintenance/attempts')/(BINDING['activation']+'.done');s=donepath.lstat()
def metadata(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(donepath))
done=donepath.read_bytes();require(metadata(donepath.lstat())==metadata(s))
ns={};exec(CONTRACT,ns);result=ns['classify'](SOURCE,BOM,boot,BINDING,first,rows,done)
group=Path('/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service')
if group.exists():
 for p in[group,*[x for x in group.rglob('*')if x.is_dir()]]:require(not(p/'cgroup.procs').read_text().strip()and 'populated 0\n'in(p/'cgroup.events').read_text())
require(first==state()and manifest.read_bytes()==raw and donepath.read_bytes()==done and metadata(donepath.lstat())==metadata(s))
save=Path('/var/lib/pgpt-s1-preservation')/SLOT;os.umask(0o077);save.mkdir(mode=0o700)
for name,value in [('pid1.private.jsonl',journal),('done.private',done),('parent-state.private.json',json.dumps(first,sort_keys=True).encode())]:
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(value);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'source':SOURCE,'BOM':BOM,'boot':boot,'binding':BINDING,'classification':result,'state':first,'pid1Metadata':rows,'privateJournalSha256':hashlib.sha256(journal).hexdigest(),'rawExported':False,'stateChangingActions':0,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(),60))
