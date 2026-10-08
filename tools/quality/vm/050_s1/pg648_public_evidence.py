"""Publish only existing safe receipts; no private archive/log/raw data."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG646-649-public-v1'
    target.mkdir(mode=0o755)
    names=('pg646-completed-baseline-v1.safe.json','pg647-build-v1.safe.json','pg647-stage-v1.safe.json',
           'pg647-retire-v1.safe.json','pg648-retirement-post-v1.safe.json','pg649-backup-preserve-v1.safe.json')
    files={}
    for name in names:
        raw=(W/name).read_bytes();j=json.loads(raw)
        if name=='pg647-build-v1.safe.json':assert j['compileExit']==j['cliExit']==0
        else:assert j['actualExit']==0
        with(target/name).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        files[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    result={'run':'PG646-649-public-v1','atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
            'productionSource':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5',
            'tests':['PG647-C001..004','PG647-O001..005','PG647-J001','PG647-R001','PG648-C001..003','PG648-R001','PG649-C001','PG649-R001'],
            'specs':['527_PG647_完了runtime635正規退役.md','528_PG648_正規退役独立後条件.md','529_PG649_八Backup私有保全.md'],
            'bugs':['BUG-906','BUG-907'],'ykt':['YKT-675','YKT-676'],'files':files,
            'stageLabelCorrection':'Original pg647-stage-v1.safe.json run=PG635-stage-v1 is preserved unchanged; actual PG647 immutable new directory/operator/hash; BUG907/527 correct identity. No restaging.',
            'rawExported':False,'privateArchivesExported':False,'formalAccepted':False,'coverage100':False}
    with(target/'manifest.json').open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'safeReceipts':len(files),'rawExported':False,'formalAccepted':False}))


if __name__=='__main__':main()
