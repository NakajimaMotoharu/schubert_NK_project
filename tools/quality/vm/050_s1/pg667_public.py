"""Current existing ADMIN safe receipts only; never private credential, raw or exec."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent;T=R.parents[3];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    os.umask(0o077);target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG661-666-public-v1';target.mkdir(mode=0o755)
    files={};names=('pg661-completed-baseline-v1','pg663-handoff-preflight-v1','pg663-handoff-execute-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-execute-v1','pg665-bootstrap-final-v3')
    for name in names:
        raw=(W/(name+'.safe.json')).read_bytes();assert json.loads(raw)['actualExit']==0
        with(target/(name+'.safe.json')).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        files[name+'.safe.json']={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    raw=(W/'pg666-current-seventeen-native-v1/manifest.safe.json').read_bytes();assert json.loads(raw)['actualExit']==0
    with(target/'pg666.safe.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    files['pg666.safe.json']={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    metadata={'run':'PG661-666-public-v1','atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'productionSource':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5','branch':'dev-foundation','os':'Ubuntu26.04 guest/Linux host','jdk':'25.0.4',
              'tools':{'jacoco':'0.8.15','asm':'9.10.1','postgresql':'18.6','pyflakes':'3.4.0'},'specs':['538_PG661_当sourceBootstrap前全20原値.md','539_PG662_当source既存ADMIN正規起動仕様.md','540_PG663_参照子import前固定Java回収仕様.md','541_PG664_推移import是正と既存ADMIN新試験枠.md','542_PG665_当既存ADMIN独立全20後条件.md','543_PG666_当Bootstrap単sessionと資格17合算.md'],
              'testIds':['BOOT662001..004','PG663-C001..003','BOOT664001..004','BOOT665001..002','BOOT666001..002'],'bugs':['BUG-911'],'ykt':['YKT-680'],'ssc':['SSC-231','SSC-232'],
              'historicalFailure':{'run':'PG662-verify-v1','operatorSource':'152c262f1','referenceExit':1,'transportJavaExit':143,'hostCollectorExit':1,'hostCollectorPostSourceGuard':True,'normalClose':'UNKNOWN','errorOnlySha256':'c1935ed537f31f678be275164c100acc7db979986bf47cd0688d0ec363b0d761','normalizedAsSuccess':False},
              'files':files,'rawExported':False,'credentialAndPrivateExecutionDataExported':False,'formalAccepted':False,'coverage100':False}
    with(target/'manifest.json').open('x')as f:json.dump(metadata,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'safeReceipts':len(files),'rawExported':False,'formalAccepted':False}))


if __name__=='__main__':main()
