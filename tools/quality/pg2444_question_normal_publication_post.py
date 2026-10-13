"""Independent seven finite phases plus retained DB/Backup/native/Unit postconditions."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1696_completed_publication_independent_post import PUBLIC_AFTER
from pg2440_question_normal_publication_sources import TOOLS,SAVE,BOM,BEFORE,CURRENT,CURRENT_BOM,production

SLOT='pg2444-question-normal-publication-post-v1'


def payload():
    path=W/'pg2410-retired-current-before-v1/payload.private.py'
    raw=path.read_text();proof=json.loads((path.parent/'manifest.safe.json').read_bytes())
    fixed=json.loads((W/'pg2441-frozen-v1.safe.json').read_bytes())
    if proof['actualExit']!=0 or hashlib.sha256(raw.encode()).hexdigest()!=proof['payloadSha256'] or fixed['actualExit']!=0:
        raise ValueError('qualified immutable retired-current reader and whole publication ABI required')
    marker="save=base/'pg2410-retired-current-before-v1'"
    if raw.count(marker)!=1:raise ValueError('one independent full current reader boundary required')
    raw=raw[:raw.index(marker)]
    extra=PUBLIC_AFTER
    for a,b in [('pg1694-completed-ordinary-publication-v1',SAVE),
                ('pg1691-completed-publication-tools-v1',TOOLS),
                ('pg1691_ordinary_publication_contract','pg2440_ordinary_publication_contract'),
                ('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',BEFORE)]:extra=extra.replace(a,b)
    extra=extra.replace('genuineParentDone=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    # The proven retirement reader has eleven fields; maintenance publication
    # retains the independently authenticated native field in its separate file.
    extra=extra.replace("after=json.loads(published_raw)",
        "after=json.loads(published_raw)\nrequire('native' not in after and set(after)==set(old_after)-{'native'})\nrequire(json.loads(pub_before)=={k:v for k,v in old_after.items()if k!='native'})\nafter={**after,'native':old_after['native']}")
    extra=extra.replace("oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)",
        "require(len(phases)>=7 and len({stamp for stamp,phase,observed in phases})==len(phases))\nrequire(tuple(dict.fromkeys(phase for stamp,phase,observed in phases))==oracle['PHASES'])\nfor stamp,phase,observed in phases:oracle['verify'](public_first,observed,phase,expected_epoch,lower,upper)")
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one whole independent snapshot boundary required')
    raw=raw.replace(marker,'\n'+extra+marker)
    old="'/opt/schubert-nk/releases/0.1.0-PG2126' and hashlib.sha256(manifest).hexdigest() == '"+CURRENT_BOM+"'"
    if raw.count(old)!=1:raise ValueError('one current manifest/source tuple required')
    raw=raw.replace(old,"'/opt/schubert-nk/releases/0.1.0-PG2428' and hashlib.sha256(manifest).hexdigest() == '"+BOM+"'")
    raw=raw.replace("data['source']['commit'] == '"+CURRENT+"'","data['source']['commit'] == '"+production()+"'")
    raw=raw.replace("str(base / 'pg2126-manifest.sig')","str(base / 'pg2428-manifest.sig')")
    raw='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\n'+raw
    raw+='''
require(native==json.loads((base/'pg2410-retired-current-before-v1/native-before.private.json').read_bytes()))
require(after['unitFilesActual']==old_after['unitFilesActual']and after['configuration']==old_after['configuration'])
require(not(publication/'daemon-reload-reserved.private').exists()and not(publication/'morning-unit-old.private').exists())
save=base/'pg2444-question-normal-publication-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native,'public':public_last},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'postSha256':hashlib.sha256(encoded).hexdigest(),'productionSource':data['source']['commit'],'candidateManifestSha256':hashlib.sha256(manifest).hexdigest(),'sevenFinitePhasesVerified':True,'all24And32Unchanged':True,'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNativePreserved':True,'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'formalAccepted':False}))
'''
    if check(raw,'<whole finite publication independent post>'):raise ValueError('all independent namespaces required')
    compile(raw,'<whole finite publication independent post>','exec');return raw


def main():
    actual=json.loads((W/'pg2442-activate-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['currentApprovalEpochChanged']is not True or actual['unitExchangeAndReload']is not False:
        raise ValueError('actual qualified finite publication without Unit operation required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed independent observer required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if not r.returncode:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
