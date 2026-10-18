"""Fresh existing A2 VM, exact owned forward/BOM187/signature; no boot/reload/stage authority."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg3428_vm_candidate_preflight_readonly as previous
from pg4996_resume_connection import authenticate_host,remote_identity
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import W,P,SSH

CURRENT='a2ecc77ca312c383246c94ea692c4db7487112cd'
CURRENT_BOM='78a6f8631f188303dd28b4470868564599beda23e9cc5b5a983c7535fea56ef4'
CANDIDATE='29612b2a484a5ab7418e02a491c4360af7444626'
CANDIDATE_BOM='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6'
SLOT='pg5432-current-vm-reauthentication-v1'


def payload():
    raw=previous.GUEST
    replacements={
        '37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863':CURRENT_BOM,
        'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25':CURRENT,
        '0.1.0-PG2802':'0.1.0-PG4980','pg2802-manifest.sig':'pg4980-manifest.sig'}
    for before,after in replacements.items():
        if raw.count(before)!=1:raise ValueError('one exact current identity scalar '+before[:12])
        raw=raw.replace(before,after,1)
    marker="'expiry-cleanup','inbox-inspector'"
    if raw.count(marker)!=1:raise ValueError('all fixed current Unit selectors')
    raw=raw.replace(marker,"'expiry-cleanup','inbox-inspector','bootstrap-admin'",1)
    marker="'oldNativeTransferred':False"
    if raw.count(marker)!=1:raise ValueError('one data-only result boundary')
    raw=raw.replace(marker,marker+",'candidateSource':"+repr(CANDIDATE)+",'candidateBOM':"+repr(CANDIDATE_BOM)+",'candidatePlaced':False,'dataOnlyNotRuntimeAuthority':True",1)
    if check(raw,'<fresh A2 all187 current signature readonly>'):raise ValueError('standalone static0')
    compile(raw,'<fresh existing guest, never boot fallback>','exec')
    return raw


def main():
    authenticate_host();host=remote_identity()
    candidate=json.loads((W/'pg5430-candidate-build-v1.safe.json').read_bytes())
    if candidate['actualExit']!=0 or candidate['candidateSource']!=CANDIDATE or candidate['manifestSha256']!=CANDIDATE_BOM or candidate['signatureVerified'] is not True:
        raise ValueError('actual host candidate first; not a guest permission')
    raw=payload();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    with(out/'payload.private.py').open('x') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=150)
    with(out/'stdout.private.log').open('xb') as stream:stream.write(result.stdout);stream.flush();os.fsync(stream.fileno())
    with(out/'stderr.private.log').open('xb') as stream:stream.write(result.stderr);stream.flush();os.fsync(stream.fileno())
    value={'actualExit':result.returncode,'source':CURRENT,'candidateSource':CANDIDATE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),
        'host':host,'vmStateChangingActions':0,'admissionAuthorityIssued':False,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    with(out/'manifest.safe.json').open('x') as stream:json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({key:value[key] for key in ('actualExit','source','candidateSource','payloadSha256','vmStateChangingActions','admissionAuthorityIssued')}))
    if result.returncode==0:
        observed=value['result'];print(json.dumps({key:observed[key] for key in ('deployedSource','release','bomSha256','guestBoot','artifactsVerified','signatureVerifyExit','units')}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
