"""Publish only safe receipts; never private phase trees, DB rows, native, keys or credentials."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg3788_hygiene_publication_sources import SOURCE,BOM

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3796-hygiene-finite-publication-v1'
CASES=[('PT-HYGIENE-POST-3778','pg3778-hygiene-unused-held-post-v1/manifest.safe.json'),('PT-HYGIENE-RO-ABI-3782','pg3782-frozen-v1.safe.json'),('PT-HYGIENE-RO-3784','pg3784-prepare-ro-v1.safe.json'),('PT-HYGIENE-RO-POST-3786','pg3786-hygiene-ro-independent-post-v1/manifest.safe.json'),('PT-HYGIENE-PUBLICATION-ABI-3790','pg3790-frozen-v1.safe.json'),('PT-HYGIENE-PUBLICATION-3792','pg3792-activate-v1.safe.json'),('PT-HYGIENE-PUBLICATION-POST-3794','pg3794-hygiene-publication-independent-post-v1/manifest.safe.json')]


def sanitize(value):
    allowed={'actualExit','operatorSource','productionSource','currentSource','candidateSource','installedSource','candidateManifestSha256','genuineParentBeforeSha256','startedUTC','completedUTC','startUTC','endUTC','observedUTC','payloadSha256','privateLogSha256','sourceQualified','formalAccepted','guestMutations0','currentApprovalEpochChanged','finiteCodeOnlyPublication','oldFailedNormalized','candidateHostReadonlyOnly','startsStopsReloadsSqlWrites0'}
    result={k:v for k,v in value.items()if k in allowed}
    if 'result'in value:
        if any(not isinstance(v,(str,int,float,bool,type(None)))for v in value['result'].values()):raise ValueError('safe scalar-only guest receipt required')
        result['result']=value['result']
    if 'phases'in value:result['phases']=value['phases']
    if 'fileHashes'in value:result['frozenFileCount']=len(value['fileHashes'])
    return result


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed publisher required')
    prepared=[]
    for test,path in CASES:
        raw=(W/path).read_bytes();value=json.loads(raw)
        if type(value.get('actualExit'))is not int or value['actualExit']!=0 or value.get('candidateSource')!=SOURCE:raise ValueError('genuine same-source original0 receipt required')
        safe=sanitize(value);safe.update(testId=test,originalReceiptSha256=hashlib.sha256(raw).hexdigest(),originalReceipt=path)
        prepared.append((test,safe))
    os.umask(0o077);OUT.mkdir(mode=0o700)
    files=[]
    for index,(test,value)in enumerate(prepared,1):
        p=OUT/(f'{index:03d}-receipt.json');raw=(json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n').encode()
        with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        files.append({'path':p.name,'testId':test,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    manifest={'run':'PG3796-hygiene-finite-publication-v1','publishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':SOURCE,'BOM':BOM,'files':files,'formalAccepted':False,'formalReference':'PT-WEB-20260925-24/1964PT/53scope','individualAccepted':17,'individualScope':190,'wholeEffortCompletionRate':None,'oldNativeAppliedToNewSource':False,'newSourceOrdinaryResultIncluded':False,'rawPrivateDataExported':False,'BUG':['1322','1323','1324','1325'],'YKT':['1088','1089','1090','1091']}
    raw=(json.dumps(manifest,sort_keys=True,ensure_ascii=False)+'\n').encode()
    with(OUT/'manifest.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    print(json.dumps({'files':len(files),'manifestSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
