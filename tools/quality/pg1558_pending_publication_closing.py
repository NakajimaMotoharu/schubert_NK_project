"""Separate full source/original/publication/owner closing. No replay or runtime start."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1553_pending_publication_refs import source

BODY=r'''
POST=BASE/'pg1558-pending-publication-independent-closing-v1';require(not os.path.lexists(POST))
raw=(SAVE/'after.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='c5cbec662c26ea04f1c6057c1f767e166fb77a591162daf071c02345fdfe9b8f')
after=json.loads(raw);require(after['pendingCodeOnly']is True and after['epochAndAllBusinessOriginalsUnchanged']is True)
require((SAVE/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\npendingCodeOnly=true\nepochDbBusinessWrites=0\n')
parent=after['parent'];require(parent['pid']==103953 and parent['ticks']==2954748 and parent['argvSha256']=='08deea0b9084361766458df68f3424330e86d553d97258db0a0a4fb132f983e3'and not pathlib.Path('/proc/103953').exists())
require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),parent['locks']))
for name,m in parent['locks'].items():require(metadata(ROOT/name)==m)
PEER_CLOSED=True;peer_check();publication_phase='old-linked-private'
require((SAVE/'old-approval.private').read_bytes()==oracle.OLD_APPROVAL)
require((SAVE/'old-epoch.private').read_bytes()==pathlib.Path(oracle.STARTUP+'/epoch.current').read_bytes())
require(public()==after['publicAfter']and public()==after['publicAfter'])
directory=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
link=os.open(SAVE/'current-link.private',os.O_PATH|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 actual_old=linked_attributes(directory,'current-link.private',link)
 oracle.moved_old_link(after['publicBefore'][oracle.CURRENT][oracle.CURRENT+'/current'],actual_old,0,time.time_ns())
finally:os.close(link);os.close(directory)
flags=command(['findmnt','-n','-o','OPTIONS','--mountpoint',oracle.NEW_LINK],4096).decode('ascii').strip().split(',')
require(len(flags)==len(set(flags))and 'ro'in flags and 'rw'not in flags)
old_release=pathlib.Path(oracle.OLD_LINK);old_raw=(old_release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(old_raw).hexdigest()==BOM)
old_data=json.loads(old_raw);require(old_data['source']['commit']==SOURCE and len(old_data['artifacts'])==187)
old_sums=contract.canonical_sum_bytes(old_data['artifacts'],BOM);require((old_release/'SHA256SUMS').read_bytes()==old_sums)
old_records=old_data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(old_raw),'sha256':BOM},{'path':'SHA256SUMS','size':len(old_sums),'sha256':hashlib.sha256(old_sums).hexdigest()}]
old_held=contract.HeldInventory(str(old_release),old_records,0).open()
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 for unit in UNITS:kernel_empty(unit)
 old_first=old_held.capture()
 first=snapshot();second=snapshot();require(first==second==after['current']);protected_current(first)
 require(old_first==old_held.capture()and public()==after['publicAfter'])
 POST.mkdir(mode=0o700);encoded=json.dumps(first,sort_keys=True).encode()
 with(POST/'observed.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 for unit in reversed(refs):manager.UnrefUnit(unit)
 refs=[];bus.close();bus=None;old_held.close()
 with(POST/'complete.private').open('xb')as f:f.write(b'independentPendingCodeOnlyClosing=true\nallOriginalDbEpochPermitPreserved=true\nmanagementAndServiceResourcesGone=true\n');f.flush();os.fsync(f.fileno())
 fd=os.open(POST,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 if refs:raise ValueError('new closing Ref not normally returned')
 if bus is not None:bus.close()
 if not old_held.closed:old_held.close()
print(json.dumps({'actualExit':0,'newCurrentSource':NEW_SOURCE,'newCurrentManifestSha256':NEW_BOM,'codeOnlyIndependentClosingQualified':True,'oldLinkedInodeAndApprovalPreserved':True,'allOriginalDbEpochPermitBackupCredentialNativePreserved':True,'managementAndServiceResourcesGone':True,'allNewMetadataRefsNormalClosed':True,'oldRoot1456StillFailed143':True,'observedSha256':hashlib.sha256(encoded).hexdigest(),'actions0':True,'formalAccepted':False,'resumeIssued':False}))
'''

def payload():
    nodes=[]
    for node in ast.parse(source()).body:
        if isinstance(node,ast.Try):break
        nodes.append(node)
    raw="import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg1553-pending-publication-tools-v1')\nsys.argv=['readonly-closing','verify','2']\n"+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+BODY
    compile(raw,'<independent no-epoch full publication closing>','exec');return raw

def main():
    os.umask(0o077);out=W/'pg1558-pending-publication-independent-closing-v1';out.mkdir(mode=0o700)
    previous=json.loads((W/'pg1556-pending-publication-v1/manifest.safe.json').read_bytes())
    if previous['actualExit']!=0 or previous['sshExit']!=0 or not previous['normalScopesAccepted']:raise ValueError('actual normal publication required')
    raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(result.stderr)
    safe={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'actions0':True,'formalAccepted':False}
    if result.returncode==0:safe['guest']=json.loads(result.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode

if __name__=='__main__':raise SystemExit(main())
