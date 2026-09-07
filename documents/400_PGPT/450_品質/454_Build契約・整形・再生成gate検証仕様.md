# Build契約・整形・再生成gate検証仕様

## 1. 対象と期待値

対象ProgramはNK-PRO-001/002と共通Build基盤。RD TST-001～005、UI234～236/264、SS323/354/355、411/451、PG-D-010/013/030/031に対応する。外部仕様、Current baseline、wire goldenは変更しない。

| Test ID | 対象・操作 | 独立した期待値・根拠 | 異常・再発防止 |
|---|---|---|---|
| PT-QUALITY-003 | 親Spotless3.10.2/GJF1.36.1で全Java main/testをcheck | 固定formatter差分0、除外0。411 §11 | BUG-017初回validate失敗を検出。機械整形後に全reactor check/PT/coverageを再実行 |
| PT-QUALITY-004 | 親Enforcer3.6.3で全reactor validate | Java[25,26)、Maven[3.9.12,4)、dependencyConvergence全rule PASS | BUG-018 SLF4J2.0.18/1.7.13不一致を検出。親management固定後も依存経路を除外しない |
| PT-QUALITY-005 | 001_generate_payload_records.pyを隔離directoryへ実行、固定formatter後に全生成物とproductionのSHA-256比較 | SS323の69 named record＋catalog1件＝70件、全件byte一致。比較でprotected source変更0 | 隔離catalogへの故意1行追加を差分1件として検出。BUG-019のdecode/encode semantic呼出し欠落を恒久検出 |

## 2. 実行・証跡

実行環境・導入元・固定hashは421 §5.2。コマンドはroot `clean verify`と`tools/quality/002_verify_generation.py`。null境界は453、DB/JMS境界は各ProgramのPT仕様に従い、これらのBuild検査を機能PTの代替としない。

006_NK-MSG-002の継続reactor証跡へrun ID、branch、対象commit、日時、OS/JDK、command/終了code、各counterを保存する。`evidence/quality/generation-results.json`に70件のhash、source不変、negative結果を格納し、同directoryのmanifest/checksumsへ登録する。BUG-017～019/YKT-014～016は修正commitと正式再試験証跡を照合した後に完了とする。
