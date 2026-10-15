"""Read exact current stopped runtime entry as data before new-only retirement tools."""
import types
import pg3556_current_stopped_readonly as transport

SLOT='pg3660-current-runtime-retirement-input-v1'


def payload():
    return r'''
from pathlib import Path
import json,hashlib,os,stat,datetime
def require(v):
 if not v:raise ValueError('exact stopped runtime input refused')
def metadata(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
base=Path('/var/lib/pgpt-s1-preservation')
p=base/'pg3600-native-stop-v1/after.private.json';raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
require(digest=='e12ce6adc3a4c1641f099a4f01d4c35a7728a6a06c8bd68876e1fcdd7169d38e')
snapshot=json.loads(raw);require(len(snapshot)==10 and len(snapshot['rows'])==24 and len(snapshot['units'])==10)
require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
current=Path('/opt/schubert-nk/current');require(str(current.readlink())=='/opt/schubert-nk/releases/0.1.0-PG3420')
manifest=(current/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()=='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72')
source=json.loads(manifest)['source']['commit'];require(source=='4856b3fcaeb4cae983d77757a38dc0bf56a693e2')
runtime=snapshot['runtime'];root='/run/systemd/system';directory=root+'/schubert-nk-morning-controller.service.d';target=directory+'/zz-pg3564-once-resume.conf'
require(set(runtime)=={root,directory,target})
require({str(p)for p in Path(root).iterdir()}=={directory}and {str(p)for p in Path(directory).iterdir()}=={target})
for name,item in runtime.items():
 p=Path(name);m=metadata(p);require(m==item['metadata']and not os.listxattr(p))
 if name==target:require(stat.S_ISREG(m[4])and m[2:6]==[0,0,stat.S_IFREG|0o644,1]and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
 else:require(stat.S_ISDIR(m[4])and item['sha256']is None)
require(metadata(Path(target))==runtime[target]['metadata'])
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':source,'stoppedAfterSha256':digest,'snapshotKeys':10,'all24SnapshotTables':24,'runtimeEntries':3,'targetName':'zz-pg3564-once-resume.conf','targetSha256':runtime[target]['sha256'],'targetBytes':runtime[target]['metadata'][6],'runtimeMetadataAndByteCurrent':True,'originalEmptyParentRetained':True,'actions0':True,'formalAccepted':False}))
'''


def main():
    fn=transport.main
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_runtime_input_only')()


if __name__=='__main__':raise SystemExit(main())
