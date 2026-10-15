"""Independent seven-phase publication with unchanged data, units and native originals."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check

from pg1696_completed_publication_independent_post import PUBLIC_AFTER
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg3450_current_outbox_publication_sources as role

SLOT = 'pg3458-current-outbox-publication-independent-post-v1'


def compose(raw, receipt, fixed, bom):
    if (type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0
            or type(fixed.get('actualExit')) is not int or fixed['actualExit'] != 0
            or receipt.get('productionSource') != role.CURRENT
            or hashlib.sha256(raw.encode()).hexdigest() != receipt.get('payloadSha256')
            or bom != role.ro.role.BOM):
        raise ValueError('exact successful current full reader and fixed candidate ABI')
    result = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'result' for t in n.targets))
    raw = ''.join(raw.splitlines(keepends=True)[:result.lineno - 1])
    extra = PUBLIC_AFTER
    for old, new in [('pg1694-completed-ordinary-publication-v1', role.SAVE),
                     ('pg1691-completed-publication-tools-v1', role.TOOLS),
                     ('pg1691_ordinary_publication_contract', 'pg3450_ordinary_publication_contract'),
                     ('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37', role.BEFORE)]:
        extra = extra.replace(old, new)
    extra = extra.replace('genuineParentDone=true\\n', 'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    extra = extra.replace("after=json.loads(published_raw)",
                          "after=json.loads(published_raw)\nrequire('native'not in after and 'native'not in old_after)\nrequire(json.loads(pub_before)==old_after)")
    extra = extra.replace("oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)",
                          "require(len(phases)>=7 and len({stamp for stamp,phase,observed in phases})==len(phases))\nrequire(tuple(dict.fromkeys(phase for stamp,phase,observed in phases))==oracle['PHASES'])\nfor stamp,phase,observed in phases:oracle['verify'](public_first,observed,phase,expected_epoch,lower,upper)")
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('one full top-level snapshot boundary, not nested bus')
    view = """
require(set(after)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
historical_native=after['native']
after={k:v for k,v in after.items()if k!='native'}
require(json.dumps(after,sort_keys=True).encode()==(base/'pg3432-current-a9-before-view-v2/before.private.json').read_bytes())
"""
    raw = raw.replace(marker, '\n' + view + '\n' + extra + marker)
    guards = [
        ("require(str(release.readlink()) == '/opt/schubert-nk/releases/0.1.0-PG2802' and hashlib.sha256(manifest).hexdigest() == '" + role.CURRENT_BOM + "')",
         "require(str(release.readlink()) == '/opt/schubert-nk/releases/0.1.0-PG3420' and hashlib.sha256(manifest).hexdigest() == '" + bom + "')"),
        ("require(data['source']['commit'] == '" + role.CURRENT + "' and len(data['artifacts']) == 187)",
         "require(data['source']['commit'] == '" + role.production() + "' and len(data['artifacts']) == 187)"),
        ("str(base / 'pg2802-manifest.sig')", "str(base / 'pg3420-manifest.sig')")]
    for old, new in guards:
        if raw.count(old) != 1:
            raise ValueError('exact current-data/candidate guard role required')
        raw = raw.replace(old, new)
    raw = 'PUBLICATION_FILES=' + repr(fixed['fileHashes']) + '\n' + raw
    raw += """
require(native==historical_native)
require(after['unitFilesActual']==old_after['unitFilesActual']and after['configuration']==old_after['configuration'])
require(not(publication/'daemon-reload-reserved.private').exists()and not(publication/'morning-unit-old.private').exists())
save=base/'pg3458-current-outbox-publication-independent-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native,'public':public_last},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'postSha256':hashlib.sha256(encoded).hexdigest(),'productionSource':data['source']['commit'],'candidateManifestSha256':hashlib.sha256(manifest).hexdigest(),'sevenFinitePhasesVerified':True,'all24And32Unchanged':True,'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNativePreserved':True,'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'formalAccepted':False}))
"""
    if check(raw, '<whole independent seven-phase candidate publication>'):
        raise ValueError('all independent namespace exports required')
    compile(raw, '<currenta9 data and new4856 finite publication>', 'exec')
    return raw


def payload():
    p = W / 'pg3430-current-a9-readonly-before-v1'
    return compose((p / 'payload.private.py').read_text(), json.loads((p / 'manifest.safe.json').read_bytes()),
                   json.loads((W / 'pg3452-frozen-v1.safe.json').read_bytes()), role.candidate_bom())


def main():
    actual = json.loads((W / 'pg3454-activate-v1.safe.json').read_bytes())
    if (type(actual.get('actualExit')) is not int or actual['actualExit'] != 0
            or actual.get('sourceQualified') is not True
            or actual.get('currentApprovalEpochChanged') is not True
            or actual.get('unitExchangeAndReload') is not False):
        raise ValueError('genuine finite publication0, no Unit/reload, required')
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('fixed clean independent post')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir()
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    with management_gate(P / 'current-management-critical.lock'):
        actual = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw, capture_output=True, timeout=120)
    (out / 'stderr.private.log').write_bytes(actual.stderr)
    value = {'actualExit': actual.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'formalAccepted': False}
    if actual.returncode == 0:
        value['guest'] = json.loads(actual.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return actual.returncode


if __name__ == '__main__':
    raise SystemExit(main())
