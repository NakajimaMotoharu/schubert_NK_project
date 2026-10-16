"""Safe pre-stop immutability qualification; no operation/Root acceptance claims."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg4260_stable_admission_image import SOURCE


def main():
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4298-immutable-pre-stop-v1';out.mkdir();files={}
    for name in ['manifest.safe.json','host-tests.log']:
        p=out/name;p.write_bytes((W/'pg4296-immutable-owned-qualification-v1'/name).read_bytes());files[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    value={'source':SOURCE,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'BUG':'BUG1348','YKT':'YKT1114',
           'actualABICompiled':False,'actualConsumerVerified':False,'formalAccepted':False,'productionPtAdded':0,'rootActions':0}
    p=out/'manifest.json';p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
