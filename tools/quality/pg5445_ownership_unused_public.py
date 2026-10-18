"""Allowlisted true unused results, original receipt hashes; never export raw DB/log/key/native."""
import hashlib
import json
import os
from pathlib import Path
import pg5444_ownership_unused_post as post

W=post.role.W
ROOT=Path(__file__).resolve().parents[2]


def main():
    paths={'host':'pg5440-frozen-v1.safe.json','stage':'pg5442-stage-v1.safe.json',
        'place':'pg5442-place-v1.safe.json','post':post.SLOT+'/manifest.safe.json'}
    receipts={key:json.loads((W/path).read_bytes())for key,path in paths.items()}
    if any(type(v['actualExit'])is not int or v['actualExit']!=0 for v in receipts.values()):raise ValueError('every original actual terminal int0')
    post.qualify_placement(receipts['place']);host=receipts['host'];outer=receipts['post'];r=outer['result']
    if len(host['phases'])!=6 or any(type(v['actualExit'])is not int or v['actualExit']!=0 for v in host['phases'].values()):raise ValueError('all original six host phases')
    if outer['payloadSha256']!=hashlib.sha256(post.payload().encode()).hexdigest()or r['candidateSource']!=post.role.SOURCE or r['currentSource']!=post.role.CURRENT:
        raise ValueError('exact independently executed post and two separate sources')
    flags=('candidate187SignatureVerified','current187SignatureVerified','all24TablesEqualTwice','allTenKernelJob0',
        'configuration32EveryFieldUnchanged','allUnitFileBytesMetadataUnchanged','originalBackupCredentialOldProofsPreserved',
        'native88Preserved','runtimeStartupAndApprovalEpochUnchanged','allClientAdvisoryMA0','candidateUnusedOnly',
        'noSignalsOrStartsOrReloads','newTenReferencesReturnedNormally')
    if any(r.get(k)is not True for k in flags)or r['candidateNativeCredit']is not False:raise ValueError('all actual limited post conditions')
    value={'actualExit':0,'candidateSource':post.role.SOURCE,'currentSource':post.role.CURRENT,
        'candidateBOM':post.role.candidate_bom(),'full11BeforeSha256':r['full11BeforeSha256'],
        'snapshotSha256':r['beforeSha256'],'postPayloadSha256':outer['payloadSha256'],
        'receipts':{key:{'privatePath':path,'sha256':hashlib.sha256((W/path).read_bytes()).hexdigest(),'actualExit':0}for key,path in paths.items()},
        'hostPhases':host['phases'],'stageStartedUTC':receipts['stage']['startedUTC'],'stageCompletedUTC':receipts['stage']['completedUTC'],
        'placeStartedUTC':receipts['place']['startedUTC'],'placeCompletedUTC':receipts['place']['completedUTC'],
        'postObservedUTC':outer['observedUTC'],'verified':{k:r[k]for k in flags},'nativePhysicalFilesPreserved':r['nativePhysicalFiles'],
        'actualNewGuestOperations':['unused stage','unused place','independent post'],'currentChanged':False,
        'newSourceNativeQualified':False,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,
        'rawSecretsExported':False,'toolRuntime':'Python3; Java25.0.4 currentA2 ABI; pinned source-bound originals',
        'osContext':'Linux dedicated existing PGPT guest; same observed boot; no reboot'}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5442-unused296-v1';os.umask(0o077);out.mkdir(parents=True)
    path=out/'manifest.json'
    with path.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'formalAccepted':False,'candidateUnusedOnly':True}))


if __name__=='__main__':main()
