"""Current guest processes/output of the original composite; read only, never resend payload."""
import pg4584_current_admission_image as admission

SLOT='pg4646-composite-current-observation-v1'


def payload():
    return 'SOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+r'''
import datetime,hashlib,json,os,pathlib,stat
require=lambda v:None if v else(_ for _ in()).throw(ValueError('current composite observation refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
processes=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdecimal()or int(p.name)==os.getpid():continue
 try:
  argv=(p/'cmdline').read_bytes()
  if not(argv.startswith(b'python3\0-B\0-\0')or argv.startswith(b'sudo\0-n\0python3\0-B\0-\0')):continue
  status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l);fds=[]
  for f in(p/'fd').iterdir():
   try:
    s=f.stat();fds.append({'fd':int(f.name),'target':str(f.readlink()),'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'fdinfo':(p/'fdinfo'/f.name).read_text()})
   except(FileNotFoundError,ProcessLookupError):fds.append({'fd':int(f.name),'raced':True})
  values=(p/'stat').read_text().rsplit(')',1)[1].split()
  processes.append({'pid':int(p.name),'ppid':int(values[1]),'ticks':int(values[19]),'state':values[0],'argvSha256':hashlib.sha256(argv).hexdigest(),'exe':str((p/'exe').readlink()),'cgroup':(p/'cgroup').read_text(),'uids':status['Uid'].split(),'gids':status['Gid'].split(),'fds':fds})
 except(FileNotFoundError,ProcessLookupError):continue
base=pathlib.Path('/var/lib/pgpt-s1-preservation');outputs={}
for name in ['pg4606-current-browser-composite-v1','pg4606-current-browser-composite-v1-raw']:
 root=base/name;items={}
 if os.path.lexists(root):
  require(root.is_dir()and not root.is_symlink())
  for p in root.iterdir():
   s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1))
   items[p.name]={'bytes':s.st_size,'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 outputs[name]={'exists':root.exists(),'files':items}
value={'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':SOURCE,'processes':processes,'outputs':outputs,'startsStopsSignals':0,'originalCompositeExitUnknown':True,'formalAccepted':False}
out=base/'pg4646-composite-current-observation-v1';os.umask(0o077);out.mkdir(mode=0o700)
with(out/'observed.private.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'source':SOURCE,'observedUTC':value['observedUTC'],'candidateProcesses':[{'pid':p['pid'],'ppid':p['ppid'],'ticks':p['ticks'],'argvSha256':p['argvSha256'],'state':p['state'],'fds':len(p['fds'])}for p in processes],
 'outputs':{n:{'exists':v['exists'],'files':{k:{'bytes':s['bytes'],'sha256':s['sha256']}for k,s in v['files'].items()}}for n,v in outputs.items()},'signalsStartsStops':0,'originalCompositeExitUnknown':True,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(),60))
