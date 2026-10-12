"""Independent canonical phases, retained Unit inode, current187, oldWARNING full post."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg1849_warning_completed_current_before as engine
from pg1696_completed_publication_independent_post import PUBLIC_AFTER
from pg1877_warning_publication_sources import once,TOOLS,SAVE,BOM,BEFORE
from pg1844_warning_unit_full_six import CANDIDATE,OLD

SLOT='pg1882-warning-publication-full-post-v1'


def public_after():
    raw=PUBLIC_AFTER
    for old,new in [('pg1694-completed-ordinary-publication-v1',SAVE),('pg1691-completed-publication-tools-v1',TOOLS),('pg1691_ordinary_publication_contract','pg1877_ordinary_publication_contract'),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',BEFORE)]:raw=raw.replace(old,new)
    raw=raw.replace('genuineParentDone=true\\n','genuineParentWarningOriginal=true\\nmanagerFailureRetained=true\\n').replace('startsStopsReloadsEpochWrites0=true','startsStopsSqlWrites0=true\\ncanonicalEpochApprovalCurrentChanged=true\\nsoleUnitExchangedAndReloaded=true')
    raw=once(raw,"require(set(after)==set(old_after)and all(after[k]==old_after[k]for k in old_after if k!='startup'))","require(set(after)==set(old_after)and all(after[k]==old_after[k]for k in old_after if k not in {'startup','unitFilesActual'}))\nunit_path='/etc/systemd/system/schubert-nk-morning-controller.service'\nrequire(set(after['unitFilesActual'])==set(old_after['unitFilesActual'])and all(after['unitFilesActual'][k]==v for k,v in old_after['unitFilesActual'].items()if k!=unit_path))")
    raw=once(raw,"oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)","for stamp,phase,observed in phases:oracle['verify'](public_first,observed,phase,expected_epoch,lower,upper)\n"+UNIT_POST)
    return raw


UNIT_POST=r'''
old_unit=old_after['unitFilesActual'][unit_path];new_unit=after['unitFilesActual'][unit_path]
require(len(old_unit)==len(new_unit)==10 and old_unit[9]=='28e6e23ddcfeacac7dc1daf326a1a2b1bc91895bbd34b313fe89a1b04f499bd6')
require(new_unit[0]==old_unit[0]and new_unit[1]!=old_unit[1]and new_unit[2:7]==[0,0,stat.S_IFREG|0o644,1,1947]and new_unit[9]=='e9ce87045404893edede09b86dfb55523698ed26eeef3c4cb2b386f16518613b'and all(lower<=new_unit[i]<=upper for i in [7,8]))
held_old=publication/'morning-unit-old.private';s=held_old.lstat()
require(stat.S_ISREG(s.st_mode)and list(metadata9(s))[:8]==old_unit[:8]and lower<=s.st_ctime_ns<=upper and not os.listxattr(held_old))
require(hashlib.sha256(held_old.read_bytes()).hexdigest()==old_unit[9]and metadata9(held_old.lstat())==metadata9(s))
require(strict(pathlib.Path(unit_path),0o644,1947)==(pathlib.Path('/opt/schubert-nk/current')/'systemd/schubert-nk-morning-controller.service').read_bytes())
require(publication_private('daemon-reload-reserved.private')==b'one normal daemon-reload; no retry\n')
for ignored in range(2):
 config=command(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=Type,SuccessExitStatus'],4096)
 require(sorted(config.splitlines())==[b'SuccessExitStatus=10',b'Type=oneshot']and config.endswith(b'\n'))
require(not pathlib.Path('/etc/systemd/system/pg1877-morning-unit.part').exists())
'''


def payload():
    fixed=json.loads((W/'pg1879-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0:raise ValueError('actual seven-phase ABI required')
    raw=engine.payload(json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes()))
    raw=once(raw,'\nbus = dbus.SystemBus(private=True)\n','\n'+public_after()+'\nbus = dbus.SystemBus(private=True)\n')
    raw='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\n'+raw
    raw=raw.replace("'/opt/schubert-nk/releases/0.1.0-PG1638' and hashlib.sha256(manifest).hexdigest() == '195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'","'/opt/schubert-nk/releases/0.1.0-PG1846' and hashlib.sha256(manifest).hexdigest() == '"+BOM+"'")
    raw=raw.replace("data['source']['commit'] == '"+OLD+"'","data['source']['commit'] == '"+CANDIDATE+"'")
    raw=raw.replace("str(base / 'pg1638-manifest.sig')","str(base / 'pg1846-manifest.sig')")
    raw=raw.replace(engine.SLOT,SLOT).replace("'startsStopsReloadsSqlWrites0':True","'startsStopsSqlWrites0':True,'normalSingleReload':True,'regularUnitOldInodeVerified':True,'canonicalPublicationIndependentPost':True")
    compile(raw,'<independent full newcurrent Unit and unchanged oldWARNING>','exec')
    if check(raw,'<whole SSC283 independent post>'):raise ValueError('all actual post static globals required')
    return raw


def main():
    actual=json.loads((W/'pg1880-activate-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['currentApprovalEpochChanged']is not True or actual['candidateSource']!=CANDIDATE or subprocess.check_output(['git','status','--porcelain']):raise ValueError('actual sameSource clean publication required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload()
    (out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
