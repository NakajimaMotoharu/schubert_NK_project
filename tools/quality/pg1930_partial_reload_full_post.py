"""Separate full new-owner reload result; original partial failure remains immutable."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1899_partial_publication_snapshot import payload as partial
from pg1877_warning_publication_sources import once

SLOT='pg1930-partial-reload-full-post-v1'


def payload():
    fixed=json.loads((W/'pg1926-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['sourceQualified']is not True:raise ValueError('actual sameSource full reload ABI required')
    raw=partial().replace('pg1896-complete-publication-full-post-v1',SLOT)
    raw=once(raw,"[b'SuccessExitStatus=',b'Type=oneshot']","[b'SuccessExitStatus=10',b'Type=oneshot']")
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one independent new owner result boundary required')
    raw=raw.replace(marker,EXTRA+'\n'+marker)
    raw='RELOAD_FILES='+repr(fixed['fileHashes'])+'\n'+raw
    raw=raw.replace("'normalSingleReload':True","'normalSingleReload':True,'existingUnitNoReexchange':True,'oldPartialFailurePreserved':True,'allNewReloadScopesReturnedNormally':True")
    compile(raw,'<independent partial old state and new normal reload>','exec')
    if check(raw,'<whole actual reload fullpost>'):raise ValueError('all actual post globals required')
    return raw


EXTRA=r'''
reload_save=base/'pg1929-partial-reload-v1';reload_tool=base/'pg1925-partial-reload-tools-v1'
def reload_private(name):
 p=reload_save/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
require(reload_private('complete.private')==b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\npartialExistingUnitVerified=true\nnormalSingleReload=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsEpochSqlWrites0=true\noldUnknownNormalized=false\n')
require(reload_private('daemon-reload-reserved.private')==b'one normal daemon-reload; no retry\n')
require(hashlib.sha256(reload_private('before.private.json')).hexdigest()=='16ec6b95e9de832eec5eaf90849a64e6a54c94600b3b6f3f7a09527b17515ad4')
require(json.loads(reload_private('after.private.json'))==after)
require(reload_private('refs-prepare.private.log')==b'')
gap=reload_private('observations.private').decode('ascii');require(re.fullmatch(r'maxGapNanos=[0-9]+\n',gap)is not None and int(gap.split('=')[1])<30000000000)
for name,digest in RELOAD_FILES.items():
 p=reload_tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((reload_tool/'payload-sha256.json').read_bytes())==RELOAD_FILES)
'''


def main():
    actual=json.loads((W/'pg1927-finish-reload-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['normalSingleReload']is not True or actual['currentApprovalEpochChanged']is not False or subprocess.check_output(['git','status','--porcelain']):raise ValueError('actual clean new owner single reload required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
