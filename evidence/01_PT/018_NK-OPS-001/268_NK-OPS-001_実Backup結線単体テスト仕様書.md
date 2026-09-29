# NK-OPS-001 実Backup結線PT（PG379、実行前）

RD OPS-009/BAK-001/BKO-001、UI251/253、SS341§5.1/6・342§4・343§6.17、SSC108/BUG325/YKT257。対象はInspectorUnitSnapshot、BackupUnitReceiptGate、MorningBackupUnitCycle、MorningBackupStage、MorningDatabaseSession、MorningProcessMain。正式認定は更新しない。

| Test ID | 目的・入力/操作 | 独立期待値・根拠 | 結果 |
|---|---|---|---|
| PT-OPS-BGATE009 | 固定18fieldのfresh exit1/255、old Invocation、signal/timeout/欠落・ABAをbus/kernel/busへ供給 | 新正常exit-codeのみFAILED、同kernel/再bus不一致はunknown、旧observeは成功0のみ。正常失敗を成功へ変換しない | 未実行 |
| PT-OPS-BUCYCLE008 | typed FAILED、真正stop/全終端/完了callback/原本request照合、callback失敗・期限切れ | FAILEDをそのまま返す。順序はreceipt→stop→terminal→結果確定→proof→marker退役。未知/失敗でowners保持。literal call順から算出 | 未実行 |
| PT-OPS-MBSTAGE009 | 同owner Epoch/原本/DB/request/begins/part、null/別activation/ISSUED | work内に同一INVALID Epoch、別ownerや欠落は処理前拒否 | 未実行 |
| PT-OPS-MDB015 | 同sessionの実完了/FAILED atomic記録、commit後再読、callback外/thread/失敗 | Connectionをexportせず両stepを同Connectionで更新・再読。期待はDDL/SQL後条件。fixtureだけでは実phase失敗の証明としない | 未実行 |
| PT-OPS-ARCHPROC009 | 親残7nsのconfig tool待ち/親期限経過・null | 子のwait budgetは7ns。新30分へリセットせず期限ではspawn0 | 未実行 |
| PT-OPS-MBACKUP001 | 実VM固定外部Morning→同owner固定Backup、独立SQL/Unit/files確認 | fresh真正worker、実dump/list・tar/age・公開manifest/hash、両step結果、全Unit終端、request/marker後条件。全Morning未完了ならMain30、permit未発行 | 未実行 |

前提：host Java25.0.4/Maven3.9.12、固定m2/Node24.19.0、隔離VM Ubuntu26.04/PG18/age1.2.1。実秘密/DBdump/credential archive原本はGit外private保存。hostは変更module選択test/static/JaCoCo、VMは同class hash/JaCoCo agentの外部process coverageを採取しhost execと同sourceのみmergeする。未網羅を除外せずcoverage100%未達は未認定。コマンド/source/run/終了code/input/expected/actual/hash/coverageを実行後269/manifestへ記録する。

接続図：Mainの単一30分budget→ControlScope.executeOwnedEpoch(M→原本DB→固定8stop→A→INVALID)→Stageの同owner preparation→Cycle(start→freshtyped結果→stop→全終端→実bundle/両step完了)→原本/current/request再照合→request退役→marker退役。不足はStage Epoch接続、Session狭い完了port、実親archive assembly/Expiry配備。これらはD04/05の同経路必要依存で、偽Unitや新規同等helperで補わない。

PG379 Production6回帰trigger（2026-09-30、実施前）：同owner Epoch/Backup typed terminal/結果確定/親tool budgetのsecurity・transaction変更群を一単位で固定し全6 clean test/static/coverageを実行する。018/269の途中選択runは正式53scopeや外部受入ではない。未網羅を明示し、続く同じ外部起動経路の結線へ進む。

PT-OPS-CANON001の独立roots byte oracleは`evidence/provisional/PG379-owned-backup/input/roots-golden.txt`。SS343§6.17から手書き固定した13行、SHA-256（独立sha256sum）は`4b08c89315842f33d6eae97a7c650f563987ca795e1793f3481b362c0646e962`。PUBLIC fixtureであり実host/root authority/正規issuer証拠ではない。Production encoderとの比較は未実行。CRLF/順序/一byte/UUID/owner/ino/freshness差の負試験を後続collector接続で追加する。5gateの完全byte oracleは未完了につきSSC108を閉じない。

PT-OPS-MNAMESPACE001（SSC109/BUG327/YKT259）：前提host localRW＋strict privateRO祖先、privateRW固定mutation対象。期待は両view同dev/ino/owner/mode/ACL/FSかつhostRWの祖先のみ許容、hostRO/差替え/ACL/不明は拒否、privateRO mutationは拒否。host注入fixtureと実VM statvfs/同Production Mainの一往復で検証する。先行VM診断はhost5対象RW、strict private4祖先RO/backupRW、exit0。固定Morning受入ではなく設定反例のみ。
