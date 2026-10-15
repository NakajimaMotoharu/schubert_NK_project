"""Preserve exact sealed11/native and explicit canonical10 as data only, never old authority."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg3752_current_preservation_readonly import CURRENT,BOM


GUEST=r'''
import os,json,hashlib
from pathlib import Path
require=lambda v:None if v else(_ for _ in()).throw(ValueError('new-only data-only preservation view refused'))
os.umask(0o077);base=Path('/var/lib/pgpt-s1-preservation');p=base/'pg3662-native-stop-v1/after.private.json';raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()==PROOF['afterSha256'])
require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()==PROOF['guestBoot']);manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==PROOF['BOM'])
require(PROOF['all187ArtifactSignatureVerified']and PROOF['allTenKernelJob0']and PROOF['all24TablesEqualTwice']and PROOF['dbClientsAdvisoryMA0']and PROOF['native34Preserved']and PROOF['currentOriginalClosedAndNoIntent'])
data=json.loads(raw);require(set(data)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'}and len(data['rows'])==24 and sum(Path(p).suffix=='.exec'for p in data['native'])==34)
before=json.dumps({k:v for k,v in data.items()if k!='native'},sort_keys=True).encode();native=json.dumps(data['native'],sort_keys=True).encode();require(os.statvfs(base).f_bavail*os.statvfs(base).f_frsize>len(raw)+len(before)+len(native)+256*1024**2)
target=base/'pg3754-current-4856-before-view-v1';require(not os.path.lexists(target));target.mkdir(mode=0o700)
for name,body in [('before.private.json',before),('sealed-after.private.json',raw),('sealed-native-historical.private.json',native)]:
 with(target/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(body);f.flush();os.fsync(f.fileno())
for d in [target,base]:
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
require(p.read_bytes()==raw and hashlib.sha256(Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()==PROOF['BOM'])
print(json.dumps({'actualExit':0,'productionSource':PROOF['deployedSource'],'BOM':PROOF['BOM'],'guestBoot':PROOF['guestBoot'],'privateBeforeSha256':hashlib.sha256(before).hexdigest(),'sealedAfterSha256':PROOF['afterSha256'],'sealedHistoricalNativeSha256':hashlib.sha256(native).hexdigest(),'canonicalBeforeFields':10,'sealedImageFields':11,'nativePhysicalFilesPreserved':34,'dataOnlyNotRuntimeAuthority':True,'nativeCandidateCredit':False,'rawExported':False,'guestBeforePath':str(target/'before.private.json'),'newPrivateDataFiles':3,'dbWrites':0,'unitActions':0,'candidateDeployed':False,'formalAccepted':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed data-only view operator')
    path=W/'pg3752-current-preservation-readonly-v1/manifest.safe.json';proof=json.loads(path.read_bytes());r=proof['result'];assert proof['actualExit']==r['actualExit']==0 and r['deployedSource']==CURRENT and r['BOM']==BOM
    os.umask(0o077);out=W/'pg3754-current-before-view-v1';out.mkdir();raw='PROOF='+repr(r)+'\n'+GUEST;(out/'view.private.py').write_text(raw);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):v=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=45)
    (out/'stdout.safe.json').write_bytes(v.stdout);(out/'stderr.private.log').write_bytes(v.stderr);value={'actualExit':v.returncode,'source':CURRENT,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'freshReadOnlyProofSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not v.returncode:value['result']=json.loads(v.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return v.returncode


if __name__=='__main__':raise SystemExit(main())
