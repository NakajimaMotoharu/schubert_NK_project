"""Allowlisted genuine finite publication result; no raw protected values or new Root claim."""
import hashlib
import json
import os
from pathlib import Path
import pg5460_ownership_publication_post as post


def main():
    w=post.role.W;paths={'host':'pg5456-frozen-v1.safe.json','stage':'pg5458-stage-v1.safe.json',
        'activate':'pg5458-activate-v1.safe.json','post':post.SLOT+'/manifest.safe.json'}
    values={key:json.loads((w/path).read_bytes())for key,path in paths.items()}
    if any(type(v['actualExit'])is not int or v['actualExit']!=0 for v in values.values()):raise ValueError('every true original numeric0')
    host=values['host'];outer=values['post'];r=outer['result']
    if len(host['phases'])!=7 or any(v['actualExit']!=0 for v in host['phases'].values()):raise ValueError('actual all seven host phases')
    if outer['source']!=post.role.SOURCE or r['productionSource']!=post.role.SOURCE or r['candidateManifestSha256']!=post.role.BOM or outer['payloadSha256']!=hashlib.sha256(post.payload().encode()).hexdigest():
        raise ValueError('same296 independent actual post')
    flags=('sevenFinitePhasesVerified','all24And32Unchanged','whole187SignedArtifactBytesVerified','allTenKernelEmpty',
        'allClientAdvisoryFlock0','originalBackupNative88Preserved','canonicalInvalidEpochApprovalCurrentAndOldLinkVerified',
        'unitBytesInodesConfigurationUnchanged','newTenReferencesReturnedNormally','newSourceParentNotStarted','oldNativeNotAppliedToNewSource')
    if any(r.get(k)is not True for k in flags):raise ValueError('all actual limited finite conditions')
    value={'actualExit':0,'productionSource':post.role.SOURCE,'priorSource':post.role.CURRENT,'BOM':post.role.BOM,
        'full11BeforeSha256':post.FULL_SHA,'full11AfterSha256':r['postSha256'],'postPayloadSha256':outer['payloadSha256'],
        'receipts':{key:{'privatePath':path,'sha256':hashlib.sha256((w/path).read_bytes()).hexdigest(),'actualExit':0}for key,path in paths.items()},
        'hostPhases':host['phases'],'stageStartedUTC':values['stage']['startedUTC'],'stageCompletedUTC':values['stage']['completedUTC'],
        'activateStartedUTC':values['activate']['startedUTC'],'activateCompletedUTC':values['activate']['completedUTC'],
        'postObservedUTC':outer['observedUTC'],'verified':{k:r[k]for k in flags},'nativePhysicalFilesPreserved':88,
        'currentChanged':True,'unitExchangeAndReload':False,'newSourceNativeQualified':False,'F03Accepted':False,
        'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'rawSecretsExported':False}
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5458-finite296-v1'
    os.umask(0o077);out.mkdir(parents=True);path=out/'manifest.json'
    with path.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'newRootNotStarted':True,'formalAccepted':False}))


if __name__=='__main__':main()
