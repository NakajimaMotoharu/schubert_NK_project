"""Select current ordinary8 plus only Bootstrap closing; earlier point excluded."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1719_current_bootstrap_sources import SOURCE

SLOT='pg1732-current-bootstrap-native-catalog-v1'

def main():
    prior=json.loads((W/'pg1708-new-source-native-catalog-v1/manifest.safe.json').read_bytes())
    post=json.loads((W/'pg1731-current-bootstrap-full-post-v1/manifest.safe.json').read_bytes())
    if prior['actualExit']!=post['actualExit'] or prior['actualExit']!=0 or prior['productionSource']!=SOURCE or post['guest']['productionSource']!=SOURCE or post['guest']['allResources0']is not True:
        raise ValueError('actual current normal20 independent full post required')
    b=post['guest']['bootstrap'];closing=[p for p in b['files']if p['relative'].endswith('.closing.exec')]
    if len(closing)!=1 or len(prior['selected'])!=8:raise ValueError('one current closing point required')
    selected={**closing[0],'unit':'schubert-nk-bootstrap-admin.service','lowerMs':b['lowerMs'],'upperMs':b['upperMs']}
    code="""import hashlib,json,os,pathlib,stat
p=pathlib.Path('/run/schubert-nk/pt-coverage')/SELECTED['relative'];s=p.lstat()
assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(999,981,0o600,1)and 0<s.st_size<=16777216 and not os.listxattr(p)
raw=p.read_bytes();assert p.lstat()==s and s.st_size==SELECTED['bytes']and hashlib.sha256(raw).hexdigest()==SELECTED['sha256']
print(json.dumps({'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]}))
"""
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=('SELECTED='+repr(selected)+'\n'+code).encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if r.returncode:raise ValueError('immutable current Bootstrap closing read refused')
    selected.update(json.loads(r.stdout));points=prior['selected']+[selected]
    if len({v['relative']for v in points})!=9:raise ValueError('distinct process/entry points required')
    v={**prior,'selected':points,'payloadSha256':hashlib.sha256(raw).hexdigest(),'bootstrapCapturedNormal20Verified':True,
       'earlierSameSessionPointsNotImported':[p for p in b['files']if p['relative'].endswith('.terminal.exec')],
       'bootstrapPostSha256':hashlib.sha256((W/'pg1731-current-bootstrap-full-post-v1/manifest.safe.json').read_bytes()).hexdigest(),
       'sourceChanged0':True,'newVmOperations0':True,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'selectedPoints':9,'bootstrapClosingOnly':True,'sameSessionEarlierPointImported':False,'formalAccepted':False}))

if __name__=='__main__':raise SystemExit(main())
