"""Fresh current825e stopped data, preserving captured20 and all72 native files."""
import hashlib
import json
from pyflakes.api import check
import pg4828_new_current_bootstrap_post as completed
import pg4772_new_current_owned_sources as owner

W = completed.role.W
SOURCE, BOM = owner.SOURCE, owner.BOM
SLOT = 'pg4862-current-preservation-readonly-v1'
PREVIOUS = completed.SLOT
BEFORE = '40fa4c1cf84ae43c7727ffad8aa10f698b79133cfe3e06cdc1539c9fe0811bd2'
FIELDS = ('backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native')


def payload():
    outer = json.loads((W/PREVIOUS/'manifest.safe.json').read_bytes())
    raw = (W/PREVIOUS/'payload.private.py').read_text()
    v = outer['result']
    if not (outer['actualExit'] == 0 and outer['source'] == SOURCE and v['productionSource'] == SOURCE
            and v['nativePhysicalFiles'] == 72 and v['beforeSha256'] == BEFORE
            and v['allResources0'] and v['capturedNormal20VerifiedBeforeCurrent']
            and hashlib.sha256(raw.encode()).hexdigest() == outer['payloadSha256']):
        raise ValueError('actual closed825e full/Bootstrap20/all72 immutable original first')
    marker = "save=base/" + repr(PREVIOUS)
    if raw.count(marker) != 1: raise ValueError('one evidence-only output path')
    raw = raw.replace(marker, 'save=base/' + repr(SLOT), 1)
    marker = '    fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)'
    if raw.count(marker) != 1: raise ValueError('one actual full snapshot saved while references held')
    extra = '''
    require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))
    require(not list(pathlib.Path('/run/schubert-nk/startup').glob('*.start.intent')))
    full11={name:value[name]for name in FRESH_FIELDS}
    require(len(full11['rows'])==24 and len(full11['units'])==10 and sum(p.endswith('.exec')for p in full11['native'])==72)
    fresh_raw=json.dumps(full11,sort_keys=True).encode()
    with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(fresh_raw);f.flush();os.fsync(f.fileno())
'''
    raw = raw.replace(marker, extra + marker, 1)
    marker = "'formalAccepted':False}))"
    if raw.count(marker) != 1: raise ValueError('one original actual terminal result')
    raw = raw.replace(marker, "'formalAccepted':False,'freshCurrentPreservation':True,'dataOnlyNotRuntimeAuthority':True,'nativeCandidateCredit':False,'currentOriginalClosedAndNoIntent':True,'runtimeConfigFilesToRetire':0,'privateBeforeSha256':hashlib.sha256(fresh_raw).hexdigest(),'sealedFull11Fields':11,'genuineCompletion':FRESH_DONE}))", 1)
    _, _, genuine, _ = owner.context()
    if not (genuine['genuineParentDone'] is True and genuine['completionCode'] == 10):
        raise ValueError('actual current completed WARNING10 history, not startup authority')
    raw = 'FRESH_FIELDS=' + repr(FIELDS) + '\nFRESH_DONE=' + repr(genuine) + '\n' + raw
    if check(raw, '<fresh current stopped all72 data only>'): raise ValueError('all emitted static0')
    return raw


def main():
    candidate = json.loads((W/'pg4860-candidate-build-v1.safe.json').read_bytes())
    if not (candidate['actualExit'] == 0 and candidate['priorSource'] == SOURCE and candidate['candidateNotDeployed']):
        raise ValueError('actual distinct signed candidate first')
    return completed.role.before.admission.execute(SLOT, payload(), 150)


if __name__ == '__main__': raise SystemExit(main())
