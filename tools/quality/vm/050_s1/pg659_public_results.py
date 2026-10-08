"""Safe current campaign receipts only; no private exec/archive/log/DB export."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    os.umask(0o077)
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG652-658-public-v1'
    target.mkdir(mode=0o755)
    names={'pg652.safe.json':'pg652-retention-post-v2.safe.json','pg653.safe.json':'pg653-completed-readonly-v1.safe.json',
           'pg654.safe.json':'pg654-chr-a01-native-v1.safe.json','pg655-build.safe.json':'pg655-native-build-v1.safe.json',
           'pg655-stop.safe.json':'pg655-native-stop-v1.safe.json','pg656.safe.json':'pg656-terminal-final-v1.safe.json',
           'pg657.safe.json':'pg657-normal-eight-native-v1/manifest.safe.json','pg658.safe.json':'pg658-same-source-sixteen-native-v1/manifest.safe.json'}
    hashes={}
    for name,source in names.items():
        raw=(W/source).read_bytes();v=json.loads(raw)
        if name=='pg655-build.safe.json':assert v['actualCompileExit']==v['argumentExit']==0
        else:assert v['actualExit']==0
        with(target/name).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        hashes[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    metadata={'run':'PG652-658-public-v1','atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
              'productionSource':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5','branch':'dev-foundation',
              'os':'Ubuntu26.04 guest/Linux host','jdk':'25.0.4','javaCompile':'-Xlint:all -Werror',
              'tools':{'jacoco':'0.8.15','asm':'9.10.1','postgresql':'18.6','artemis':'2.56.0','pyflakes':'3.4.0'},
              'specs':['531_PG652_通常保持期限全列独立検査.md','532_PG653_654_新普通親真正DONE・実A01.md','533_PG655_新通常cohort所有停止.md','534_PG656_新通常所有停止後条件.md','535_PG657_通常親八freshnative品質計測.md','536_PG658_同source二cohort品質合算.md'],
              'testIds':['PG652-C001..003','PG652-R001','PG653-C001','PG653-R001','PG654-C001','PG654-R001','PG655-C001..002','PG655-R001','PG656-C001','PG656-R001','PG657-C001','PG657-R001','PG658-C001','PG658-R001'],
              'bugs':['BUG-897','BUG-908','BUG-909','BUG-910'],'ykt':['YKT-666','YKT-677','YKT-678','YKT-679'],
              'files':hashes,'rawExported':False,'privateArchivesAndExecutionDataExported':False,'formalAccepted':False,'coverage100':False}
    with(target/'manifest.json').open('x')as f:json.dump(metadata,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    report=T/'program/characterization/reports/nk/PG654-native-a01-v1'
    artifact=report/'artifacts/CHR-A01.json';raw=artifact.read_bytes();v=json.loads(raw)
    assert v['caseId']=='CHR-A01'and v['status']=='PASS'and v['csrf']=='<TOKEN>'and v['passwordValue']==''
    with(report/'manifest.json').open('x')as f:json.dump({'source':metadata['productionSource'],'run':'PG654-native-a01-v1','artifactSha256':hashlib.sha256(raw).hexdigest(),'receiptRef':'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG652-658-public-v1/pg654.safe.json','rawCookieTokenExported':False,'approvedDIF001':True,'formalAccepted':False},f,sort_keys=True);f.write('\n')
    print(json.dumps({'safeReceipts':len(hashes),'rawExported':False,'formalAccepted':False}))


if __name__=='__main__':main()
