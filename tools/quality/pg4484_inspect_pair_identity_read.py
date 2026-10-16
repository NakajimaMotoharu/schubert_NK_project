"""Read only current exact management pair identity and full socket endpoints."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, SSH
from pg4434_current_candidate_admission_read import authenticate_host

BODY = r'''
import hashlib,json,os
from pathlib import Path
base=Path('/var/lib/pgpt-s1-preservation');old=base/'pg4482-bound-configuration-pair-read-v1'
os.umask(0o077);save=base/'pg4484-inspect-pair-identity-read-v1';save.mkdir(mode=0o700)
def require(v):
 if v is not True:raise ValueError('current exact pre-operation identity required')
pair_raw=(old/'second-pair.private.json').read_bytes();require(hashlib.sha256(pair_raw).hexdigest()=='e1558f41bdf20aa2c85eaf7a821820d4d339b9f1dc0a657f1e4c0b9924c5dbaa');pair=json.loads(pair_raw)
detail={}
for label,pid,ticks,digest in [('java',827198,16494387,'72e6609effcd0397c9a679d8bea26588975bd6eaf56cff535e4c4b954bd6a601'),('python',827230,16494598,'8c039420d33e9ba1c67afaabf06bf878f0333ee262d87bc3b77f7c608dee588c')]:
 p=Path('/proc')/str(pid);require(int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==digest)
 keys=[v.split(b'=',1)[0].decode('ascii')for v in(p/'environ').read_bytes().split(b'\0')if v]
 detail[label]={'pid':pid,'ticks':ticks,'argvSha256':digest,'exe':str((p/'exe').readlink()),'root':str((p/'root').readlink()),'cwd':str((p/'cwd').readlink()),'agentVariableNamesPresent':[k for k in keys if k in ['LD_PRELOAD','LD_AUDIT','JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','PYTHONPATH','PYTHONSTARTUP']]}
 require(not detail[label]['agentVariableNamesPresent'])
data=json.loads((old/'second-data.private.json').read_bytes())
out={'identity':detail,'javaAuthority':pair['java']['authority'],'pythonAuthority':pair['python']['authority'],'cgroups':[pair[k]['cgroup']for k in ['java','python']],
 'javaFdTargets':{k:v['target']for k,v in pair['java']['fds'].items()},'pythonFdTargets':{k:v['target']for k,v in pair['python']['fds'].items()},'peers':data['database']['peers'],
 'tcp':pair['tcp'],'tcp6':pair['tcp6'],'backendFds':pair['backend']['fds']}
encoded=json.dumps(out,sort_keys=True).encode()
with(save/'identity.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'operationsIssued':0,'identitySha256':hashlib.sha256(encoded).hexdigest(),'identity':detail,
 'javaAuthority':out['javaAuthority'],'pythonAuthority':out['pythonAuthority'],'cgroups':out['cgroups'],
 'javaSocketTargets':{k:v for k,v in out['javaFdTargets'].items()if v.startswith('socket:')},'pythonFdTargets':out['pythonFdTargets'],'peerCount':len(out['peers'])}))
'''


def main():
    if check(BODY,'<exact management identity read>'):raise ValueError('emitted static0')
    authenticate_host();os.umask(0o077);out=W/'pg4484-inspect-pair-identity-read-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(BODY)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=BODY.encode(),capture_output=True,timeout=60)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(BODY.encode()).hexdigest(),'operationsIssued':0}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':
    raise SystemExit(main())
