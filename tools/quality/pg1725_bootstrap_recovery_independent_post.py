"""SSC276 separate full post, all originals/resources; never signal/start."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH,P
from pg1674_critical_management_gate import management_gate
from pg1718_current_bootstrap_before import payload as complete_post

SLOT='pg1725-bootstrap-recovery-full-post-v1'
BODY=r'''
require(not pathlib.Path('/proc/383695').exists())
handoff=base/'pg1724-bootstrap-retained-handoff-v1'
require({p.name for p in handoff.iterdir()}=={'old-proof.private.json','fresh-proof.private.json','fresh-complete.private','383695.term-once.private','complete.private'})
def read_private(name):
 p=handoff/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
require(hashlib.sha256(read_private('old-proof.private.json')).hexdigest()=='3b84d06a176a9d0e3fe4296d4f72108f787d4391120805450f47891bbb4744e0')
fresh_raw=read_private('fresh-proof.private.json');require(hashlib.sha256(fresh_raw).hexdigest()==FRESH)
fresh=json.loads(fresh_raw);require(fresh['independentFreshProofComplete']is True and fresh['signalsIssued']==0 and fresh['oldCloseUnknown']is True and fresh['native']==native)
require(read_private('fresh-complete.private')==('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+FRESH+'\n').encode())
r=json.loads(read_private('383695.term-once.private'));require(r['pid']==383695 and r['ticks']==7281859 and r['actor']==fresh['actor']and r['signal']=='TERM'and r['replayAllowed']is False)
require(read_private('complete.private')==b'ownedJavaGone=true\noldCloseUnknown=true\nallOldResources0=true\nfullIndependentPostPending=true\n')
require(not list((base/'pg1719-bootstrap-verify-v3').iterdir()))
require(hashlib.sha256(snapshot_raw).hexdigest()=='6b29aa3fbeee305335bba17f2fe40f51041a3197cc17c9795a9ddd949930c838')
'''

def payload():
    actual=json.loads((W/'pg1724-bootstrap-retained-handoff-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or len(actual['stages'])!=2 or actual['stages'][0]['signalsIssued']!=0 or actual['stages'][1]['ownedJavaGone']is not True:
        raise ValueError('actual onceTERM complete required')
    fresh=actual['stages'][1]['freshProofSha256']
    if fresh!=actual['stages'][0]['proofSha256']:raise ValueError('same durable fresh proof required')
    raw=complete_post().replace('pg1718-current-bootstrap-before-v1',SLOT)
    marker='finally:\n for u in reversed(refs):manager.UnrefUnit(u)'
    if raw.count(marker)!=1:raise ValueError('one post Ref close required')
    raw='FRESH='+repr(fresh)+'\n'+raw.replace(marker,'\n'.join(' '+l if l else l for l in BODY.splitlines())+'\n'+marker)
    raw=raw.replace("'startsStopsWrites0':True", "'startsStopsWrites0':True,'ownedJavaDbAdvisoryMA0':True,'oldCloseUnknown':True,'fullRecoveryPost':True")
    from pyflakes.api import check
    if check(raw,'<current preRef failure whole post>'):raise ValueError('generated static refused')
    compile(raw,'<current preRef failure whole post>','exec');return raw

def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v));return r.returncode

if __name__=='__main__':raise SystemExit(main())
