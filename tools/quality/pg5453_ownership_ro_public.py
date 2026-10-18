"""Allowlisted same-source actual RO acceptance; no replay/export of protected originals."""
import hashlib
import json
import os
from pathlib import Path
import pg5454_ownership_publication_sources as role


def main():
    result=role.qualify();paths={'host':'pg5448-frozen-v1.safe.json','stage':'pg5450-stage-v1.safe.json',
        'prepare-ro':'pg5450-prepare-ro-v1.safe.json','post':role.ro_post.SLOT+'/manifest.safe.json'}
    values={key:json.loads((role.W/path).read_bytes())for key,path in paths.items()}
    if any(type(v['actualExit'])is not int or v['actualExit']!=0 for v in values.values()):raise ValueError('all original actual int0 required')
    if len(values['host']['phases'])!=6 or any(v['actualExit']!=0 for v in values['host']['phases'].values()):raise ValueError('actual RO six host phases')
    for key in('stage','prepare-ro'):
        v=values[key]
        if v['action']!=key or v['candidateSource']!=role.SOURCE or v['installedSource']!=role.CURRENT or v['sourceQualified']is not True or v['currentApprovalEpochChanged']is not False or v['startsStopsReloadsSqlWrites0']is not True:
            raise ValueError('actual296/A2 readonly-only operation')
    flags=('candidateHostReadonlyVerified','native88Preserved','newTenReferencesReturnedNormally','all24TablesEqualTwice',
        'configuration32EveryFieldUnchanged','allUnitFileBytesMetadataUnchanged','originalBackupCredentialOldProofsPreserved','allClientAdvisoryMA0','runtimeStartupAndApprovalEpochUnchanged')
    value={'actualExit':0,'candidateSource':role.SOURCE,'currentSource':role.CURRENT,'BOM':role.BOM,
        'full11BeforeSha256':role.BEFORE,'originalSnapshotSha256':result['beforeSha256'],
        'receipts':{key:{'privatePath':path,'sha256':hashlib.sha256((role.W/path).read_bytes()).hexdigest(),'actualExit':0}for key,path in paths.items()},
        'hostPhases':values['host']['phases'],'postPayloadSha256':values['post']['payloadSha256'],'postObservedUTC':values['post']['observedUTC'],
        'stageStartedUTC':values['stage']['startedUTC'],'stageCompletedUTC':values['stage']['completedUTC'],
        'prepareStartedUTC':values['prepare-ro']['startedUTC'],'prepareCompletedUTC':values['prepare-ro']['completedUTC'],
        'verified':{key:result[key]for key in flags},'nativePhysicalFilesPreserved':88,'currentChanged':False,
        'candidateReadonlyOnly':True,'newSourceNativeQualified':False,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'rawSecretsExported':False}
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5450-ro296-v1'
    os.umask(0o077);out.mkdir(parents=True);path=out/'manifest.json'
    with path.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'candidateReadonlyOnly':True,'formalAccepted':False}))


if __name__=='__main__':main()
