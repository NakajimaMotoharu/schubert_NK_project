"""One QMP grow and one root partition/filesystem grow, never reboot/shrink/raw copy."""
import datetime
import hashlib
import json
import os
import selectors
import shlex
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from lan_server import run

SLOT='pg2012-online-capacity-grow-v1'
NEW_SIZE=48*1024**3

LAN=r'''
import hashlib,json,os,pathlib,socket,struct
disk=pathlib.Path('/home/mini/schubert-nk-pgpt/vm/pg1435-cold-v1/active.qcow2');sock=disk.parent/'qmp.sock';proc=pathlib.Path('/proc/13204')
assert os.geteuid()==0 and proc.exists()and str((proc/'exe').readlink())=='/usr/bin/qemu-system-x86_64'
argv=(proc/'cmdline').read_bytes();assert b'file='+str(disk).encode()+b',if=virtio,format=qcow2' in argv
tick=int((proc/'stat').read_text().rpartition(')')[2].split()[19]);inode=disk.stat().st_ino
assert os.statvfs(disk.parent).f_bavail*os.statvfs(disk.parent).f_frsize>=20*1024**3
root=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2012-grow-v1');assert not os.path.lexists(root);root.mkdir(mode=0o700)
def persist(name,value):
 with(root/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
s=socket.socket(socket.AF_UNIX);s.settimeout(15);s.connect(str(sock));assert struct.unpack('3i',s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))==(13204,0,0)
f=s.makefile('rwb',buffering=0);g=json.loads(f.readline(65537));assert g['QMP']['version']['qemu']=={'major':10,'minor':2,'micro':1}
def rpc(command,arguments=None):
 message={'execute':command,'id':command}
 if arguments is not None:message['arguments']=arguments
 f.write((json.dumps(message)+'\n').encode())
 for _ in range(16):
  raw=f.readline(65537);assert 0<len(raw)<=65536;value=json.loads(raw)
  if value.get('id')==command:assert 'error'not in value;return value['return']
  assert 'event'in value
 raise ValueError('bounded QMP reply refused')
assert rpc('qmp_capabilities')=={}and rpc('query-status')['status']=='running'and rpc('query-block-jobs')==[]
before=rpc('query-block');matches=[x for x in before if x['device']=='virtio0'];assert len(matches)==1
old=matches[0]['inserted'];assert old['file']==str(disk)and old['drv']=='qcow2'and old['ro']is False and old['image']['virtual-size']==42949672960 and old['image']['backing-image']['virtual-size']==42949672960 and old['backing_file']=='/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2'and old['image']['format-specific']['data']['corrupt']is False
persist('before.private.json',{'blocks':before,'pid':13204,'ticks':tick,'diskInode':inode,'argvSha256':hashlib.sha256(argv).hexdigest()})
persist('block-resize-once.private',{'device':'virtio0','oldSize':42949672960,'newSize':51539607552,'repeatForbidden':True,'shrinkForbidden':True})
assert rpc('block_resize',{'device':'virtio0','size':51539607552})=={}
after=rpc('query-block');new=next(x for x in after if x['device']=='virtio0')['inserted'];assert new['image']['virtual-size']==51539607552 and new['file']==old['file']and new['backing_file']==old['backing_file']and new['image']['backing-image']==old['image']['backing-image']
assert disk.stat().st_ino==inode and int((proc/'stat').read_text().rpartition(')')[2].split()[19])==tick and(proc/'cmdline').read_bytes()==argv
persist('after.private.json',{'blocks':after,'samePidTicksInode':True});f.close();s.close()
print(json.dumps({'qmpGrowExit':0,'samePidTicksInode':True,'virtualBytesBefore':42949672960,'virtualBytesAfter':51539607552,'backingUnchanged':True,'noRebootCopyShrink':True,'rootPrivateSlot':str(root)}))
'''

GUEST=r'''
import fcntl,json,os,pathlib,stat,subprocess,sys,time
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846')
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2012-online-grow-v1');assert not os.path.lexists(root);root.mkdir(mode=0o700)
def persist(name,value):
 with(root/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def command(args):
 r=subprocess.run(args,capture_output=True,timeout=120);persist('command-'+args[0].rsplit('/',1)[-1]+'.private.json',{'argv':args,'exit':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()});assert r.returncode==0;return r.stdout
def table():return json.loads(subprocess.check_output(['/usr/sbin/sfdisk','--json','/dev/vda'],timeout=10))['partitiontable']
def quiescent():
 units=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
 for unit in units:
  raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'--property=MainPID,ControlPID,Job'],text=True,timeout=10);v=dict(x.split('=',1)for x in raw.splitlines());assert v=={'MainPID':'0','ControlPID':'0','Job':''}
  p=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
  if p.exists():assert all(not(d/'cgroup.procs').read_text().strip()for d in[p,*[d for d in p.rglob('*')if d.is_dir()]])
held=[]
try:
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);held.append(fd);s=os.fstat(fd);assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 quiescent()
 before=table();assert before['label']=='gpt'and before['id']=='D1D80BB0-6CC8-4F75-96D7-429EFFC6A7E7'and before['sectorsize']==512
 old=next(p for p in before['partitions']if p['node']=='/dev/vda1');assert old['start']==2324480 and old['size']==81561567 and old['uuid']=='F8A5DEDF-C7D3-42EA-96AA-30C2DB90705C'
 persist('partition-before.private.json',before)
 print('CURRENT_LOCKED_QUIESCENT_READY',flush=True)
 assert sys.stdin.readline()=='QMP_GROW_CONFIRMED\n'
 for _ in range(100):
  size=subprocess.check_output(['/usr/sbin/blockdev','--getsize64','/dev/vda'],text=True).strip();assert size in {'42949672960','51539607552'}
  if size=='51539607552':break
  time.sleep(.05)
 else:raise ValueError('bounded kernel capacity event unavailable')
 quiescent();persist('growpart-once.private',{'device':'/dev/vda','partition':1,'noRepeat':True});command(['/usr/bin/growpart','/dev/vda','1'])
 after=table();new=next(p for p in after['partitions']if p['node']=='/dev/vda1');assert set(new)==set(old)and all(new[k]==old[k]for k in old if k!='size')and new['size']==old['size']+16777216
 assert set(after)==set(before)and all(after[k]==before[k]for k in before if k not in {'lastlba','partitions'})and after['lastlba']==before['lastlba']+16777216
 assert[ p for p in before['partitions']if p['node']!='/dev/vda1']==[p for p in after['partitions']if p['node']!='/dev/vda1']
 quiescent();persist('resize2fs-once.private',{'device':'/dev/vda1','noForceShrinkReboot':True,'noRepeat':True});command(['/usr/sbin/resize2fs','/dev/vda1'])
 quiescent();assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d';persist('partition-after.private.json',after)
 space=os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize;assert space>=12*1024**3
 print(json.dumps({'actualExit':0,'sameBoot':True,'nonRootPartitionsUnchanged':True,'rootStartUuidTypeUnchanged':True,'guestFreeBytesAfter':space,'noRebootCopyShrink':True,'ownedLocksReleasedNormally':True,'allTenUnitsKernelEmpty':True,'privateRoot':str(root)}))
finally:
 for fd in reversed(held):os.close(fd)
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed environment source required')
    prior=json.loads((W/'pg2006-existing-runtime-independent-post-v1/manifest.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['allClientAdvisoryFlock0']is not True:raise ValueError('actual fully closed current before required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    guest_output=b''
    with management_gate(P/'current-management-critical.lock'):
        with (out/'guest.stderr.private.log').open('wb') as errors:
            guest=subprocess.Popen(SSH+['sudo','-n','python3','-B','-c',shlex.quote(GUEST)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors)
            admission=b'';code=1
            try:
                with selectors.DefaultSelector() as ready:
                    ready.register(guest.stdout,selectors.EVENT_READ)
                    if not ready.select(30):raise ValueError('bounded guest admission unavailable; no QMP issued')
                    admission=guest.stdout.readline()
                if admission!=b'CURRENT_LOCKED_QUIESCENT_READY\n':
                    guest_output,_=guest.communicate(input=b'QMP_REFUSED\n',timeout=15)
                    code=guest.returncode or 1
                else:
                    code,log=run('python3 -c '+shlex.quote(LAN),timeout=45,sudo=True);(out/'lan.private.log').write_text(log)
                    guest_output,_=guest.communicate(input=b'QMP_GROW_CONFIRMED\n' if code==0 else b'QMP_REFUSED\n',timeout=180)
                    if not code:code=guest.returncode
            except Exception as error:
                (out/'refused.safe.json').write_text(json.dumps({'errorType':type(error).__name__,'replayForbidden':True}))
                if guest.poll() is None:
                    guest.stdin.close();guest.wait(timeout=15)
                code=1
            finally:
                (out/'guest.private.log').write_bytes(admission+guest_output)
    value={'actualExit':code,'operatorSource':operator,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'lanPayloadSha256':hashlib.sha256(LAN.encode()).hexdigest(),'guestPayloadSha256':hashlib.sha256(GUEST.encode()).hexdigest(),'formalAccepted':False,'independentFullPostPending':True}
    if not code:value['guest']=json.loads(guest_output)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
