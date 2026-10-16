"""Exact live QMP/guest geometry read only; no block or filesystem change."""
import hashlib
import json
import os
import shlex
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,SSH
from pg4434_current_candidate_admission_read import authenticate_host
from lan_server import run

HOST=r'''
from pathlib import Path
import datetime,hashlib,json,os,socket,stat,struct
os.umask(0o077);p=Path('/proc/4599');argv=(p/'cmdline').read_bytes()
assert int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==101242 and hashlib.sha256(argv).hexdigest()=='f765c39c924d24fc03739355785e22c06b302d68418a85860e3d661960a2b106'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='c7964823-c628-4ef2-99b5-07b0f0b62bba'
root=Path('/home/mini/schubert-nk-pgpt/vm/pg2810-network-resume-cold-v1');qmp=root/'qmp.sock';s=qmp.lstat();parent=root.lstat()
assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid()and s.st_nlink==1 and not os.listxattr(qmp)
assert stat.S_ISDIR(parent.st_mode)and parent.st_uid==os.getuid()and not(stat.S_IMODE(parent.st_mode)&0o022)and root.resolve()==root
sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.settimeout(10);sock.connect(str(qmp))
peer=struct.unpack('3i',sock.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')));assert peer==(4599,os.getuid(),os.getgid())
stream=sock.makefile('rwb',buffering=0)
def frame():
 raw=stream.readline(16777217);assert raw.endswith(b'\n')and len(raw)<=16777216;return json.loads(raw)
greeting=frame();assert 'QMP'in greeting
sequence=0;events=[]
def command(name):
 global sequence
 sequence+=1;ident='PG4564-read-'+str(sequence);stream.write((json.dumps({'execute':name,'id':ident})+'\r\n').encode())
 while True:
  value=frame()
  if 'event'in value:events.append(value);continue
  assert value.get('id')==ident and 'return'in value and 'error'not in value;return value['return']
command('qmp_capabilities');status=command('query-status');assert status['status']=='running'and status['running']is True
jobs=command('query-block-jobs');assert jobs==[]
blocks=command('query-block');entries=[b for b in blocks if b.get('inserted',{}).get('image',{}).get('filename')==str(root/'active.qcow2')];assert len(entries)==1
disk=entries[0];image=disk['inserted']['image'];assert disk['inserted']['ro']is False and disk['inserted']['drv']=='qcow2'and image['virtual-size']==60129542144
schema=command('query-qmp-schema');byname={v['name']:v for v in schema};operation=byname['block_resize'];argument=byname[operation['arg-type']]
assert {m['name']for m in argument['members']}=={'device','node-name','size'}
stream.close();sock.close();space=os.statvfs(root)
layers=[];item=image
while item:
 file=Path(item['filename'])
 if not file.is_absolute():file=root/file
 st=file.stat();layers.append({'filename':str(file.resolve()),'virtualSize':item['virtual-size'],'metadata':[st.st_dev,st.st_ino,st.st_uid,st.st_gid,st.st_mode,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns]})
 item=item.get('backing-image')
assert len(layers)==3
value={'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'greeting':greeting,'peer':peer,'status':status,'jobs':jobs,'disk':disk,
 'blockResizeSchema':[operation,argument],'layers':layers,'hostAvailableBytes':space.f_bavail*space.f_frsize,'events':events,'resizeCommandsIssued':0,'bootChanged':False}
out=Path('/home/mini/schubert-nk-pgpt/runs/PG4566-capacity-preflight-v1');out.mkdir(mode=0o700)
raw=json.dumps(value,sort_keys=True).encode()
with(out/'host.safe.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
print(json.dumps(value))
'''

GUEST=r'''
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
assert os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
raw=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de'
commands={
 'partitionTable':['sfdisk','--json','/dev/vda'],
 'blockTree':['lsblk','-b','-J','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS'],
 'rootMount':['findmnt','-n','-o','SOURCE,FSTYPE,OPTIONS','/'],
 'filesystemUuid':['blkid','-s','UUID','-o','value','/dev/vda1'],
 'packages':['dpkg-query','-W','-f','${Package} ${Version}\n','cloud-guest-utils','e2fsprogs','util-linux']}
results={}
for name,args in commands.items():
 r=subprocess.run(args,capture_output=True,text=True,timeout=20);assert r.returncode==0;results[name]={'actualExit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
assert results['filesystemUuid']['stdout'].strip()=='92978eec-7925-481e-8629-5b963d59ced1'
table=json.loads(results['partitionTable']['stdout'])['partitiontable'];assert table['device']=='/dev/vda'and table['label']=='gpt'and table['sectorsize']==512
parts=table['partitions'];assert len(parts)==4 and {p['node']for p in parts}=={'/dev/vda1','/dev/vda13','/dev/vda14','/dev/vda15'}
rootpart=next(p for p in parts if p['node']=='/dev/vda1');assert rootpart['size']*512==58939391488
tools={n:shutil.which(n)for n in ['growpart','resize2fs','sfdisk','blockdev','findmnt']};assert all(tools.values())
v=os.statvfs('/var/lib/pgpt-s1-preservation');value={'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'tools':tools,
 'availableBytes':v.f_bavail*v.f_frsize,'ordinaryStartMinimum':12884901888,'minimumMet':v.f_bavail*v.f_frsize>=12884901888,'rootPartition':rootpart,
 'source':'964e96e45bb588e7e75798b5adf425cbd9985427','BOM':hashlib.sha256(raw).hexdigest(),'operationsIssued':0}
os.umask(0o077);out=Path('/var/lib/pgpt-s1-preservation/pg4566-capacity-preflight-v1');out.mkdir(mode=0o700)
with(out/'guest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(value))
'''


def main():
    if check(HOST,'<exact readonly QMP>')or check(GUEST,'<exact readonly guest geometry>'):raise ValueError('all emitted static0')
    authenticate_host();os.umask(0o077);out=W/'pg4566-capacity-preflight-v1';out.mkdir(mode=0o700)
    (out/'host-payload.private.py').write_text(HOST);(out/'guest-payload.private.py').write_text(GUEST)
    status,output=run(shlex.join(['python3','-B','-c',HOST]),timeout=60,sudo=True)
    (out/'host-observer.private.log').write_text(output)
    if status!=0:raise ValueError('original QMP read result failed; preserve')
    value=json.loads(output.strip());(out/'host.safe.json').write_text(json.dumps(value,sort_keys=True))
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=GUEST.encode(),capture_output=True,timeout=100)
    (out/'guest-observer.private.log').write_bytes(r.stdout+r.stderr)
    if r.returncode!=0:raise ValueError('original guest geometry read failed; preserve')
    guest=json.loads(r.stdout);(out/'guest.safe.json').write_text(json.dumps(guest,sort_keys=True))
    summary={'actualExit':0,'qemuVersion':value['greeting']['QMP']['version'],'hostAvailableBytes':value['hostAvailableBytes'],'oldVirtualSize':value['disk']['inserted']['image']['virtual-size'],
      'blockNode':value['disk']['inserted']['node-name'],'layers':len(value['layers']),'guestAvailableBytes':guest['availableBytes'],'minimumMet':guest['minimumMet'],
      'guestTools':guest['tools'],'operationsIssued':0,'source':guest['source'],'hostProofSha256':hashlib.sha256((out/'host.safe.json').read_bytes()).hexdigest(),'guestProofSha256':hashlib.sha256((out/'guest.safe.json').read_bytes()).hexdigest()}
    (out/'manifest.safe.json').write_text(json.dumps(summary,sort_keys=True));print(json.dumps(summary));return 0


if __name__=='__main__':raise SystemExit(main())
