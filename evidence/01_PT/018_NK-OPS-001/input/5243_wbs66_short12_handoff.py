"""Reconfirm all short-term criterion IDs and bind current four-role handoff receipts."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
ADD = {
 'WBS-F02': ('PG39862','PG39870'),
 'WBS-F03': ('PG36628','PG39814','PG39864','PG39865','PG39888'),
 'WBS-P004-03': ('PG39700',),
 'WBS-P004-05': ('PG39868',),
 'WBS-P018-08': (),
 'WBS-C02': ('PG39616',),
 'WBS-P018-02': (),
 'WBS-P018-10': ('PG39850','PG39884'),
 'WBS-P004-02': (),
 'WBS-P018-07': (),
 'WBS-P019-02': (),
 'WBS-P020-01': ('PG39834',),
}
NEXT = {
 'WBS-F02':'現API/Web全型、StorageのSQLException依存3、未移管上位72・旧入口、同source全六と13要求・451',
 'WBS-F03':'保護Main4/Test32、Root11、六モジュールの型付き全域、Native監視のPMD適用未解決、全451',
 'WBS-P004-03':'現保持原本とowner、正規退役、実DB認可済SQLとcommit後条件、全451',
 'WBS-P004-05':'実DBとUTC・rollback/close後条件、JDBCトランザクションの保護型、全451',
 'WBS-P018-08':'現BOM/current runtime ownerを持つ全stream、session/CRC、正規停止後条件、終了依存',
 'WBS-C02':'現実行先で14設定の実効Unit・Inspector終了・owner・native postを照合',
 'WBS-P018-02':'現候補の正規署名、実配置のBOM、対象と拒否の受渡し・終了証拠',
 'WBS-P018-10':'実producerからsinkまでの証拠、残catalogと当source全scope、全451',
 'WBS-P004-02':'正規の現DB参照保護と終了依存、当sourceの全対象',
 'WBS-P018-07':'実Caddy/TLS、同じ親deadline・owner/generation、実API/Web連鎖と正規停止',
 'WBS-P019-02':'P018-02の四共通条件・元作業の終了判断。固有試験と追加費0',
 'WBS-P020-01':'資格host空き20GiBでの正常preflight、実NK CHR/DIF、各子と451',
}


def ref(file):
    return dict(path=str(file),sha256=sha256(file.read_bytes()).hexdigest())


def load(file):
    return json.loads(file.read_bytes())


def evidence(alias):
    [path]=E.glob(alias+'*/manifest.json')
    return path


def main():
    start_path=next(D.glob('525_WBS66*'))
    start=load(start_path)
    v=start['values']
    assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==v['source']
    prev=evidence('PG38578')
    d=load(prev)
    assert all(ref(Path(p['path']))==p for p in d['planSource'])
    assert all(ref(Path(p['path']))==p for p in v['oracleReferences'])
    assert d['targetItems']==12 and d['uniqueTargetItems']==11
    assert d['topFive']==5 and d['topFiveCriteria']==25 and d['directCriteria']==59
    assert d['individualFormalDelta']==0 and d['formalCount']==17 and d['shortPlanPp']==143.371
    rows=[]
    for original in d['items']:
        item=original['item']
        assert not original['allowedFormalClosing']
        assert original['criterionCount']==len(original['directCriterionIds'])
        supplement=[ref(evidence(n)) for n in ADD[item]]
        rows.append(dict(original,replacesPriorEvidence=False,currentLocalSupplements=supplement,
                         outstandingSpecificEvidence=NEXT[item]))
    origins=[evidence(x) for x in ('PG36620','PG36624','PG36628','PG39870','PG39888')]
    old=load(origins[0])
    raw=load(origins[1])
    print('originalSSC447 run keys:',sorted(old), 'raw keys:',sorted(raw))
    stages=old.get('stages')
    found=old.get('tests')
    assert old['actualExit']==0 and isinstance(found,int) and found==152
    assert all(old.get(k,0)==0 for k in ('failures','errors','skipped','notRun'))
    four=[
       dict(owner='F02',state='LOCAL_FOUR_MODULE_EVIDENCE',receipts=rows[0]['currentLocalSupplements'],missing=NEXT['WBS-F02']),
       dict(owner='F03',state='LOCAL_TYPED_ANALYSIS_EVIDENCE',receipts=rows[1]['currentLocalSupplements'],missing=NEXT['WBS-F03']),
       dict(owner='C02',state='ENVIRONMENT_BLOCKED',receipts=rows[5]['currentLocalSupplements'],missing=NEXT['WBS-C02']),
       dict(owner='F04',state='QA058_AUTHENTICATION_AND_OWNER_UNRESOLVED',receipts=[ref(next(D.glob('495_*')))],
            missing='harukaで対象scopeの現owner・認証・正規remote観測。前回の接続終了255で観測本体未開始'),
    ]
    gates=Path(v['oracleReferences'][3]['path'])
    assert load(gates)['result']['physical']==8 and load(gates)['result']['findings']==0
    pack=dict(actualExit=0,source=v['productionCoreMain'],head=v['source'],priorIndex=ref(prev),items=rows,
       shortTermTargets=12,shortTermDistinct=11,directCriteria=59,priorityFiveCriteria=25,priorityFiveAccepted=0,
       officialAccepted=17,officialAll=190,netIncrease=0,officialPt=1964,officialScope=53,
       requiredNet=10,requiredDistinctOfEleven=10,requiredAllFive=True,shortPricePp=143.371,effortPercent=None,
       handoffRoles=four,externalHandoffReceipt=None,deadlineJST=dict(d['deadlineJST'],fourHandoff='2026-11-25T23:29:00+09:00'),
       historicalSsc447=dict(success=152,failed=0,errors=0,skipped=0,notRun=0,
           source='e4794ddf45487268883334d0f8773d89bd47dcba',rawMiss=dict(L=4,M=4,C=0,B=58,I=85),
           references=list(map(ref,origins[:3])),appliedToCurrentSource=False),
       newTests=0,newAcceptance=0,formalUpdated=False,freshCurrentCoverageCalculated=False,
       terminalAtUTC=datetime.now(timezone.utc).isoformat(),verifier=ref(Path(__file__).resolve().relative_to(Path.cwd())))
    out=E/v['run']
    out.mkdir()
    (out/'manifest.json').write_text(json.dumps(pack,ensure_ascii=False,indent=2)+'\n')
    print(dict(items=len(pack['items']),formal=pack['officialAccepted'],criteria=pack['directCriteria'],hash=ref(out/'manifest.json')['sha256']))


if __name__ == '__main__':
    main()
