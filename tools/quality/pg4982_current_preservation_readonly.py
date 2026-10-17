"""Fresh current04bb/all80 read before new4980 unused candidate, never old startup authority."""
import hashlib
import json
from pyflakes.api import check
import pg4938_current_bootstrap_post as completed
import pg4900_current_admission_image as admission

W=admission.W
SOURCE,BOM=admission.SOURCE,admission.BOM
CANDIDATE='a2ecc77ca312c383246c94ea692c4db7487112cd'
CANDIDATE_BOM='78a6f8631f188303dd28b4470868564599beda23e9cc5b5a983c7535fea56ef4'
SLOT='pg4982-current-preservation-readonly-v1'
FIELDS=('backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native')


def payload():
    signed=json.loads((W/'pg4980-candidate-build-v1.safe.json').read_bytes())
    if not(type(signed['actualExit'])is int and signed['actualExit']==0 and signed['candidateSource']==CANDIDATE
        and signed['priorSource']==SOURCE and signed['manifestSha256']==CANDIDATE_BOM
        and signed['signatureVerified']is True and signed['candidateNotDeployed']is True):raise ValueError('actual distinct host candidate, no guest authority')
    outer=json.loads((W/completed.SLOT/'manifest.safe.json').read_bytes());past=outer['result']
    raw=(W/completed.SLOT/'payload.private.py').read_text()
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==SOURCE
        and past['productionSource']==SOURCE and past['nativePhysicalFiles']==80 and past['allResources0']is True
        and past['capturedNormal20VerifiedBeforeCurrent']is True and past['currentCredentialsRetired']is True
        and hashlib.sha256(raw.encode()).hexdigest()==outer['payloadSha256']):raise ValueError('immutable closed current04bb captured20/all80 data only')
    marker='save=base/'+repr(completed.SLOT)
    if raw.count(marker)!=1:raise ValueError('one evidence-only new output namespace')
    raw=raw.replace(marker,'save=base/'+repr(SLOT),1)
    marker='    fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)'
    if raw.count(marker)!=1:raise ValueError('one held metadata/ten-reference final boundary')
    extra="""
    require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))
    require(not list(pathlib.Path('/run/schubert-nk/startup').glob('*.start.intent')))
    full11={name:value[name]for name in FRESH_FIELDS}
    require(len(full11['rows'])==24 and len(full11['units'])==10 and sum(p.endswith('.exec')for p in full11['native'])==80)
    fresh_raw=json.dumps(full11,sort_keys=True).encode()
    with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(fresh_raw);f.flush();os.fsync(f.fileno())
"""
    raw=raw.replace(marker,extra+marker,1)
    marker="'formalAccepted':False}))"
    if raw.count(marker)!=1:raise ValueError('one allowlisted terminal result only')
    raw=raw.replace(marker,"'formalAccepted':False,'freshCurrentPreservation':True,'dataOnlyNotRuntimeAuthority':True,'candidateSource':CANDIDATE,'candidateBOM':CANDIDATE_BOM,'candidateDeployed':False,'nativeCandidateCredit':False,'privateBeforeSha256':hashlib.sha256(fresh_raw).hexdigest(),'sealedFull11Fields':11}))",1)
    raw='FRESH_FIELDS='+repr(FIELDS)+'\nCANDIDATE='+repr(CANDIDATE)+'\nCANDIDATE_BOM='+repr(CANDIDATE_BOM)+'\n'+raw
    if check(raw,'<fresh current04bb preserved originals/DB/all80>'):raise ValueError('complete current reader namespace static0')
    compile(raw,'<data-only current before candidate; no old success authority>','exec');return raw


def main():return admission.execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
