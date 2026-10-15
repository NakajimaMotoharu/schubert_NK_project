"""Explicit immutable-after/current original+intent+runtime receipt, no admission authority."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg3564_current_browser_resume_sources import SOURCE

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg3674-current-intent-runtime-receipt-v1'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3674-current-intent-runtime-receipt-v1'


def main():
    term=json.loads((W/'pg3582-current-browser-terminal-v1/manifest.safe.json').read_bytes());post=json.loads((W/'pg3668-current-browser-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
    if not(term['actualExit']==post['actualExit']==0 and post['productionSource']==SOURCE and post['exactRuntimeEntryRetired']):raise ValueError('genuine current terminal/retired fullpost required')
    raw='AFTER_SHA='+repr(post['proofHashes']['after.private.json']['sha256'])+'\nDONE_SHA='+repr(term['proofHashes']['done.private'])+'\n'+r'''
from pathlib import Path
import json,hashlib,os,stat,datetime
require=lambda v:None if v else (_ for _ in ()).throw(ValueError('current original intent/runtime receipt refused'))
base=Path('/var/lib/pgpt-s1-preservation');raw=(base/'pg3662-native-stop-v1/after.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==AFTER_SHA)
after=json.loads(raw);require(len(after)==11 and len(after['rows'])==24 and 'native'in after)
require(Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
startup=Path('/run/schubert-nk/startup');require(not any(p.name.endswith('.start.intent')for p in startup.iterdir())and not any(Path(p).name.endswith('.start.intent')for p in after['startup']))
active=Path('/var/lib/schubert-nk/maintenance/active');require(not os.path.lexists(active)and str(active)not in after['originals'])
done=Path('/var/lib/schubert-nk/maintenance/attempts/784b8508-7dcd-415d-9b85-3855f4335a8c.done');contents=done.read_bytes();require(hashlib.sha256(contents).hexdigest()==DONE_SHA and after['originals'][str(done)]['sha256']==DONE_SHA)
lines=contents.decode('ascii').splitlines();require(lines==['NKDONE1','e1ee096d-370b-4ab9-915a-7c124207e854','2026-10-15T16:49:02.160964Z','784b8508-7dcd-415d-9b85-3855f4335a8c','2026-10-15T20:35:59.251066Z','10'])
root=Path('/run/systemd/system');directory=root/'schubert-nk-morning-controller.service.d';require(set(after['runtime'])=={str(root),str(directory)}and list(root.iterdir())==[directory]and not list(directory.iterdir()))
for p in [root,directory]:
 s=p.lstat();require(stat.S_ISDIR(s.st_mode)and not p.is_symlink()and not os.listxattr(p))
 require([s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==after['runtime'][str(p)]['metadata'])
require(sum(Path(p).suffix=='.exec'for p in after['native'])==34)
print(json.dumps({'actualExit':0,'productionSource':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2','observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retiredAfterSha256':AFTER_SHA,'snapshotFields':11,'nativePhysicalFiles':34,'currentOriginalDoneSha256':DONE_SHA,'currentOriginalNormalWarning10':True,'noMaintenanceActiveOriginal':True,'noStartupStartIntents':True,'exactUsedRuntimeAbsent':True,'sameOriginalEmptyParentMetadata':True,'runtimeEntries':2,'newAuthorityIssued':False,'startsStopsReloadsSqlWrites':0,'rawExported':False,'formalAccepted':False}))
'''
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=45)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True))
    if not r.returncode:
        PUBLIC.mkdir(parents=True)
        with(PUBLIC/'manifest.json').open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
