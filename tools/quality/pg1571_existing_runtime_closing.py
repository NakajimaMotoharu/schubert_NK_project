"""Independent all-current/resource closing after fresh normal verify-only."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1567_existing_runtime_sources import refs,TOOLS

BODY=r'''
POST=BASE/'pg1571-existing-runtime-independent-closing-v1';require(not os.path.lexists(POST))
raw=(SAVE/'after.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='ae1eaff55296e103ae152fc5339fc8609652093c5f46b4af76c252b7d82b0bdb')
after=json.loads(raw);require(after['existingRuntimeVerified']is True and after['allOriginalDbEpochPermitPreserved']is True)
require((SAVE/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\nexistingRuntimeVerified=true\nepochDbBusinessWrites=0\n')
parent=after['parent'];require(parent['pid']==106867 and parent['ticks']==3133424 and parent['argvSha256']=='330a80562dca15e9cb9e0923033eafa5e760ed0b05e82a4b53ca557a44808b8c'and not pathlib.Path('/proc/106867').exists())
require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),parent['locks']))
for name,m in parent['locks'].items():require(metadata(ROOT/name)==m)
PEER_CLOSED=True;peer_check();initialize_runtime()
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 for unit in UNITS:kernel_empty(unit)
 first=snapshot();second=snapshot();require(first==second==after['current']);protected_runtime(first)
 POST.mkdir(mode=0o700);encoded=json.dumps(first,sort_keys=True).encode()
 with(POST/'observed.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 for unit in reversed(refs):manager.UnrefUnit(unit)
 refs=[];bus.close();bus=None
 with(POST/'complete.private').open('xb')as f:f.write(b'independentExistingRuntimeClosing=true\nallOriginalDbEpochPermitPreserved=true\nallManagementResourcesGone=true\n');f.flush();os.fsync(f.fileno())
 fd=os.open(POST,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 if refs:raise ValueError('new closing metadata refs not normally returned')
 if bus is not None:bus.close()
print(json.dumps({'actualExit':0,'existingCanonicalRuntimeIndependentQualified':True,'allOriginalDbEpochPermitBackupCredentialNativePreserved':True,'allManagementResourcesGone':True,'allNewMetadataRefsNormalClosed':True,'oldRoot1456StillFailed143':True,'observedSha256':hashlib.sha256(encoded).hexdigest(),'actions0':True,'formalAccepted':False,'rootStartIssued':False}))
'''

def payload():
    nodes=[]
    for node in ast.parse(refs()).body:
        if isinstance(node,ast.Try):break
        nodes.append(node)
    s="import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/"+TOOLS+"')\nsys.argv=['readonly-existing-runtime','verify','2']\n"+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+BODY
    compile(s,'<independent existing runtime full closing>','exec');return s

def main():
    os.umask(0o077);out=W/'pg1571-existing-runtime-independent-closing-v1';out.mkdir(mode=0o700)
    previous=json.loads((W/'pg1569-existing-runtime-verify-v1/manifest.safe.json').read_bytes())
    if previous['actualExit']!=0 or not previous['normalScopesAccepted']:raise ValueError('actual normal fresh verify-only required')
    raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90);(out/'stderr.private.log').write_bytes(result.stderr)
    safe={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'actions0':True,'formalAccepted':False}
    if result.returncode==0:safe['guest']=json.loads(result.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode

if __name__=='__main__':raise SystemExit(main())
