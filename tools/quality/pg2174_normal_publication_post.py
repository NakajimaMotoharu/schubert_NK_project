"""Independent all phases/new current signature, normal Unit byte/inode unchanged."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1696_completed_publication_independent_post import PUBLIC_AFTER
from pg2170_normal_publication_sources import TOOLS,SAVE,BOM,BEFORE
from pg2132_current_normal_unused_sources import CURRENT_BOM,CURRENT,production

SLOT='pg2174-normal-publication-full-post-v1'


def payload():
    path=W/'pg2130-current-normal-before-v1/payload.private.py';raw=path.read_text()
    proof=json.loads((path.parent/'manifest.safe.json').read_bytes())
    fixed=json.loads((W/'pg2171-frozen-v1.safe.json').read_bytes())
    if proof['actualExit']!=0 or hashlib.sha256(raw.encode()).hexdigest()!=proof['payloadSha256']or fixed['actualExit']!=0:
        raise ValueError('qualified all original reader and whole current publication ABI required')
    raw=raw[:raw.index("save=base/'pg2130-current-normal-before-v1'")]
    extra=PUBLIC_AFTER
    for old,new in [('pg1694-completed-ordinary-publication-v1',SAVE),('pg1691-completed-publication-tools-v1',TOOLS),('pg1691_ordinary_publication_contract','pg2170_ordinary_publication_contract'),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',BEFORE)]:extra=extra.replace(old,new)
    extra=extra.replace('genuineParentDone=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    extra=extra.replace("oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)","for stamp,phase,observed in phases:oracle['verify'](public_first,observed,phase,expected_epoch,lower,upper)")
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one normal independent scope boundary required')
    raw=raw.replace(marker,'\n'+extra+marker)
    # Change only verifier identity: historical stop/original metadata remain old/current.
    needle="'/opt/schubert-nk/releases/0.1.0-PG1846' and hashlib.sha256(manifest).hexdigest() == '"+CURRENT_BOM+"'"
    if raw.count(needle)!=1:raise ValueError('one explicit old/new current verifier tuple required')
    raw=raw.replace(needle,"'/opt/schubert-nk/releases/0.1.0-PG2126' and hashlib.sha256(manifest).hexdigest() == '"+BOM+"'")
    raw=raw.replace("data['source']['commit'] == '"+CURRENT+"'","data['source']['commit'] == '"+production()+"'")
    raw=raw.replace("str(base / 'pg1846-manifest.sig')","str(base / 'pg2126-manifest.sig')")
    raw='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\n'+raw
    raw+='''
require(native==json.loads((base/'pg2130-current-normal-before-v1/native-before.private.json').read_bytes()))
require(after['unitFilesActual']==old_after['unitFilesActual']and after['configuration']==old_after['configuration'])
require(not(publication/'daemon-reload-reserved.private').exists()and not(publication/'morning-unit-old.private').exists())
save=base/'pg2174-normal-publication-full-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native,'public':public_last},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'postSha256':hashlib.sha256(encoded).hexdigest(),'productionSource':data['source']['commit'],'candidateManifestSha256':hashlib.sha256(manifest).hexdigest(),'all24And32Unchanged':True,'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNativePreserved':True,'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'formalAccepted':False}))
'''
    from pyflakes.api import check
    if check(raw,'<normal finite publication independent post>'):raise ValueError('whole actual namespace required')
    compile(raw,'<normal finite publication independent post>','exec');return raw


def main():
    actual=json.loads((W/'pg2172-activate-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['currentApprovalEpochChanged']is not True:
        raise ValueError('actual normal finite publication required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean independent post required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if not r.returncode:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
