"""Bind current short-term evidence to the exact approved WBS and leave unmet gates open."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import csv, json, subprocess


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def table(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter="\t"))


pmo=Path("documents/400_PGPT/470_PMO")
records=next(pmo.glob("601_*"))
entry=read(next(records.glob("1256_*")))
core=entry["values"]["productionCoreMain"]
pmowork=Path("../PMO/hourly-monitor")
plan=next((pmowork/"wbs66-20261116").glob("58_*"))
evaluation=pmowork/"更新判断-20261207/更新判定基準.json"
original=plan/"922条件の受入照合.tsv"
parents=plan/"190元項目から条件と終端判断を引く.tsv"
ids=[x["id"] for x in read(evaluation)["targets"]]
details=table(original)
hierarchy=table(parents)
assert len(details)==922 and len(hierarchy)==190 and len(ids)==len(set(ids))==12
ops=Path("evidence/01_PT/018_NK-OPS-001/evidence")

review={
    "F02": ((40840,40844,40820), "現Batch新組立、三ライブラリは入力同一参照、六宣言", "API／Web実buildと許可範囲内の型付き全六（QA-056）、SSC-461旧Storage JDBC一辺、実runtime。"),
    "F03": ((40818,40830,40838,40848), "Main 1027・Test 1119/1151、局所型付きと既三の適用、snapshot raw差", "保留32 Test、API/Web・Batch保留、Root11と当候補の全六、raw生成部のレビューと451。"),
    "P004-03": ((40582,40270), "局所3/5、旧借用DAO証拠", "DurableRecordFiles／MaintenanceRunFilesの承認済み実所有と終端・原本保全、実DAOの認証とDB後条件。"),
    "P004-05": ((40580,40608,40842), "二所有型、UTC既driver、新Summary13の共有", "実PostgreSQL role・pool・commit／rollback・資源、JdbcSyncRequestProcessorの実監査後条件。"),
    "P018-08": ((40260,40268,40842), "独立decoder/物理照合の合成、局所Java実測", "実native stream、CRC/session、真正owner・終端、正常／異常／停止の全三子。"),
    "P018-02": ((40430,), "五所有の局所値・形式", "当sourceの署名付きrelease/BOMと現hostのbyte、公開・権限・保持の独立post。"),
    "P018-10": ((40684,40826), "合成のREQUEST Details新2、旧純値・固定診断", "全入口・三子の独立出力、実sink・実NSS、当releaseの未漏洩証拠。"),
    "P004-02": ((40838,40842,40844), "Summary実13、raw四100、型付き、ABI差0", "実Inbox参照保護、該当型・DB role/TX・実後条件。"),
    "P018-07": ((40612,40616), "公開Caddy設定と分離した純値6", "Caddy20のRoot型依存、承認済み同parent/Unit、TLS・readiness・deadline・終端。"),
    "P019-02": ((40430,), "P018-02共有・追加費0", "配布manifest/署名判断とP018-02成立。固有最低件数には算入しない。"),
    "C02": ((40184,40846), "14公開設定と旧Unit timeoutの証拠", "同boot/Invocationの実効Unit/所有/真正始終端、Web→Caddy・Inspectorと停止後条件。"),
    "P020-01": ((40706,40708), "既比較器211と独立raw", "真正Current/NK実adapter、Browser、DIF/QA051 final・全三子とG01～G06。"),
}
assert set(ids)==review.keys()
criterion_rows=[]
for item in ids:
    canonical="WBS-"+item
    items=[r["判定ID"] for r in details if r["元項目"]==canonical]
    parent,= (r for r in hierarchy if r["元項目"]==canonical)
    assert parent["開始状態"]=="NOT_ACCEPTED" and int(parent["固有条件数"])==len(items)==len(set(items))
    assert bool(items)==(item!="P019-02")
    proof_ids,now,needed=review[item]
    proof_files={}
    for number in proof_ids:
        suffix="*-v2" if number in (40826,40820) else "*"
        proof,=ops.glob(f"PG{number}-{suffix}/manifest.json")
        proof_files[number]=pin(proof)
    criterion_rows.append(dict(id=item,original=canonical,countsTowardUniqueGoal=item!="P019-02",
        requiredCriteria=items,originalParent=parent,provisionalEvidence=now,remainingFirstEvidence=needed,
        proofFiles=proof_files,status="NOT_ACCEPTED",commonReleaseAnd451StillRequired=True))
assert sum(len(row["requiredCriteria"]) for row in criterion_rows)==59
snapshot=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
assert snapshot==subprocess.check_output(["git","rev-parse","origin/dev-foundation"],text=True).strip()
out=ops/entry["values"]["run"]/"manifest.json"
out.parent.mkdir()
out.write_text(json.dumps(dict(actualExit=0,core=core,snapshot=snapshot,startEvent=entry["eventId"],
    approvedRules=pin(evaluation),originalCriteria=pin(original),originalParents=pin(parents),previousProof=pin(next(records.glob("996_*"))),
    rows=criterion_rows,uniqueCriteria=59,preparationValidationCorrections=1,
    coreAccepted=0,shortAccepted=0,originalAccepted=17,formalDelta=0,effortRate=None,authorizedRuntimeOperations=0,
    newProductTests=0,whole451=False,terminalAtUTC=datetime.now(timezone.utc).isoformat()),ensure_ascii=False,indent=2)+"\n")
print(pin(out),sum(len(r["requiredCriteria"]) for r in criterion_rows))
