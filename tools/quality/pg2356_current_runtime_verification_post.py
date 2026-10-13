"""Independent post for actual e392 verification; never replay or rewrite its receipt."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,SSH
import pg2348_current_reloaded_recovery_post as prior

SLOT='pg2356-current-runtime-verification-post-v1'
SOURCE=prior.SOURCE

NORMAL=r'''
normal=base/'pg2354-current-runtime-verification-v1'
receipt=(normal/'complete.private').read_bytes()
require(receipt==b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\nfreshResumeRuntimePrepared=true\nnormalSingleRuntimeReload=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsEpochSqlWrites0=true\noldUnknownNormalized=false\n')
before_raw=(normal/'before.private.json').read_bytes()
after_raw=(normal/'after.private.json').read_bytes()
normal_before=json.loads(before_raw);normal_after=json.loads(after_raw)
require(normal_before==normal_after)
reference=json.loads((base/'pg2348-current-reloaded-recovery-post-v1/after.private.json').read_bytes())['before']
require(normal_before==reference)
require(normal_after['configuration']==current_view)
require(normal_after['runtime']==expected_runtime)
for key in ['rows','units','startup','originals','backup','extraDurable','unitFilesActual']:
 require(normal_after[key]==after[key])
require(native==tree(pathlib.Path('/run/schubert-nk/pt-coverage')))
'''


def payload():
    raw=prior.body().replace('PEER_CLOSED=False','PEER_CLOSED=True')
    tail=prior.TAIL
    marker="save=base/'pg2348-current-reloaded-recovery-post-v1'"
    if tail.count(marker)!=1:raise ValueError('one independent post publication boundary')
    tail=tail.replace(marker,NORMAL+"\nsave=base/"+repr(SLOT))
    tail=tail.replace("'verificationOnlyNormalScopePending':True","'verificationOnlyNormalScopePending':False,'verificationOnlyNormalScopeConfirmed':True,'thisScopeReloadIssued':False,'historicalReceiptFlagsBug1237':True")
    tail=tail.replace("'oldCloseUnknown':True}","'oldCloseUnknown':True}")
    raw+=tail
    if check(raw,'<independent current verification post>'):raise ValueError('all independent post globals required')
    compile(raw,'<independent current verification post>','exec');return raw


def main():
    entry=json.loads((W/'pg2352-verify-runtime-v1.safe.json').read_bytes())
    if not(entry['actualExit']==0 and entry['sourceQualified'] and entry['verificationOnlyNormalScope'] and not entry['normalSingleRuntimeReload'] and entry['operatorSource']=='e39202411d5622c4522c3c40ae30a036eb5fb846'):raise ValueError('fixed actual normal verification required')
    log=W/'pg2352-verify-runtime-v1.private.log'
    if hashlib.sha256(log.read_bytes()).hexdigest()!=entry['privateLogSha256']:raise ValueError('fixed actual log required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'verificationEntrySha256':hashlib.sha256(json.dumps(entry,sort_keys=True).encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
