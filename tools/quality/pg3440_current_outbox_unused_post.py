"""Independent full current data/resource and unused signed187 post; no operation replay."""
import ast
import hashlib
import json
import os
import subprocess

from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg1685_unused_candidate_independent_post import EXTRA
import pg3434_current_outbox_candidate_sources as role

SLOT = 'pg3440-current-outbox-unused-independent-post-v1'


def payload():
    role.qualify()
    original = W / 'pg3430-current-a9-readonly-before-v1'
    raw = (original / 'payload.private.py').read_text()
    receipt = json.loads((original / 'manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or hashlib.sha256(raw.encode()).hexdigest() != receipt['payloadSha256']:
        raise ValueError('actual same-current full independent reader unchanged')
    tree = ast.parse(raw)
    result = next(n for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'result' for t in n.targets))
    raw = ''.join(raw.splitlines(keepends=True)[:result.lineno - 1])
    candidate = json.loads((W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
    extra = EXTRA
    for old, new in [('pg1684-completed-unused-placement-v4', role.SAVE),
                     ('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37', role.BEFORE),
                     ('PG1638', 'PG3420'), ('pg1638', 'pg3420'),
                     ('2741c4546afad6c1e8b6efbd53dfb58144edf7bb', role.SOURCE),
                     ('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1', candidate['manifestSha256']),
                     ('5e32c12cc0231fd9ac307d3ffdfe6428aa53002e0398248cf32362d903d4aca5', candidate['signatureSha256'])]:
        extra = extra.replace(old, new)
    extra = extra.replace('genuineParentDone=true\\n', 'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    raw += '\n' + extra + r'''
# The canonical maintenance view has ten fields; native remains a separate
# independently compared full metadata tree, never candidate coverage credit.
require(set(after)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
require(native==after['native'])
after={k:v for k,v in after.items()if k!='native'}
require(json.dumps(after,sort_keys=True).encode()==(base/'pg3432-current-a9-before-view-v2/before.private.json').read_bytes())
save=base/'pg3440-current-outbox-unused-independent-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native,'candidateManifestSha256':hashlib.sha256(manifest_raw).hexdigest()},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'run':'pg3440-current-outbox-unused-independent-post-v1','postSha256':hashlib.sha256(encoded).hexdigest(),'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'allOriginalBackupAndNativeUnchanged':True,'unusedCandidate187Verified':True,'signatureVerified':True,'candidateSource':c['source']['commit'],'candidateManifestSha256':hashlib.sha256(manifest_raw).hexdigest(),'currentEpochApprovalUnchanged':True,'signals0':True,'candidateNativeCredit':False,'formalAccepted':False}))
'''
    if check(raw, '<independent warm unused current/candidate post>'):
        raise ValueError('complete independent post namespace')
    compile(raw, '<full24/187/current native preserved>', 'exec')
    return raw


def main():
    placement = json.loads((W / 'pg3438-place-v1.safe.json').read_bytes())
    if placement['actualExit'] != 0 or placement['sourceQualified'] is not True or placement['currentApprovalEpochChanged'] is not False:
        raise ValueError('genuine original unused placement0 required')
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed independent observer')
    os.umask(0o077); out = W / SLOT; out.mkdir()
    raw = payload().encode(); (out / 'payload.private.py').write_bytes(raw)
    with management_gate(P / 'current-management-critical.lock'):
        actual = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw, capture_output=True, timeout=120)
    (out / 'stderr.private.log').write_bytes(actual.stderr)
    value = {'actualExit': actual.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'formalAccepted': False}
    if actual.returncode == 0:
        value['guest'] = json.loads(actual.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value)); return actual.returncode


if __name__ == '__main__':
    raise SystemExit(main())
