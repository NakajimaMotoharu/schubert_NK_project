"""Publish only whitelisted non-secret deployment receipts, never raw private logs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
T = R.parents[3]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
D = T/'evidence/01_PT/018_NK-OPS-001/evidence/PG685-687-current-public-v1'


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=T)
    assert not D.exists()
    names = ('pg685-frozen-v4.safe.json','pg685-stage-v1.safe.json',
             'pg686-candidate-stage-v1.safe.json','pg685-verify-v1.safe.json',
             'pg685-activate-v1.safe.json','pg687-activate-post-v1.safe.json')
    values = {}
    for name in names:
        raw=(W/name).read_bytes();obj=json.loads(raw);assert obj['actualExit']==0
        allowed=('run','actualExit','source','operatorSource','candidateSource','manifestSha256',
                 'startedUTC','completedUTC','endedUTC','elapsedSeconds','privateLogSha256',
                 'currentUnchanged','candidateOnly','activationNotRun','oldUnknownNormalized',
                 'graphCases','cliConditions','oldV2ClassBytesIdentical','productionPTCredit',
                 'guestActions','formalAccepted','frozenToolSource')
        safe={k:obj[k]for k in allowed if k in obj}
        if 'proof'in obj:
            proof=obj['proof'];assert proof['fields']==21 and proof['batchRows']==514
            safe['proof']={k:proof[k]for k in ('mode','beforeSha256','afterSha256','completeSha256',
                         'fields','full24Twice','batchRows','tenUnitsKernel0','whole187Signature',
                         'resources0','allNewMetadataNormal','formalAccepted','startsStopsWrites0')}
        safe['privateReceiptSha256']=hashlib.sha256(raw).hexdigest();values[name]=safe
    D.mkdir()
    files={}
    for name,value in values.items():
        content=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
        with(D/name).open('xb')as f:f.write(content)
        files[name]=hashlib.sha256(content).hexdigest()
    manifest={'run':'PG685-687-current-public-v1','productionSource':'9bd50536f692610036a0ed8b83e0a8b35fe2a66f',
              'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
              'testIds':['FREEZE685001','PT-OPS-CODE685001','PT-OPS-CODE685002','PT-OPS-CODE685003','STAGE686001','STAGE686002','POST687001','POST687002'],
              'specifications':['555','556','557'],'files':files,'sanitization':'WHITELIST_ONLY_NO_RAW_SESSIONS_CREDENTIALS_DATABASE_BACKUPS',
              'formalAccepted':False,'sameSourceParentNativeAccepted':False,'pgptComplete':False}
    with(D/'manifest.json').open('x')as f:json.dump(manifest,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'receipts':len(files),'manifestSha256':hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
