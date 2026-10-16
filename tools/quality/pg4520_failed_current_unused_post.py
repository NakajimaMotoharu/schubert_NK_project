"""Fresh current M/A/RODB/tenRefs plus independently signed unused187 candidate."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg4510_metadata_only_handoff_sources as previous
import pg3762_hygiene_unused_post as original_candidate
from pg1446_current_cold_stage import W,P,SSH
from pg4434_current_candidate_admission_read import authenticate_host
from pg1674_critical_management_gate import management_gate

SLOT='pg4520-failed-current-unused-post-v1'


def permissions(records):
    if type(records)is not list or not records:raise ValueError('full candidate metadata')
    paths=set()
    for r in records:
        if type(r)is not dict or set(r)!={'path','directory','uid','gid','mode','nlink','symlink','xattrs'}:raise ValueError('complete candidate attributes')
        name=r['path'];directory=r['directory']
        if type(name)is not str or type(directory)is not bool or name in paths:raise ValueError('unique complete candidate catalog')
        paths.add(name)
        executable=name in ['operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector']
        if type(r['uid'])is not int or type(r['gid'])is not int or type(r['mode'])is not int or type(r['nlink'])is not int:raise ValueError('typed candidate ownership')
        if r['uid']!=0 or r['gid']!=986 or r['mode']!=(0o750 if directory or executable else 0o640)or r['symlink']is not False or r['xattrs']!=[]or r['nlink']<1 or not directory and r['nlink']!=1:raise ValueError('fixed root/schubert candidate modes')
    return True


def candidate_check():
    text=original_candidate.EXTRA
    start=text.index("candidate=Path('/opt/schubert-nk/releases/");end=text.index('\nbefore=Path(',start)
    # Preserve the original independent full187/hash/signature/inventory oracle.
    text=text[start:end].replace('PG3748','PG4432').replace('pg3748','pg4432')
    return inspect.getsource(permissions)+'\n'+'''def candidate_verify():
'''+''.join(' '+line+'\n'for line in text.splitlines())+r'''
 sums={r['path']:r['sha256']for r in c['artifacts']};require(len(sums)==187);sums['RELEASE-MANIFEST.json']=CANDIDATE['manifestSha256']
 canonical=''.join(sums[name]+'  '+name+'\n'for name in sorted(sums)).encode('ascii');require((candidate/'SHA256SUMS').read_bytes()==canonical)
 records=[]
 for p in [candidate,*candidate.rglob('*')]:
  s=p.lstat();require(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode))
  records.append({'path':p.relative_to(candidate).as_posix(),'directory':stat.S_ISDIR(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink,'symlink':p.is_symlink(),'xattrs':os.listxattr(p)})
 require(permissions(records));s=sig.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(sig))
 return {'candidateSource':c['source']['commit'],'candidateManifestSha256':CANDIDATE['manifestSha256'],'candidate187SignatureVerified':True,'candidateUnusedOnly':True,'candidatePermissionsVerified':True,'candidateFileInventory':len(sums)+1,'candidateNativeCredit':False}
'''


def payload():
    candidate=json.loads((W/'pg4432-candidate-build-v1.safe.json').read_bytes())
    if candidate['actualExit']!=0 or candidate['candidateSource']!='964e96e45bb588e7e75798b5adf425cbd9985427' or candidate['manifestSha256']!='93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de':raise ValueError('fixed signed candidate')
    raw=previous.post_source().replace('pg4510-metadata-only-handoff-v1-independent-post',SLOT)
    tree=ast.parse(raw);scopes=[n for n in tree.body if isinstance(n,ast.Try)and n.finalbody]
    if len(scopes)!=1:raise ValueError('one authenticated outer ten-Ref scope')
    last=scopes[0].body[-1];lines=raw.splitlines(keepends=True)
    lines.insert(last.end_lineno,' candidate_first=candidate_verify();candidate_second=candidate_verify();require(candidate_first==candidate_second)\n')
    raw=''.join(lines)
    marker="(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))"
    if raw.count(marker)!=1:raise ValueError('one final normal-close output')
    raw=raw.replace(marker,"value.update(candidate_first);value.update(currentSource=data['source']['commit'],configuration32EveryFieldUnchanged=True,all24TablesEqualTwice=True,allClientAdvisoryMA0=True,newTenReferencesReturnedNormally=True,native58Preserved=True,runtimeStartupAndApprovalEpochUnchanged=True)\n"+marker,1)
    raw='CANDIDATE='+repr(candidate)+'\n'+candidate_check()+'\n'+raw
    if check(raw,'<full current plus signed unused candidate post>'):raise ValueError('all emitted static0')
    compile(raw,'<full current plus signed unused candidate post>','exec');return raw


def main():
    receipt=json.loads((W/'pg4516-place-v1.safe.json').read_bytes())
    if receipt['actualExit']!=0 or receipt['sourceQualified']is not True or receipt['currentApprovalEpochChanged']is not False:raise ValueError('genuine same-artifact unused placement0 first')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed post source first')
    raw=payload();authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=240)
    (out/'stdout.safe.json').write_bytes(result.stdout);(out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'currentSource':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','candidateSource':'964e96e45bb588e7e75798b5adf425cbd9985427','payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
