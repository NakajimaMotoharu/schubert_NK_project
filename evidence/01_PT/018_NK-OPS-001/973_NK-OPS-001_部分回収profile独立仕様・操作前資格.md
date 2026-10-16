# NK-OPS-001 部分回収profileの独立仕様・操作前資格

2026-10-16、Production7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e/PG3976。QA047、SS342/343 SSC288/353、BUG1341・1342/YKT1107・1108。正式1964PT/53scope・旧個別17/190履歴・工数null・QA051final不変更。

| Test ID | 事前条件・入力/操作 | 独立期待値・結果 |
|---|---|---|
| PT-SSC288-READ | 元4152 UNKNOWN/固定boot・二retainer/Caddy既stop、4160 read | Caddy18項目の同INV正常終端/kernel0、残3actor/全24/原値/native50/startup33不変。actual0。全32宣言同値・動的ExecStart差だけ。98/7FD二読保持 |
| PT-SSC288-DECL | 32field、path/argv/ignore/null/missingの独立変異 | 宣言変更を全拒否、動的ExecStart時刻等は宣言比較から分離。純2成功 |
| PT-SSC288-PAIR | 固定98/7FD集合、全9metadata/fdinfo/権限/子/世代変異 | 不一致拒否・同世代zombie/FD0だけ限定許容。profile純3/keeper純2成功 |
| PT-SSC288-POOL | SS342 literal API2..8/Web1..2、境界内/外・停止role/未知/null/bool | 本人両端socket前提、範囲内だけ許容・停止role0。旧4176は総数3仮定でactual1を保全、是正純2成功 |
| PT-SSC288-PRIOR | Caddy既終端のcallback/部分new-only namespace/fresh SQL oracle | Caddy通常stop呼出し0・同INV正常終端確認のみ、残5stopと別post。純3成功 |
| PT-SSC288-HOST | SSH shell roundtrip・固定phase/旧source/hash/実exit変異 | -c全programを一引数、ACK別channel、旧4152 actual143は失敗のまま、他source/正常化拒否。純2成功 |
| PT-SSC288-PROOF | 4182新only stageと同3hashのproof、実M/A保持旧pair・新十metadata Ref | actual0/2026-10-16T10:22:03Z、signals0/全原値・全189/普通pool両端/十Ref正常返却。新TERM/業務stopは未実施 |

PG4190で既59＋新14=工具73/FES0・host/全3emitted静的0。log SHA a418f2aec941645c11c3b2e5dd31eb0d99f94f585b3f62aeb464d64dd1936d6f。実行環境/command/source hashesは公開manifest・元私有PG4190に保存。Production PT追加0、Java四coverageへの加算0、工具coverage100%の主張0。

実行：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg4190_partial_recovery_qualification.py`。全VM/DB/FD rawはPG379/guest私有領域に保持し公開しない。

設計source7f4bd9624、隔離a9ee1238f、PR134/main9d300bd12881a2fae3a1b42654c10cc9eb105e47をremote確認。mainはSS343/353/914だけ。添付は既存100件上限で不可、既存添付を削除しない。

次はclean固定・fresh所有確認後、pg4188の一回実行。旧4152の元observer終了143回収→残5真正terminal/revoke/別post/keeper正常返却は未完。Root失敗/BUG1332原因・新正常経路/native資格/F03/CHR/全四100/451/traceは後続で、旧成功を移植しない。
