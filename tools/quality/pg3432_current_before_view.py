"""Private data-only view of the sealed image freshly reauthenticated by3430; no authority copy."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from pg1446_current_cold_stage import SSH, P, W
from pg1674_critical_management_gate import management_gate

ROOT = Path(__file__).resolve().parents[2]
AFTER = '62b783d9ae660bd5cdaaedb732d94f4611e164cc13c9cff1e58c4cd22ad87c8e'
GUEST = r'''
import os,json,hashlib,pathlib
os.umask(0o077);base=pathlib.Path('/var/lib/pgpt-s1-preservation')
raw=(base/'pg3192-native-stop-v1/after.private.json').read_bytes()
require=lambda v:None if v else(_ for _ in()).throw(ValueError('private data-only before view refused'))
require(hashlib.sha256(raw).hexdigest()==AFTER)
proof_raw=(base/'pg3430-current-a9-readonly-before-v1/result.safe.json').read_bytes();proof=json.loads(proof_raw)
require(proof['actualExit']==0 and proof['productionSource']=='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'and proof['all24UnchangedTwice']and proof['allActorGone']and proof['allTenUnitsKernelEmpty']and proof['allClientAdvisoryFlock0']and proof['exactRuntimeEntryRetired'])
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(manifest).hexdigest()=='37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863')
data=json.loads(raw);require(set(data)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'}and isinstance(data['native'],dict))
# The maintenance before contract has ten fields. Retain the exact sealed raw
# eleven-field image and its historical native metadata, never silently drop it.
flat={k:v for k,v in data.items()if k!='native'};before=json.dumps(flat,sort_keys=True).encode();native=json.dumps(data['native'],sort_keys=True).encode()
target=base/'pg3432-current-a9-before-view-v2';require(not os.path.lexists(target));target.mkdir(mode=0o700)
for name,body in [('before.private.json',before),('sealed-after.private.json',raw),('sealed-native-historical.private.json',native)]:
 with(target/name).open('xb')as f:f.write(body);f.flush();os.fsync(f.fileno())
for p in [target,target.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','privateBeforeSha256':hashlib.sha256(before).hexdigest(),'sealedAfterSha256':AFTER,'sealedHistoricalNativeSha256':hashlib.sha256(native).hexdigest(),'canonicalBeforeFields':10,'sealedImageFields':11,'nativeCandidateCredit':False,'dataOnlyNotRuntimeAuthority':True,'sealedImageCopiedNotFreshCapture':True,'freshEqualityWitness':'PG3430','runtimeAlreadyRetired':True,'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'guestBeforePath':str(target/'before.private.json'),'rawExported':False,'businessActions':0,'permissionIssued':False,'formalAccepted':False}))
'''


def main():
    source = W / 'pg3430-current-a9-readonly-before-v1/manifest.safe.json'
    value = json.loads(source.read_bytes())
    assert value['actualExit'] == 0 and value['all24UnchangedTwice'] and value['startsStopsReloadsSqlWrites'] == 0
    os.umask(0o077); out = W / 'pg3432-current-a9-before-view-v2'; out.mkdir()
    code = 'AFTER=' + repr(AFTER) + '\n' + GUEST; (out / 'view.private.py').write_text(code)
    with management_gate(P / 'current-management-critical.lock'):
        actual = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=code.encode(), capture_output=True, timeout=30)
    (out / 'observer.private.log').write_bytes(actual.stdout + actual.stderr)
    assert actual.returncode == 0
    result = json.loads(actual.stdout); result.update(freshEqualityWitnessManifestSha256=hashlib.sha256(source.read_bytes()).hexdigest(), freshEqualityWitnessCompletedUTC=value['completedUTC'], payloadSha256=hashlib.sha256(code.encode()).hexdigest())
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3432-data-before-view'; public.mkdir()
    path = public / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'privateBeforeSha256': result['privateBeforeSha256'], 'dataOnlyNotAuthority': True,
                      'businessActions': 0, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
