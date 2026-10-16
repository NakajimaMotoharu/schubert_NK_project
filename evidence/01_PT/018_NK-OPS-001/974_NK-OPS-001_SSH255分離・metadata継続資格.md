# NK-OPS-001 SSH255分離・metadata継続の操作前独立資格

2026-10-16、Production7bb/PG3976/boot79a。SS343/353 SSC289、QA047、BUG1343/YKT1109。旧4152/4188/4200を別runとして保持する。

| Test ID | 入力・事前条件・独立期待値 | 実結果 |
|---|---|---|
| PT-SSC289-ORIGINAL | 元4152 observer70976の終了値を回収、guest二pidfd terminal/消失と区別 | actual255、stderr0、旧normal false。4188は143固定guardでactual1、残5stop/inspect/post未発行 |
| PT-SSC289-READ | 4196 read、全旧PID/lock消失・全24/原本/Backup/keys/native50/startup33/普通3actor/Caddy既終端不変 | actual0、privateSHA6758d930bc6fb6b295274a05d4b58aba7b535909af8f263afe05f0ff43eecef6。残metadata791348/全5FD二読/子0・単task、新管理操作0 |
| PT-SSC289-TRANSPORT | literal source/hash/255/failure falseと別guest terminal evidence。0/143/bool/null/欠落/消失不成立を変異 | 全拒否、純1成功。255を正常/guest143へ変換0 |
| PT-SSC289-IDENTITY | literal791348/t14602179/argv/権限/cgroup/5FDと全metadata/各fdinfo/余剰・欠落変異 | 同一profileだけ許容、全変異拒否、純1成功 |
| PT-SSC289-TOPOLOGY | 完全生成AST、固定一pidfd TERM、子inspect/recover/post順、EPIPE時UNKNOWN保持 | 純1成功。Root/業務直接stop/force/DBterminateなし |
| PT-SSC289-PROOF | 新only stageと同artifact545bb84f5c6d58b9305ac4499a0f8afa916e2baee7dcba3c61547e1d30727cdb、fresh全原値/189/5FD/普通pool両端・十Ref | stage0/proof0/10:38:50Z、signals0/businessStops0/十Ref正常、proofada7084e。旧close falseのまま |

PG4202は既73＋新3=工具76/FES0、host/全emitted静的0、Production PT追加0。commandは`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg4202_continuation_qualification.py`。log SHA4231cb19166265e7f7314aff2bf56c3e8ba941406f56fd325bcad78c96883201。生成前TDDの禁止語検査は過去工具commentをコードと混同して失敗、AST上の実呼出しへ是正してVM操作前に合格。実失敗/業務障害に数えない。

設計source d51104ca3/隔離bae9825ce、設計only PR135/main e58ce46ac4117caa956583634b40db06d95112c9をremote確認。SS343/353/914だけ、実装/設定/証跡混在0。添付100件上限で不可、既存保全。

公開PG4204 manifest SHA8c998559fc1ced2d194421b85285d3dec139d2c5527463001572f72138b708a9、旧4152 actual255・4196safe・4200 stage/proof・4202結果/ログだけ。FD/DB/鍵/原本rawは私有保全、公開しない。全新scope/metadata正常閉鎖・実残5・別postは次の未完であり、旧Root143/旧close UNKNOWN/正式1964/53/旧17/190/工数null/QA051finalを変更しない。
