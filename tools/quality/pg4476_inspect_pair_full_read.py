"""Full current pre-operation pair and all preserved data; no held gate acquisition."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4360_pool_bound_partial_sources as original
import pg4160_retained_config_read as process_source
from pg1446_current_cold_stage import SSH, W
from pg4434_current_candidate_admission_read import authenticate_host


def payload():
    raw=original.files()['post.py'];tree=ast.parse(raw)
    end=next(n.lineno for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='metadata')
    prefix=''.join(raw.splitlines(keepends=True)[:end-1])
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    selected=[]
    # The first snapshot is the complete raw8 before the post-only witness
    # wrapper. All runtime row/owner changes are independently checked below.
    for name in ['metadata','tree','require','command','units','database','durable']:
        selected.append(ast.get_source_segment(raw,functions[name]))
    first=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    selected.append(ast.get_source_segment(raw,first))
    assignments=[]
    names={'base','oldraw','old','fields','expected_inv','sql'}
    for n in tree.body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in names for t in n.targets):
            assignments.append(ast.get_source_segment(raw,n))
        if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='table':assignments.append(ast.get_source_segment(raw,n))
        if isinstance(n,ast.AugAssign)and isinstance(n.target,ast.Name)and n.target.id=='sql':assignments.append(ast.get_source_segment(raw,n))
    proc=next(n for n in ast.parse(process_source.BODY).body if isinstance(n,ast.FunctionDef)and n.name=='proc')
    # Helpers precede the literal SQL assignments; require/Path are available.
    result=prefix+'\n'+'\n'.join(selected)+'\n'+'\n'.join(assignments)+'\n'+ast.get_source_segment(process_source.BODY,proc)+'\n'+BODY
    if check(result,'<complete current inspect pair/data read>'):raise ValueError('all emitted static0')
    return result


BODY=r'''
os.umask(0o077);save=base/'pg4476-inspect-pair-full-read-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
require(hashlib.sha256(oldraw).hexdigest()=='33b24b767326879adff27c1ee38aaa08102e347d04d631947047ef667f3352c6')
reference_raw=(base/'pg4440-failed-full-image-diagnosis-v1/after.private.json').read_bytes();require(hashlib.sha256(reference_raw).hexdigest()=='148a8d8a3a3284dbf4a72833ca808ca8a07cee84a85b5562f07356006ac91148');reference=json.loads(reference_raw)
def private(name,value):
 encoded=json.dumps(value,sort_keys=True).encode();require(len(encoded)<=67108864)
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return hashlib.sha256(encoded).hexdigest()
def read_pair():
 return {'sudo':proc(827196),'java':proc(827198),'python':proc(827230),'backend':proc(827228),
         'tcp':Path('/proc/net/tcp').read_text(),'tcp6':Path('/proc/net/tcp6').read_text()}
first_pair=read_pair();first_pair_sha=private('first-pair.private.json',first_pair)
first=snapshot();first_sha=private('first-data.private.json',first)
second_pair=read_pair();second_pair_sha=private('second-pair.private.json',second_pair)
second=snapshot();second_sha=private('second-data.private.json',second)
for label,pid,ticks,digest in [('java',827198,16494387,'72e6609effcd0397c9a679d8bea26588975bd6eaf56cff535e4c4b954bd6a601'),('python',827230,16494598,'8c039420d33e9ba1c67afaabf06bf878f0333ee262d87bc3b77f7c608dee588c')]:
 a=first_pair[label];b=second_pair[label];require(a==b and a['pid']==pid and a['ticks']==ticks and a['argvSha256']==digest)
for value in [first,second]:
 require(all(value[k]==reference[k]for k in ['units','actors','durable','native','startup','runtime']))
 require(value['database']['rows']==reference['database']['rows'])
 peers=value['database']['peers'];require(len(peers)==1 and peers[0]['pid']==827228 and peers[0]['user']=='schubert_batch'and peers[0]['application']=='PG998-native-stage'and peers[0]['state']in ['active','idle in transaction'])
 locks=value['database']['locks'];require(len(locks)==1 and locks[0]['pid']==827228 and locks[0]['classid']==0 and locks[0]['objid']==71419602 and locks[0]['objsubid']==1 and locks[0]['mode']=='ExclusiveLock'and locks[0]['granted']is True)
 require(len(value['flocks'])==2 and all(l.split()[4]=='827198'for l in value['flocks']))
require(first_pair['java']['children']==[827230]and first_pair['python']['children']==[])
require(first_pair['java']['authority']['PPid']=='827196'and first_pair['python']['authority']['PPid']=='827198')
require(not os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG4432')and not os.path.lexists('/var/lib/pgpt-s1-preservation/pg4432-manifest.sig'))
summary={'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':data['source']['commit'],'BOM':sha,'boot':boot,'operationsIssued':0,'oldScopesNormal':False,'formalAccepted':False,
 'firstPairSha256':first_pair_sha,'secondPairSha256':second_pair_sha,'firstDataSha256':first_sha,'secondDataSha256':second_sha,
 'java':{'pid':827198,'ticks':16494387,'argvSha256':first_pair['java']['argvSha256'],'fdCount':len(first_pair['java']['fds'])},
 'python':{'pid':827230,'ticks':16494598,'argvSha256':first_pair['python']['argvSha256'],'fdCount':len(first_pair['python']['fds'])},
 'allCurrentOriginalDataPreserved':True,'allFullPairDescriptorsEqualTwice':True,'backendPid':827228,'candidatePlaced':False}
private('manifest.safe.json',summary);print(json.dumps(summary))
'''


def main():
    raw=payload();authenticate_host();os.umask(0o077);out=W/'pg4476-inspect-pair-full-read-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'operationsIssued':0,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':
    raise SystemExit(main())
