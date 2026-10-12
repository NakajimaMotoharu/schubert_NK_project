"""Separate read-only closing: exact saved typed recovery/current/normal scopes, no replay."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1505_publication_recovery_sources_v3 import refs as source

BODY=r'''
POST=BASE/'pg1508-publication-recovery-closing-v3';require(not os.path.lexists(POST))
recovery=BASE/'pg1507-publication-only-recovery-v3';raw=(recovery/'after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='b9db4093f107b5fe1a93d152117ea3476b80f3747bbba3fea5d0afdaec1f4cff')
after=json.loads(raw);require(after['onlyTypedIntentRetirement']is True and after['originalDbEpochPreserved']is True and after['parent']['pid']==95216 and after['parent']['ticks']==1668178 and after['parent']['argvSha256']=='f0b6bf8cffd125928d2f14c5a6516cd1c288651a8809a24a04e9bb42b6e362fe')
require((recovery/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\npublicationOnlyRecovered=true\nepochDbBusinessWrites=0\n')
hashes={'schubert-nk-expiry-cleanup.service':'d173ce572ce1a26d4e460787488f85c5051ac509f7cd18e222d6a59a40b2dff1','artemis.service':'e8f8db7811b04e92ba1a072da1ff3ce43de470a41257f875a20113bd3991d48d','schubert-nk-cleanup.service':'f5ed3ff37ef89e5600d9f8c455debf4bcf719a1bb26fdf8d126b632ee8196f52'}
require(set(hashes)==set(ORDER))
for unit in ORDER:
 b=(recovery/(unit+'.stopped.private')).read_bytes();require(hashlib.sha256(b).hexdigest()==hashes[unit])
 STOP_RECEIPTS[unit]=json.loads(b);STOPPED.append(unit)
 require((recovery/(unit+'.stop-reserved.private')).is_file())
RETIRED=True;PEER_CLOSED=True
require(not pathlib.Path('/proc/95216').exists()and not pathlib.Path('/proc/41805').exists())
peer_check();require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),after['parent']['locks']))
for name,m in after['parent']['locks'].items():require(metadata(ROOT/name)==m)
# These exact three inode keys were independently observed before current Broker stop.
broker_keys={(253,1,503366),(253,1,503372),(0,33,31)}
for line in pathlib.Path('/proc/locks').read_text().splitlines():
 f=line.split()
 if len(f)==8 and f[1]in {'POSIX','FLOCK','OFDLCK'}:
  d=f[5].split(':');require(len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))not in broker_keys)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 for unit in UNITS:kernel_empty(unit)
 first=snapshot();second=snapshot();require(first==second==after['current']);validate_current(first)
 require('/run/schubert-nk/startup/permit-start.intent'not in first['runtime']['startup'])
 POST.mkdir(mode=0o700);encoded=json.dumps(first,sort_keys=True).encode()
 with(POST/'observed.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 for unit in reversed(refs):manager.UnrefUnit(unit)
 refs=[];bus.close();bus=None
 with(POST/'complete.private').open('xb')as f:f.write(b'independentPublicationOnlyClosing=true\nallOriginalDbEpochPermitPreserved=true\nmanagementAndServiceResourcesGone=true\n');f.flush();os.fsync(f.fileno())
 fd=os.open(POST,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 if refs:raise ValueError('new closing Ref not normally returned')
 if bus is not None:bus.close()
print(json.dumps({'actualExit':0,'allOriginalDbEpochPermitBackupCredentialNativeCurrentPreserved':True,'serviceThreeAndManagementResourcesGone':True,'canonicalPublicationIntentOnlyRetired':True,'allNewMetadataRefsNormalClosed':True,'oldRoot1456StillFailed143':True,'observedSha256':hashlib.sha256(encoded).hexdigest(),'actions0':True,'formalAccepted':False,'resumeIssued':False}))
'''

def payload():
    nodes=[]
    for n in ast.parse(source()).body:
        if isinstance(n,ast.Try):break
        if isinstance(n,ast.FunctionDef)and n.name in {'stop_one','save'}:continue
        nodes.append(n)
    raw="import sys\nsys.argv=['readonly-closing','verify','2']\n"+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+BODY
    compile(raw,'<independent publication-only fullclosing>','exec');return raw

def main():
    os.umask(0o077);out=W/'pg1508-publication-recovery-closing-v3';out.mkdir(mode=0o700)
    previous=json.loads((W/'pg1507-publication-recovery-once-v3/manifest.safe.json').read_bytes());assert previous['actualExit']==0 and previous['sshExit']==0 and previous['normalScopesReceipt']is True
    raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'actions0':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode

if __name__=='__main__':raise SystemExit(main())
