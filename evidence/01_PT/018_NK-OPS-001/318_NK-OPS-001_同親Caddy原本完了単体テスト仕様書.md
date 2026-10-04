# 318 NK-OPS-001 同親Caddy・原本完了単体テスト仕様書

2026-10-04。PG455 / S3-D05 / SSC178。未実行・未受入。設計公開は origin/main `437cdeb5f`（設計source `880c67b82`、PR #9）、実装/試験sourceは実採取後に319へ記録する。

## 対象と独立oracle

NK-OPS-001/NK-BAT-001/OPS009、UI251/253、SS341§3/10/12・342§3/4/SSC164・343§6.15/6.17。MorningNewRunAdmission/ResumeAdmissionの保持原本cap、MorningControlScope/BackupStage/Mainのtyped正常結果、MorningStartupLaunchOwner、BackupUnitStartClientのlive-ready専用退役、固定Caddy daemon/smokeを対象とする。新業務仕様・電文・DDL変更はない。

期待値は以下のliteral順序、公開合成UUID/µs時刻、手書きUnit/HTTP/DB full-column fixtureから作る。Production methodで期待値を作らない。実Caddy/Morningプロセスは既存の外部Unit・正規署名candidate/現在boot/真正same-ownerから採取し、reflectionによるmain擬似呼出しをnative成功へ算入しない。

| Test ID | 入力・操作/事前条件 | 独立期待値・観点 |
|---|---|---|
| ORIG455001 | pending同activation・同thread/aliveでverify→complete→verify | 同保持Sessionだけ、完成値全一致・active/pendingなし。別Session生成0。閉鎖後cap使用拒否 |
| ORIG455002 | foreignthread/失効/別activation/null/verify-only port/二回完了/既done別時刻又は0↔10 | 変更0又は初回だけ、固定例外。既done全byte不変。capを持つことだけで親終了0にしない |
| ORIG455003 | root/filesの前後各IO/Runtime/Error、complete後のgraph不明 | 正常completeを返さず、部分公開は修復/削除0。実経路では所有保持/保全、次scopeを成功へunwindしない |
| PARENT455001 | 実必要保守とpermitの完全結果、同API/Web世代 | literal `API→Web→Caddy→WEB intent退役→API intent退役→done→外側close→exit`。両intentはCaddy送達まで連続保持 |
| PARENT455002 | 各段故障/世代交換/期限境界/半退役/stop不明 | 通常失敗はCaddy→Web→APIの逆順全終端、UNKNOWNは所有保持・残留保全。ready単独/停止単独をdoneへ補完0 |
| MAIN455001 | 全必要実結果SUCCESS又は許容WARNING、全scope正常close | 0又は10。実Backup FAILED＋六BACKUP_UNAVAILABLE＋実Transfer/Expiryは10、未知/未実行/criticalは0/10不可 |
| MAIN455002 | 原本/DB/credential/M/最後root各close又は検査故障 | 途中typed値があっても0/10不可。各IOException/Runtime/Errorの同一原因を保持し、NPE catch正常化0 |
| CADDY455001 | fixed cold Unit→validate→一度start→fresh manager/kernel世代→実TLS/login | client0は非ready。Caddy daemon ABI・本人socket・証明書検証・HTTPS200と同API/Web世代が必要 |
| CADDY455002 | client非0/null/送達例外/期限/異boot/PID/Invocation/socket/証明書/HTTP異常 | fake receipt/別enum/二重start/無検証TLS0。送達不明は両intent保持、公開停止は真正全終端まで確認 |

## 実行・証跡・終了条件

変更moduleと依存canaryをまとめた独立selected試験→actual exit/XML F/E/S0・静的6module0・source前後hash/coverage counters/全到達byteの保存→同所有契約source固定fresh全6回帰→正規27migration/BOM/Backup inventory/現在boot再認証→実外部Morning/API/Web/Caddy/保持原本done・intent後条件→実NK CHR/native採取の順。source/工具/設定の変更後へ旧成功を流用しない。

coverageはline/method/class/branch全100を要求し、host到達・native到達の不足を明記する。生成除外/到達不能扱い/無意味assertは追加しない。全scope同一source/run、独立DB full-column/HTTP-TLS oracle、null/空/未知/異常/並行/再送・期限、NPE静的0、BUG先行起票・必要YKTを維持する。

結果は319と安全manifestへ実日時/OS/JDK/tool version/branch/source/command/exit/対象counter/期待値/実値/BUG-SSC/hashを記録する。raw log/私有VM材料/秘密/DBdump/実token-cookie-session-keyはGit外の `work/pgpt-runs/PG379` と既存私有保全へ限定する。通常ログ全文を再読/転載しない。正式run24/1964PT/53scopeは新認定実証まで据置、IT/ST合格を宣言しない。
