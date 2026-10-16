"""Independent unused-placement full current/24/native34/config32 and candidate187 verification."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg3752_current_preservation_readonly as readonly
import pg3756_hygiene_unused_sources as role


EXTRA=r'''
# No capture uses candidate Production code or treats old Root/exec as new authority.
for name,item in expected['unitFilesActual'].items():
 p=Path(name);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==item)
for unit,oldcfg in expected['configuration'].items():
 r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],capture_output=True,text=True,timeout=10);require(r.returncode==0);cfg=complete_configuration(r.stdout,unit);require(cfg==oldcfg)
candidate=Path('/opt/schubert-nk/releases/0.1.0-PG3748');manifest_raw=(candidate/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest_raw).hexdigest()==CANDIDATE['manifestSha256']);c=json.loads(manifest_raw);require(c['source']['commit']==CANDIDATE['candidateSource']and c['release']=='0.1.0-PG3748'and len(c['artifacts'])==187)
for row in c['artifacts']:
 p=candidate/row['path'];require(p.resolve().is_relative_to(candidate)and not p.is_symlink()and p.is_file()and p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
sig=Path('/var/lib/pgpt-s1-preservation/pg3748-manifest.sig');require(sig.stat().st_size==64 and hashlib.sha256(sig.read_bytes()).hexdigest()==CANDIDATE['signatureSha256']);verify=subprocess.run(['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],capture_output=True,timeout=10);require(verify.returncode==0)
require(set(str(p.relative_to(candidate))for p in candidate.rglob('*')if p.is_file())=={r['path']for r in c['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'}and not any(p.is_symlink()for p in candidate.rglob('*')))
before=Path('/var/lib/pgpt-s1-preservation/pg3754-current-4856-before-view-v1/before.private.json').read_bytes();require(hashlib.sha256(before).hexdigest()==BEFORE and json.loads(before)=={k:v for k,v in expected.items()if k!='native'})
require(str(Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG3420')
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'currentSource':data['source']['commit'],'candidateSource':c['source']['commit'],'candidateManifestSha256':CANDIDATE['manifestSha256'],'candidate187SignatureVerified':True,'current187SignatureVerified':True,'all24TablesEqualTwice':True,'allTenKernelJob0':True,'configuration32EveryFieldUnchanged':True,'allUnitFileBytesMetadataUnchanged':True,'originalBackupCredentialOldProofsPreserved':True,'native34Preserved':True,'runtimeStartupAndApprovalEpochUnchanged':True,'allClientAdvisoryMA0':True,'candidateUnusedOnly':True,'noSignalsOrStartsOrReloads':True,'candidateNativeCredit':False,'dbWrites':0,'guestFilesWritten':0,'formalAccepted':False}))
'''


def payload():
    raw=readonly.payload();tree=ast.parse(raw);last=tree.body[-1]
    if not(isinstance(last,ast.Expr)and isinstance(last.value,ast.Call)and isinstance(last.value.func,ast.Name)and last.value.func.id=='print'):raise ValueError('one final readonly result boundary')
    raw=''.join(raw.splitlines(keepends=True)[:last.lineno-1]);capture=role.pinned(role.W/role.TOOLS,'pg3756_configuration_capture.py');candidate=json.loads((W/'pg3748-candidate-build-v1.safe.json').read_bytes());result='CANDIDATE='+repr(candidate)+'\nBEFORE='+repr(role.BEFORE)+'\n'+raw+'\n'+capture+'\n'+EXTRA
    if check(result,'<full independent current/candidate post>'):raise ValueError('complete independent post namespace')
    compile(result,'<full187/24/native34/config32 unused post>','exec');return result


def main():
    placement=json.loads((W/'pg3760-place-v1.safe.json').read_bytes());assert placement['actualExit']==0 and placement['sourceQualified']and not placement['currentApprovalEpochChanged']
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed independent post')
    os.umask(0o077);out=W/'pg3762-hygiene-unused-post-v1';out.mkdir();raw=payload();(out/'payload.private.py').write_text(raw);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stdout.safe.json').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'currentSource':role.CURRENT,'candidateSource':role.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
