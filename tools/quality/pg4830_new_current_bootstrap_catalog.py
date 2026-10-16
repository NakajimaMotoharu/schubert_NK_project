"""Current native ten streams/twelve points only after independent normal20/resources post."""
import json
from pyflakes.api import check
import pg4828_new_current_bootstrap_post as post
import pg4780_new_current_native_catalog as previous

SLOT='pg4830-new-current-bootstrap-catalog-v1'


def prerequisites():
    w=post.role.W
    prior=json.loads((w/previous.SLOT/'manifest.safe.json').read_bytes())
    value=json.loads((w/post.SLOT/'manifest.safe.json').read_bytes());result=value['result']
    if not(type(value['actualExit'])is int and value['actualExit']==0 and value['source']==post.role.SOURCE and prior['actualExit']==0 and prior['productionSource']==post.role.SOURCE and len(prior['selected'])==10 and result['nativePhysicalFiles']==72 and all(result[k]is True for k in ('capturedNormal20VerifiedBeforeCurrent','gcDoesNotInferPastSuccess','currentCredentialsRetired','allResources0','whole24Full32Signed187AndResourcesUnchanged'))):raise ValueError('same source captured20 full independent post and old current points first')
    b=result['bootstrap'];points=b['files']
    if len(points)!=2 or len({v['relative']for v in points})!=2:raise ValueError('two physical current Bootstrap points')
    selected=sorted(points,key=lambda v:0 if v['relative'].endswith('.closing.exec')else 1)
    if not(selected[0]['relative'].endswith('.closing.exec')and selected[1]['relative'].endswith('.terminal.exec')):raise ValueError('closing and terminal both required')
    return prior,[{**v,'unit':'schubert-nk-bootstrap-admin.service','lowerMs':b['lowerMs'],'upperMs':b['upperMs']}for v in selected]


def payload():
    prior,points=prerequisites()
    raw='PRIOR='+repr(prior)+'\nNEW='+repr(points)+'\n'+r'''
import hashlib,json,os,pathlib,stat
def require(v):
 if not v:raise ValueError('immutable current Bootstrap pair catalog refused')
def metadata9(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
root=pathlib.Path('/run/schubert-nk/pt-coverage');points=[]
for v in PRIOR['selected']+NEW:
 name=v['relative'];require(not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))and '\\'not in name)
 p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and not os.listxattr(p))
 if v in NEW:require((s.st_uid,s.st_gid)==(999,981))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s)and s.st_size==v['bytes']and hashlib.sha256(raw).hexdigest()==v['sha256'])
 if v in PRIOR['selected']:require(metadata9(s)==v['metadata'])
 points.append({**v,'metadata':metadata9(s)})
require(len(points)==12 and len({v['relative']for v in points})==12)
print(json.dumps({**PRIOR,'selected':points,'bootstrapCapturedNormal20Verified':True,'bootstrapTwoPointsPendingQualification':True,'currentPhysicalNative':72,'oldSourceNativeImported':False,'formalAccepted':False}))
'''
    if check(raw,'<all prior current plus genuine Bootstrap pair>'):raise ValueError('all emitted static0')
    return raw


def main():return post.role.before.admission.execute(SLOT,payload(),60)


if __name__=='__main__':raise SystemExit(main())
