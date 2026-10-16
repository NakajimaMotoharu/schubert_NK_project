"""Publish same-source original completion and independent post, never raw guest data."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]


def main():
    original=W/'pg4200-metadata-continuation-v1-recover/manifest.safe.json'
    raw=original.read_bytes();value=json.loads(raw);r=value['result']
    if value['actualExit']!=0 or value['payloadSha256']!='545bb84f5c6d58b9305ac4499a0f8afa916e2baee7dcba3c61547e1d30727cdb':raise ValueError('original exact final source result required')
    if r['businessStopsIssued']!=5 or r['caddyStopsReissued']!=0 or r['old4152TransportExit']!=255 or r['old4152Normal']is not False or r['newTenRefsNormalClose']is not True:raise ValueError('qualified partial recovery contract required')
    post=r['independentPost'];recover=r['partialRecover']
    if post['newMARDDBTenRefNormalClose']is not True or post['independentFailedDoneRecoveryPost']is not True or post['beforeSha256']!=post['afterSha256']or recover['canonicalEpochRevoked']is not True:raise ValueError('actual independent final post and new normal scope required')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4206-actual-partial-recovery-v1';out.mkdir()
    safe=out/'original-result.json';safe.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    manifest={'source':value['source'],'actualExit':0,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'originalManifestSha256':hashlib.sha256(raw).hexdigest(),'files':{safe.name:hashlib.sha256(safe.read_bytes()).hexdigest()},
              'environment':{'hostOS':platform.system()+' '+platform.release(),'hostPython':platform.python_version(),'JDK':'25.0.4','Maven':'3.9.12','guestBoot':r['boot']},
              'command':'python3 -B tools/quality/pg4200_metadata_continuation.py recover','operatorBranch':'dev-foundation',
              'operatorCommit':'d024419c6','productionPtAdded':0,'formalAccepted':False,'oldRoot143Normal':False,
              'nativeCRCSessionQualificationPending':True,'designMain':'e58ce46ac4117caa956583634b40db06d95112c9'}
    p=out/'manifest.json';p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'originalManifestSha256':manifest['originalManifestSha256'],'allNewScopesNormal':True,'oldRootNormal':False}));return 0


if __name__=='__main__':raise SystemExit(main())
