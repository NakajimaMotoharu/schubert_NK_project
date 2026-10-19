"""Publish only successful capture predicates/hashes; no raw full11/DB/native session."""
import datetime
import hashlib
import json
import os
from pg5590_current_static_projection import ROOT,W
from pg5606_current_full_preservation import SLOT,SOURCE


def main():
    path=W/SLOT/'manifest.safe.json';raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='cdb5e245a218dab0e7e125e032f55ef227d044ada200dfe2c2f99c293fbb5ed5':raise ValueError('actual original successful v2 only')
    value=json.loads(raw);v=value['result']
    if not(value['actualExit']==v['actualExit']==0 and value['source']==v['productionSource']==SOURCE and v['sealedFull11Fields']==11 and v['nativePhysicalFiles']==94
      and v['all24EqualTwice']and v['allTenRefsReturnedNormally']and v['allClientAdvisoryFlock0']and v['allKernelActor0']and value['oldStopReissued']is False):raise ValueError('all original current before predicates, not a new stop claim')
    def timestamp(p):return datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()
    result={'actualExit':0,'source':SOURCE,'operatorSource':'bfbd4af2c','result':v,'originalManifestSha256':hashlib.sha256(raw).hexdigest(),'payloadSha256':value['payloadSha256'],
      'command':'PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pinned-pyflakes-runtime> python3 -B tools/quality/pg5606_current_full_preservation.py',
      'actualExecutionStartUTC':None,'actualExecutionEndUTC':None,'hostObservedPrivatePayloadMtimeUTC':timestamp(path.with_name('payload.private.py')),
      'hostObservedTerminalManifestMtimeUTC':timestamp(path),'timingNote':'Original wrapper did not save process start/end timestamps. File mtimes are observation bounds, not claimed execution times.',
      'failedV1Preserved':True,'full11OrDatabaseBytesPublished':False,'oldNativeAcceptanceImported':False,'vmStartStopReloadActions':0,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5607-current-preservation-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'full11Sha256':v['privateBeforeSha256'],'nativePhysicalFiles':94,'sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
