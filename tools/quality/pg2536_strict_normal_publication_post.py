"""Independent finite seven-phase publication with current ten-field/native separate schema."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg1696_completed_publication_independent_post import PUBLIC_AFTER
from pg2532_strict_normal_publication_sources import TOOLS, SAVE, BEFORE, CURRENT, CURRENT_BOM, production, candidate_bom

SLOT = 'pg2536-strict-normal-publication-post-v1'


def compose(raw, receipt, fixed, bom):
    for value in [receipt, fixed]:
        if type(value) is not dict or type(value.get('actualExit')) is not int or value['actualExit'] != 0:
            raise ValueError('actual independent reader and complete publication ABI required')
    if receipt.get('productionSource') != CURRENT or receipt.get('privateBeforeSha256') != BEFORE:
        raise ValueError('exact current original receipt required')
    if hashlib.sha256(raw.encode()).hexdigest() != receipt.get('payloadSha256'):
        raise ValueError('actual current reader bytes required')
    if type(bom) is not str or len(bom) != 64 or set(bom) - set('0123456789abcdef'):
        raise ValueError('exact new candidate BOM required')
    marker = "save=base/'pg2514-current-cdbc-before-v2'"
    if raw.count(marker) != 1:
        raise ValueError('one current original reader save boundary required')
    raw = raw[:raw.index(marker)]
    extra = PUBLIC_AFTER
    for before, after in [('pg1694-completed-ordinary-publication-v1', SAVE),
        ('pg1691-completed-publication-tools-v1', TOOLS),
        ('pg1691_ordinary_publication_contract', 'pg2532_ordinary_publication_contract'),
        ('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37', BEFORE)]:
        extra = extra.replace(before, after)
    extra = extra.replace('genuineParentDone=true\\n', 'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    # Current originals already have ten fields. No historical native insertion,
    # subtraction or fake equality; the separate native file is compared below.
    extra = extra.replace("after=json.loads(published_raw)",
        "after=json.loads(published_raw)\nrequire('native' not in after and 'native' not in old_after)\nrequire(json.loads(pub_before)==old_after)")
    extra = extra.replace("oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)",
        "require(len(phases)>=7 and len({stamp for stamp,phase,observed in phases})==len(phases))\nrequire(tuple(dict.fromkeys(phase for stamp,phase,observed in phases))==oracle['PHASES'])\nfor stamp,phase,observed in phases:oracle['verify'](public_first,observed,phase,expected_epoch,lower,upper)")
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('one whole independent snapshot boundary required')
    raw = raw.replace(marker, '\n' + extra + marker)
    old = "'/opt/schubert-nk/releases/0.1.0-PG2428' and hashlib.sha256(manifest).hexdigest() == '" + CURRENT_BOM + "'"
    if raw.count(old) != 1:
        raise ValueError('one exact current manifest/source tuple required')
    raw = raw.replace(old, "'/opt/schubert-nk/releases/0.1.0-PG2512' and hashlib.sha256(manifest).hexdigest() == '" + bom + "'")
    for old, new in [("data['source']['commit'] == '" + CURRENT + "'", "data['source']['commit'] == '" + production() + "'"),
                     ("data['source']['commit']=='" + CURRENT + "'", "data['source']['commit']=='" + production() + "'"),
                     ("str(base / 'pg2428-manifest.sig')", "str(base / 'pg2512-manifest.sig')")]:
        if old not in raw:
            raise ValueError('complete candidate current-data guards required')
        raw = raw.replace(old, new)
    raw = 'PUBLICATION_FILES=' + repr(fixed['fileHashes']) + '\n' + raw
    raw += """
require(native==json.loads((base/'pg2514-current-cdbc-before-v2/native-before.private.json').read_bytes()))
require(after['unitFilesActual']==old_after['unitFilesActual']and after['configuration']==old_after['configuration'])
require(not(publication/'daemon-reload-reserved.private').exists()and not(publication/'morning-unit-old.private').exists())
save=base/'pg2536-strict-normal-publication-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native,'public':public_last},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'postSha256':hashlib.sha256(encoded).hexdigest(),'productionSource':data['source']['commit'],'candidateManifestSha256':hashlib.sha256(manifest).hexdigest(),'sevenFinitePhasesVerified':True,'all24And32Unchanged':True,'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNativePreserved':True,'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'formalAccepted':False}))
"""
    if check(raw, '<new finite publication independent complete post>'):
        raise ValueError('all independent namespace exports required')
    compile(raw, '<current ten-field publication full post>', 'exec')
    return raw


def payload():
    path = W / 'pg2514-current-cdbc-before-v2/payload.private.py'
    receipt = json.loads((path.parent / 'manifest.safe.json').read_bytes())
    fixed = json.loads((W / 'pg2533-frozen-v1.safe.json').read_bytes())
    return compose(path.read_text(), receipt, fixed, candidate_bom())


def main():
    actual = json.loads((W / 'pg2534-activate-v1.safe.json').read_bytes())
    if (type(actual.get('actualExit')) is not int or actual['actualExit'] != 0
            or actual.get('sourceQualified') is not True or actual.get('currentApprovalEpochChanged') is not True
            or actual.get('unitExchangeAndReload') is not False):
        raise ValueError('actual finite publication without Unit/reload required')
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed observer required')
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700)
    raw = payload().encode(); (out / 'payload.private.py').write_bytes(raw)
    with management_gate(P / 'current-management-critical.lock'):
        result = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw, capture_output=True, timeout=120)
    (out / 'stderr.private.log').write_bytes(result.stderr)
    value = {'actualExit':result.returncode, 'payloadSha256':hashlib.sha256(raw).hexdigest(), 'formalAccepted':False}
    if not result.returncode:
        value['guest'] = json.loads(result.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
