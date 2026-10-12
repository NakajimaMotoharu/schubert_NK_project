"""SS343 SSC247/266 composition: unused sibling placement for failed partial original.

The current partial-original/GC witness is retained, never replaced by a DONE
template. Existing signed current is fully verified before the delimited sibling
addition; old/new signed FD inventories are acquired after it, as in SSC247.
"""
import re
import sys
from pathlib import Path
from pg1478_partial_original_profile_sources import java as prior_java
from pg1512_original_component_profile_sources import refs as prior_refs
from pg1517_original_profile_retry import remap as fixed_profile

sys.path.insert(0, str(Path(__file__).parent / 'vm/050_s1'))
from pg1069_cold_candidate_sources import stage_body as archive_placement

TOOLS='pg1536-pending-unused-tools-v1'
SAVE='pg1539-pending-unused-placement-v1'
CLASS='Pg1536PendingUnusedPlacement'

def once(raw, old, new):
    if raw.count(old)!=1:raise ValueError('fixed pending unused source boundary refused')
    return raw.replace(old,new)

def java():
    raw=prior_java().replace('Pg1478PartialOriginalProfile',CLASS).replace('pg1478-partial-original-tools-v1',TOOLS).replace('pg1481-partial-original-profile-v1',SAVE).replace('pg1478_partial_original_refs.py','pg1536_pending_unused_refs.py').replace('PG1481_','PG1539_').replace('PG266-readonly-profile','PG269-pending-unused')
    raw=once(raw,'"profile".equals(args[0])','"place".equals(args[0])')
    raw=raw.replace('readonlyProfile=true','unusedPlacement=true').replace('readonlyProfile','unusedPlacement')
    raw=raw.replace('mutation0.','Unused sibling only; current/approval/epoch/Unit/DB mutation0.')
    return raw

def refs(bom, bundle):
    if any(type(h)is not str or re.fullmatch('[a-f0-9]{64}',h)is None for h in [bom,bundle]):
        raise ValueError('fixed independently qualified candidate hashes required')
    raw=fixed_profile(prior_refs()).replace('Pg1517OriginalComponentProfile',CLASS).replace('pg1517-original-component-tools-v2',TOOLS).replace('pg1519-original-component-profile-v2',SAVE).replace('PG269-original-io-profile','PG269-pending-unused').replace("b'profile'","b'place'")
    # Extract the known full-inventory acquisition into the explicit AFTER phase.
    begin=raw.index(' release=pathlib.Path(' ,raw.index("phase='CURRENT_FULL_READONLY_BEFORE'"))
    end=raw.index(' bus=dbus.SystemBus(private=True)',begin)
    acquire=raw[begin:end]
    acquire=once(acquire,' before_inventory=[h.capture()for h in held];fixed_parent=actor()', ' before_inventory=[h.capture()for h in held]')
    candidate=f'''
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1535')
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()=={bom!r})
 data=json.loads(manifest);require(data['source']['commit']=='4d6bcbddb417b76d27e52d5d9640752c300edccf'and len(data['artifacts'])==187 and data['versions']['schema']=='028')
 records=data['artifacts']+[{{'path':'RELEASE-MANIFEST.json','size':len(manifest),'sha256':{bom!r}}}]
 sums=contract.canonical_sum_bytes(data['artifacts'],{bom!r});require((release/'SHA256SUMS').read_bytes()==sums)
 records.append({{'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()}})
 held.append(contract.HeldInventory(str(release),records,0).open())
 bundle_raw=pathlib.Path('/home/ubuntu/pg1538-candidate-input-v1/bundle.safe.json').read_bytes();require(hashlib.sha256(bundle_raw).hexdigest()==BUNDLE_HASH)
 signature_hash=json.loads(bundle_raw)['signatureSha256']
 held.append(contract.HeldInventory(str(BASE),[{{'path':'pg1535-manifest.sig','size':64,'sha256':signature_hash}}],0).open_file())
 before_inventory=[h.capture()for h in held]
'''
    acquire='def acquire_after_placement():\n global before_inventory\n'+acquire+candidate
    raw=raw[:begin]+' fixed_parent=actor();before_inventory=[];placed=False\n'+raw[end:]
    stage=archive_placement().replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed','4d6bcbddb417b76d27e52d5d9640752c300edccf').replace('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',bom).replace('PG1068','PG1535').replace('pg1068','pg1535').replace('pg1071','pg1538')
    stage=stage[:stage.rindex('place_candidate()')]
    idx=raw.index('try:\n phase=');raw=raw[:idx]+'BUNDLE_HASH='+repr(bundle)+'\n'+stage+'\n'+acquire+'\n'+PARENT_CONTRACT+'\n'+raw[idx:]
    raw=once(raw,"  if action=='run':PEER_CLOSED=True", "  if action in {'run','release'}:require(placed)\n  if action=='run':PEER_CLOSED=True")
    raw=once(raw,"  if action=='release':\n   require(PEER_CLOSED)", "  if action=='prepared':\n   require(not placed and not held)\n   roots=[pathlib.Path('/opt/schubert-nk/releases'),BASE]\n   before_roots=[parent_state(p)for p in roots];begin_ns=time.time_ns()\n   place_candidate()\n   end_ns=time.time_ns()\n   for path,before,entry,links in zip(roots,before_roots,['0.1.0-PG1535','pg1535-manifest.sig'],[1,0],strict=True):\n    parent_delta(before,parent_state(path),entry,links,begin_ns,end_ns)\n   acquire_after_placement();placed=True\n   value=verify_current()\n  if action=='release':\n   require(PEER_CLOSED)")
    raw=raw.replace("'mutation0':True","'unusedCandidatePlaced':True,'currentApprovalEpochDbUnitsUnchanged':True")
    compile(raw,'<fixed partial-original unused placement>', 'exec')
    return raw

PARENT_CONTRACT=r'''
def parent_state(path):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  st=os.fstat(fd);m=[st.st_dev,st.st_ino,st.st_uid,st.st_gid,st.st_mode,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns]
  acl={n:os.getxattr(fd,n).hex()for n in os.listxattr(fd)}
  require(st.st_uid==0 and stat.S_ISDIR(st.st_mode)and not st.st_mode&0o022 and 'system.posix_acl_access'not in acl and 'system.posix_acl_default'not in acl)
  return {'metadata':m,'entries':sorted(os.listdir(fd)),'xattrs':acl}
 finally:os.close(fd)
def parent_delta(before,after,entry,links,begin,end):
 require(type(before)is dict and type(after)is dict and set(before)==set(after)=={'metadata','entries','xattrs'})
 require(type(links)is int and links in [0,1]and type(begin)is int and type(end)is int and begin<=end)
 require(all(type(v['entries'])is list and all(type(n)is str for n in v['entries'])and type(v['xattrs'])is dict and type(v['metadata'])is list and len(v['metadata'])==9 and all(type(n)is int for n in v['metadata'])for v in [before,after]))
 require(type(entry)is str and entry not in before['entries'] and sorted(before['entries']+[entry])==after['entries'])
 a=before['metadata'];b=after['metadata'];require(len(a)==len(b)==9 and a[:5]==b[:5]and b[5]==a[5]+links and a[6]<=b[6]<=a[6]+4096 and before['xattrs']==after['xattrs'])
 require(all(begin<=b[i]<=end for i in [7,8]))
 return True
'''
