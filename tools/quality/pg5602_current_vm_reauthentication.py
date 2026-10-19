"""Fresh deployed296 identity after host candidate5598; never restart/stage authority."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5432_current_vm_reauthentication as previous
from pg4996_resume_connection import authenticate_host,remote_identity
from pg1674_critical_management_gate import management_gate
from pg5598_current_signed_candidate import SOURCE,OLD_SOURCE,OLD_BOM,W,P
from pg1446_current_cold_stage import SSH

SLOT='pg5602-current-vm-reauthentication-v1'
CURRENT,CURRENT_BOM,CANDIDATE=OLD_SOURCE,OLD_BOM,SOURCE


def payload(candidate_bom):
    if type(candidate_bom)is not str or __import__('re').fullmatch('[0-9a-f]{64}',candidate_bom)is None:raise ValueError('actual signed candidate BOM digest required')
    raw=previous.payload()
    changes={previous.CURRENT:CURRENT,previous.CURRENT_BOM:CURRENT_BOM,previous.CANDIDATE:CANDIDATE,previous.CANDIDATE_BOM:candidate_bom,
      '0.1.0-PG4980':'0.1.0-PG5430','pg4980-manifest.sig':'pg5430-manifest.sig'}
    for i,key in enumerate(changes):
        if raw.count(key)!=1:raise ValueError('exact one current/candidate scalar, no cascading source replacement')
        raw=raw.replace(key,'__REA5602_'+str(i)+'__',1)
    for i,value in enumerate(changes.values()):raw=raw.replace('__REA5602_'+str(i)+'__',value,1)
    if check(raw,'<fresh296 signed187 RO metadata only>'):raise ValueError('all standalone globals before guest')
    compile(raw,'<fresh deployed296, no cold boot fallback>','exec')
    return raw


def main():
    candidate=json.loads((W/'pg5598-candidate-build-v1.safe.json').read_bytes())
    if not(candidate['actualExit']==0 and candidate['candidateSource']==SOURCE and candidate['priorSource']==CURRENT
      and candidate['release']=='0.1.0-PG5598'and candidate['signatureVerified']and candidate['artifacts']==187 and candidate['candidateNotDeployed']):raise ValueError('genuine new host signed candidate first; not guest permission')
    authenticate_host();host=remote_identity();raw=payload(candidate['manifestSha256'])
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    with(out/'payload.private.py').open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=150)
    for name,blob in(('stdout.private.log',result.stdout),('stderr.private.log',result.stderr)):
        with(out/name).open('xb')as f:f.write(blob);f.flush();os.fsync(f.fileno())
    value={'actualExit':result.returncode,'source':CURRENT,'candidateSource':SOURCE,'candidateBOM':candidate['manifestSha256'],
      'host':host,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'vmStateChangingActions':0,'admissionAuthorityIssued':False,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in('result','host')}))
    if result.returncode==0:print(json.dumps({k:value['result'][k]for k in('deployedSource','release','bomSha256','guestBoot','artifactsVerified','signatureVerifyExit','units')}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
