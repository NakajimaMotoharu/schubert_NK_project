# 281 通常resume Backup実再検証（PG387、登録時NOT-RUN）

NK-OPS-001/NK-BAT-001、OPS009/BAK、UI251/253、SS341§5/11・343、SSC116/BUG350/YKT280。対象BatchRunRepository/MorningDatabaseSession/MorningBackupStage/MorningBackupArtifacts/BackupWorkerRequest/BackupDatabaseWorker/BackupArchiveProcess。元SUCCESSと今回SKIPPEDのidentity・fresh子・成果・DBを分離する。

| Test ID | fixture/入力/操作 | 独立期待値・算出根拠 |
|---|---|---|
| PT-OPS-BRESUME001 | 実PostgreSQLの同run元DB/CONFIG SUCCESS一対、通常beginと手動beginを別portで実行 | 通常両SKIPPED/ALREADY_SUCCESSFUL/全0、元全列不変。手動は新RUNNING。SQL literal結果、Production expected生成禁止 |
| PT-OPS-BRESUME002 | 片成功・別run・別started/attempt/ended・null/欠落/未知・commit/readback fault | 親成果根拠・permitなし、元成功無変更。全pair不整合拒否 |
| PT-OPS-BVERIFY001 | 手書きASCII/LF NKBACKUPVERIFY1 literal、run/start/manifest SHA/dump size/SHA | exact byte順序・導出名一致、入力消去。生成NKBACKUP1とは閉鎖分岐で相互代用しない |
| PT-OPS-BVERIFY002 | 空/欠落/重複/並替/未知/非ASCII/非canonical/hash/size/null/境界/並行 | 拒否・owned byte消去・生成経路にfallback0 |
| PT-OPS-BVERIFY003 | 実保持dump固定byte、専用普通UID metadata、実process command記録 | pg_restore --listだけ実行、pg_dump/新part/secret読取0、保持前後inode/size/hash一致。SHAは固定literal/独立hashlib |
| PT-OPS-BVERIFY004 | 改変/別inode/owner/ACL/RO/IO/child非0/未知/interrupt/時計・全終端故障 | permitなし・元成功改変0、生成FAILED callback0、UNKNOWN隔離維持 |
| PT-OPS-BRESUME-VM001 | 同source genuine外部Morning --resume、実既存attempt5成功bundle | fresh実Backup検証Invocation、実restore-list、新dump/part/credential archive生成0。元行9/10全列/hash不変、今回両SKIP全0・独立再読/request/intent退役 |

manifestに日時/OS/JDK/tool/branch/対象source/実command/exit/input/expected/actual/coverage/BUG/SSC/hashを保存する。source固定host+実native coverageのline/method/class/branch100%を要求し、未網羅/NOT-RUNを合格にしない。全S1/timeout/S2/issuer/APIWeb/CHR/正式53scopeは別gate。秘密・dump実体・raw token/session/keyはGit外。今回SKIPは実検証前に発行根拠にしない。
