# NK-OPS-001：PG458コード配備・同親再受入仕様

関連RD NK-OPS-001/UI251/SS341342343、SSC178179、QA047～050回答済。Production source固定=`ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a`。PG457の選択試験/旧signed559復旧を、このsourceの全回帰・native合格へ流用しない。IT/ST宣言なし。

| Test ID | 対象/操作 | 独立期待値・事前条件 |
|---|---|---|
| FULL458001 | `pg458_full_v1.sh` 全6 clean/PT/SpotBugs/NullAway/coverage/runtime | source前後hash・actual終了0・全XML FES0・静的各0。coverage実missを残し100未達を合格化しない。中断PG442/別source3249を加算0 |
| CODE458001 | Pg458CodeOnlyDeployment.arguments/names 42固定vector | literal40/64hex/verify又はactivate、exact5（INVALID current/旧permit/owner/2launch）、各欠落/foreign/intent/null/未知mode拒否。工具assert、ProductionPT0/native権限0 |
| CODE458002 | 新only候補/BOM/signature/pin/既存profile・DB・原本/Backupのverify | 旧PG456/source559/digest21affa…、現在boot e07aa706…、同27SQL byte・Flyway28履歴、旧261全14列/23business・pending原本・Backup20/Transfer/config/Asset全一致。真正M/A/DB advisory71419602/readonly schema、全9kernel空。旧epochINVALID/intent0からのみ。受入前署名byte/fullBOM確認、DDL/start/permit0 |
| CODE458003 | owned code-only activate | private new-only SAVE/fsync→全保存集合/各startupbyte-metadataの再照合→既存正規activateのfreshINVALID/approval/current→同全後条件。schema027/profile/Caddy設定/27SQLは同byteのため変更0、原本/DB/Backup不変更。旧4record保全、新currentINVALIDだけ。所有不明・部分失敗は隔離保持、force repair/旧current正常化0。全owned正常帰還後のみ成功 |
| PARENT458001 | 一度の外部Morning、readonlystable observer | 当current/source/署名/Root→ordinary同PID・ticks・Invocation/親世代・固定identity/GID/groups/NNP/5cap0、actual管理UP/info5/同ownedsocket、API所有保持Web。元30分budget/各Unit期限不変更。非安定混合は再観測、欠落Root捏造0。既存startに再付着、二重start0 |
| CADDY458001 | 同親Caddy validate/start/HTTPS `/login` | 真正code=exited/status0（legacy0/0も正常値のみ）、固定TLS55160・publicCA・title「schubert NK」/HTTP200、同APIWeb/同Caddykernel socket/NNP/5cap0。失敗時本人stop→borrowed fence close-only→WEB/API逆順停止、未知は所有保持 |
| DONE458001 | live intent退役/保持原本/outer | 当Sessionの全10step実結果・DB前後条件から原本pending→DONE、same-owner WEB/API intent退役、真正親0又は10、全outer normal close後だけ。API ready/TLSだけで全体合格0、backend継続稼働と親のowned observer closeを区別 |

環境はhost JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4、隔離VM Ubuntu26.04/PostgreSQL18.6/JDK25.0.4/Artemis2.56.0。full source・終了・前後hash/XML/static/全target byteはWorkPG379へprivate保存し、redact XML/manifestのみGit保存。署名鍵/原本/permit/owner/session/DB dumpをGitに格納しない。新工具はactual guest閉集合16classでcompile/独立testを行い、新singletonだけ追加して旧工具を上書きしない。

実行入口：`bash tools/quality/vm/050_s1/pg458_full_v1.sh ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a`。full capture完了後に限り新signed候補生成・new-only stage→工具verify→activate→external Morningを一回発行し再付着。旧PG456 migration/appliedcompletion・PG457 recoveryを再実行しない。各actual command/時刻/退出/BUG/hash/resultは327結果と456へ追記する。全体coverage100・実CHR-A01/L01・native同byte正式は後続の未受入条件であり、この仕様の作成で完了扱いしない。
