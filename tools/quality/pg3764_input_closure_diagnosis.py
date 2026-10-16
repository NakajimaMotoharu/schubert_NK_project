"""Read-only original helper diagnosis and no-ownership/current preservation authentication."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import types
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg3752_current_preservation_readonly as readonly


def main():
    first=json.loads((W/'pg3760-place-v1.safe.json').read_bytes());assert first['actualExit']==1 and not first['sourceQualified'];frozen=json.loads((W/'pg3758-frozen-v1.safe.json').read_bytes());os.umask(0o077);out=W/'pg3764-input-closure-before-v1';out.mkdir()
    code='PINS='+repr(frozen['fileHashes'])+'\n'+r'''
import hashlib,json,os,subprocess
from pathlib import Path
root=Path('/var/lib/pgpt-s1-preservation/pg3756-hygiene-unused-tools-v1')
for n,h in PINS.items():assert hashlib.sha256((root/n).read_bytes()).hexdigest()==h
p=root/'pg3756_input_preflight.py';lines=[l for l in p.read_text().splitlines()if l.startswith('BUNDLE_HASH=')];assert len(lines)==2
r=subprocess.run(['/usr/bin/python3','-B',str(p)],capture_output=True,text=True,timeout=30);assert r.returncode==1
assert not os.path.lexists('/var/lib/pgpt-s1-preservation/pg3760-hygiene-unused-placement-v1')and not os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG3748')and not os.path.lexists('/var/lib/pgpt-s1-preservation/pg3748-manifest.sig')
print(json.dumps({'actualExit':0,'originalHelperActualExit':r.returncode,'originalInputHelperSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bundleAssignments':len(lines),'stderrTail':r.stderr.splitlines()[-6:],'placementSaveAbsent':True,'candidateReleaseAbsent':True,'persistedCandidateSignatureAbsent':True,'ownershipAcquiredByDiagnostic':False,'guestFilesWritten':0,'startsStopsWrites':0,'allFrozenGuestFilesUnchanged':True}))
'''
    (out/'payload.private.py').write_text(code)
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=code.encode(),capture_output=True,timeout=60)
    (out/'stdout.safe.json').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
    if r.returncode:return r.returncode
    fn=types.FunctionType(readonly.main.__code__,{**readonly.__dict__,'SLOT':'pg3764-after-refusal-current-readonly-v1'},'independent_after_refusal_current_readonly');return fn()


if __name__=='__main__':raise SystemExit(main())
