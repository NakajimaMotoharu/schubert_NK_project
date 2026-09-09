# NK-DAT-001 Log永続走査 単体テスト仕様書

## 1. 対象・根拠

V014/log_cleanup_progress・maintenance_cleanup_logs/maintenance_read_log_cleanup_progress/maintenance_cleanup_log_progress。RD DAT-009/OPS-009、UI251、SS331 §3.9/332 §11.4/341 §7.2、BUG-104/YKT-092/012、SSC-051/PG-D-136。
実PG18・独立固定時刻/ID/SQL後条件、hold/90日/400日をProduction SQLから算出しない。8件のJava testはSQL分岐matrixでありJaCoCoの代替ではない。

| Test ID | method | 観点・入力・独立期待値 |
|---|---|---|
| PT-DB-INBOX-153 | heldPrefixCannotStarveLaterLogs | 先頭hold2件/後続eligible1件、limit2。同run 2/0/2→1/1/0→0/0/0、累積3/1/2/END。旧V013は2/0/2を反復、rollback-onlyで再現 |
| PT-DB-INBOX-154 | cursorOrderCutoffAndReplay | 同logged_atのID順・limit1/10000・±1μs90日/hold境界、完了run再呼出0、新runでのみ再走 |
| PT-DB-INBOX-155 | deletionAndProgressAreAtomic | commit/rollback/savepoint/再接続後に行とcursor/累積の双方一致。削除後更新overflowを22003等で拒否し全rollback |
| PT-DB-INBOX-156 | locksNeverSkipUnseenRows | log先頭/途中row NOWAIT・advisory/progress/backup lock、競合0/LOCK_BUSYとcursor不変。解除後同runで全行、同run並行二重計上なし |
| PT-DB-INBOX-157 | gatesRolesAndClosedReadProjection | 全8cleanup共通backup2step/role/NULL/不正limit、readの未開始false/保存値/cutoff不一致、最小4columnだけ、直接table/他role拒否 |
| PT-DB-INBOX-158 | progressConstraintsAndFailures | 8column/5CHECK/PKと型、各NULL/負/overflow/cursor組合せ/非有限/不正ID/完了時刻、SQL失敗を合格にしない |
| PT-DB-INBOX-159 | completedProgressRetention | 400日±1μs/現在run/未完了/RUNNING・FAILED調査/limit/rowlock/rollback。保護を削除しない |
| PT-DB-INBOX-160 | appendOnlyInventoryAndCrossCleanup | V001～013 hash不変、23table/PK23/CHECK154/FK23/UK30/trigger1、function owner/grant/path/UTC。他cleanupはcandidateから保護を除外/削除、Inboxは既存cursorありという横展開根拠を旧PTと照合 |

## 2. 既存oracleの修正範囲

PT095は1回目4/3/1後の2回目を0/0/0/OKとし、保全行7は残る。従来の1/0/1はBUG-104の再計上そのもの。rollback(savepoint)後の初回limit2=2/2/0と旧V006保持違反反例は維持。
旧全table/constraint/migration期待値は上記SS追加分へ更新する。DB011の初回3/2/1は維持する。入力fixtureを新table初期状態へresetする。Sourceからexpected inventoryを生成しない。

BUG-106/107・YKT-094: PT093のrowlockはSSC-051に従い0/0/0/LOCK_BUSY・進捗0・log2行不変、解除後の削除は維持。PT071の設定破壊は承認8関数のうち1件が不適合となる7を期待する。旧7関数/6期待は履歴以外で用いない。
BUG-108/YKT-095: PT158の90日同値は`2026-06-19 00:00:00+00`で固定し、UTC/Asia-Tokyo/America-New-Yorkの3設定で全mutationを再試験。失敗時は秘密を含まない公開mutation名を表示する。閾値から離れた日付fixtureは順序/hold判定用であり同値境界ではない。

## 3. 実行・証跡

Java25/Maven/PG18/toolchainは421、root clean verify/018全scope収集は451/458。日時/対象commit/環境/command/終了code/Test ID/実際値/BUG/SSC/hashは040とevidence/log-cleanup-progress/manifestへ固定する。未実装・未実行であり合格なし。親batch/OS lock/実backup/IT/STは別未完了。
