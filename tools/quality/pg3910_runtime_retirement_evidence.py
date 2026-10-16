"""Publish only current exact retirement receipts and typed metadata, no raw snapshots."""
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg3902_current_runtime_retirement_sources import SOURCE,RUNTIME_SHA

ROOT=Path(__file__).resolve().parents[2]


def main():
    names=['pg3900-current-runtime-retirement-input-v1/manifest.safe.json','pg3904-frozen-v1.safe.json','pg3906-stage-v1.safe.json','pg3906-retire-v1.safe.json','pg3908-current-runtime-retirement-post-v1/manifest.safe.json']
    receipts=[]
    for name in names:
        raw=(W/name).read_bytes();value=json.loads(raw)
        if value.get('actualExit')!=0 or value.get('productionSource')!=SOURCE or any(k in value for k in ['rows','password','token','cookie','sessionId','payloadCiphertext']):raise ValueError('actual current metadata-only successful receipt required')
        receipts.append({**value,'originalReceipt':name,'originalReceiptSha256':hashlib.sha256(raw).hexdigest()})
    post=receipts[-1]
    if not(post['exactRuntimeEntryRetired']and post['all24UnchangedTwice']and post['allClientAdvisoryFlock0']and post['nativePhysicalFiles']==46 and post['ownedExplicitStops']==0):raise ValueError('independent exact current retirement and all postconditions required')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3910-runtime-retirement-v1';out.mkdir();files={}
    for i,value in enumerate(receipts,1):
        name=f'{i:03d}-receipt.json';raw=(json.dumps(value,sort_keys=True)+'\n').encode();(out/name).write_bytes(raw);files[name]=hashlib.sha256(raw).hexdigest()
    value={'source':SOURCE,'run':'PG3910-runtime-retirement-v1','testId':'PT-RUNTIME-RETIRE-3906/3908','actualExit':0,'targetName':'zz-pg3844-once-resume.conf','targetSha256':RUNTIME_SHA,'targetBytes':644,'actualNormalRetirement':True,'all24UnchangedTwice':True,'allTenKernelEmpty':True,'allActorsGone':True,'allClientAdvisoryFlock0':True,'native46Unchanged':True,'ordinaryStopsReissued':0,'RootStarts':0,'dbWrites':0,'newNativeCredit':0,'newProductionTests':0,'BUG':'BUG1327','YKT':'YKT1093','afterSnapshotKeys':11,'afterSha256':post['proofHashes']['after.private.json']['sha256'],'formalAccepted':False,'files':files}
    raw=(json.dumps(value,sort_keys=True)+'\n').encode();(out/'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'files':len(files),'manifestSha256':hashlib.sha256(raw).hexdigest(),'afterSha256':value['afterSha256'],'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
