"""Independent old-current whole post plus new signed unused sibling187."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1685_unused_candidate_independent_post import EXTRA
from pg2144_normal_unused_fixed_sources import SAVE

SLOT='pg2150-normal-unused-independent-post-v1'


def payload():
    path=W/'pg2130-current-normal-before-v1/payload.private.py';raw=path.read_text()
    manifest=json.loads((path.parent/'manifest.safe.json').read_bytes())
    candidate=json.loads((W/'pg2126-candidate-build-v1.safe.json').read_bytes())
    if manifest['actualExit']!=0 or hashlib.sha256(raw.encode()).hexdigest()!=manifest['payloadSha256']or candidate['actualExit']!=0:
        raise ValueError('qualified independent current and signed candidate required')
    marker="save=base/'pg2130-current-normal-before-v1'";raw=raw[:raw.index(marker)]
    extra=EXTRA
    for old,new in [('pg1684-completed-unused-placement-v4',SAVE),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37','75669b01c69e4ecc2459e73dbd3e0a6abcac7cdfaf6ce4095561314d533b1eb4'),('PG1638','PG2126'),('pg1638','pg2126'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',candidate['candidateSource']),('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',candidate['manifestSha256']),('5e32c12cc0231fd9ac307d3ffdfe6428aa53002e0398248cf32362d903d4aca5',candidate['signatureSha256'])]:extra=extra.replace(old,new)
    extra=extra.replace('genuineParentDone=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    raw+=extra
    raw+="require(native==json.loads((base/'pg2130-current-normal-before-v1/native-before.private.json').read_bytes()))\n"
    raw+='''
save=base/'pg2150-normal-unused-independent-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native,'candidateManifestSha256':hashlib.sha256(manifest_raw).hexdigest()},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'postSha256':hashlib.sha256(encoded).hexdigest(),'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'allOriginalBackupAndNativeUnchanged':True,'unusedCandidate187Verified':True,'signatureVerified':True,'candidateSource':c['source']['commit'],'candidateManifestSha256':hashlib.sha256(manifest_raw).hexdigest(),'currentEpochApprovalUnchanged':True,'signals0':True,'formalAccepted':False}))
'''
    from pyflakes.api import check
    if check(raw,'<normal current and unused candidate independent post>'):raise ValueError('whole actual exports required')
    compile(raw,'<normal current and unused candidate independent post>','exec');return raw


def main():
    actual=json.loads((W/'pg2146-place-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['currentApprovalEpochChanged']is not False:raise ValueError('actual completed immutable unused placement required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean independent operator required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
