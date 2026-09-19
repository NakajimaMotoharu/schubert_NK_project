# NK-DAT-001 Inbox検査権限・候補lock実行結果

2026-09-20 最新確定: dev-foundation/source139c74b3dd844a213bf5581d51f4814219386497、正式PT-WEB-20260920-05（02:55:42～03:07:25 JST、Maven11:42/exit0）、全1479件（Protocol80/Storage82/API668/Web241/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。15collector/38scope整合・49負canary成功。DB29/266＋Batch25/281＋OPS16/134＝70部分成果681PTを維持。PG187の8PT成功・BUG208/209/YKT164/165完了だが、BUG210/YKT166のTest ID表記差が残りSSC069/新OPS1部分成果は保留。今回再開比+64PT/+5部分成果。PG188受付IDは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/Question/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、利用枠残68%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/inspection-sql/manifest.jsonの現行SHA-256は `3f95f71c3ad75f250c21755370737e56983eb1b8027de80af166555a536a145f`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

最新回帰PT-WEB-20260909-18/source56935aa0、2026-09-09 09:44:09 JST終了、全838件/全Java coverage100%/静的解析0、SQL候補8件再PASS。現在の `evidence/inspection-sql/manifest.json` SHA-256は `646e043600e7560ab46177b316d6267c0a1bae883e0b0e0b516b99453766dece`。以下のrun15/hashは証跡commit5396be17の初回確定履歴として区別する。V009後の履歴件数は9件、再適用0、V001～008のsourceは不変。

## 1. 対象・状態

007仕様PT-DB-INBOX-017～024、V008の検査用role/候補functionは正式PT-WEB-20260909-15で全8件PASS。BUG-079/080とYKT-070/071は本証跡により再試験完了。各探索は新規隔離PGへ適用して終了時に停止する。既存正本V001～007/既存本番DBのchecksumは不変。正常削除・全layout・oneshotを含むNK-DAT-001全体は未完了。

## 2. 修正前の実結果

| 日時・実行 | 実際結果 | 根拠/対応 |
|---|---|---|
| 2026-09-09 08:06:56 JST終了、session44311、dev-foundation未commit V008 | 新SQL8件PASS、既存DB15件中1 failure、exit1。Protocol5/Storage16成功 | 同時migration後のSQL件数oracleだけ7L残り、actual8。BUG-079/YKT-070をb9872e09で先行起票後8Lへ同期 |
| 08:11:46 JST終了、session3530、dev-foundation未commit V008 | 新SQL8件中1 failure、error/skipped0、exit1。PT021 expected55000/actualACCEPTED | BUG-080/YKT-071を90545e1aで先行起票。DB backup rowを別TXでlockし、検査queryのlock待ちをpg_blocking_pidsで観測、その後CONFIGをINSERT/commit。初回queryがlockしていないCONFIGを後段EXISTSが採用した |
| 08:13:45 JST終了、session17854、dev-foundation修正V008 | 新SQL8/認証参照8/既存DB15の31件成功、Protocol5/Storage16も成功、全failure/error/skipped0、exit0 | 新規適用/再適用/同時migrationと固定inventory8件、backup snapshot raceの55000と次TX正常、全role/row lockを確認。正式全回帰/収集は次段階 |

BUG-080修正前SQL SHA-256: `36da261d78007dfff0e3a2b60ec88236073c00255836dab5b8349ff48d2f269d`。実credential/暗号平文/DB dumpを使わず、時刻/SQLSTATE/件数だけを保存する。
再発防止は同一queryのFOR SHARE結果を集約したstep集合だけで両成功を判定すること。後段EXISTSを廃し、新しく完了したbackupは次のtransactionで取得する。例外を成功へ変換しない。最終削除を接続していないため実削除は0。

## 3. 分岐・横展開の対応

- 引数: run/cutoff NULL、±infinity、after NULL/既知/未知をPT018/019/023。
- Backup: 0行/片方/両方、state/date/run/ended不正、row更新lock、途中追加をPT018/021。
- 候補: expiry未到達/境界/超過、PROCESSING/COMPLETED/ERROR、LGN/LOG/他layout、1行上限/PK順/emptyをPT019/023。
- 参照: AUTH_SESSION存在/欠落/NONE、実独立暗号のJava認証検査と失効非更新をPT021。参照が無くてもSQLで架空sessionを作らない。
- 権限: role属性/列grant/禁止DML/DDL/SET ROLE/他schema/他roleからのEXECUTEをPT017/022。
- Transaction: Inbox/参照/backup row lock、advisory別session競合、rollback後解放をPT020/021/023。
- 既存migration: 新規/同時適用8件、再適用0、全8version/inventory9file、既存V001～007の差分0をPT024＋既存DB15件で再試験する。

V006等の既存6cleanupは新関数のlock済集合を再取得する形式を持たないためYKT-071の同形式修正対象外。既存Inbox誤削除保護を完了にする根拠にはせずBUG-014/YKT-012で継続。新SQLの候補/参照も実際にlockした値を使うことを確認し、検索だけで横展開完了にしない。

## 4. 再試験・証跡

部分探索command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InboxInspectionBoundaryTest,DatabaseMigrationTest,AuthenticationInboxInspectorTest test`。正式commandは007。

正式PT-WEB-20260909-15/source586b3ffe、dev-foundation、2026-09-09 08:23:44 JST終了、exit0。全814件（Protocol80/Storage34/API418/Web241/CHR41）failed/error/skipped0、対象5moduleのline/method/class/branch100%、NullAway/format/Enforcer成功、SpotBugs0。SQLは上記§3の全条件matrixを実SQLで検証し、Java JaCoCo値でSQL coverageを代用しない。8collectorの10scopeを収集しchecksums全一致、017 trace canary（欠落/誤path/誤hash/外部参照の拒否）成功、baseline843de94差分0。V001～007の差分0、既存DB15件もPASS。

証跡: `evidence/inspection-sql/manifest.json` SHA-256 `766dcd72c8db980d80b68d435acbc11b44ab2884f32f8ecd96b42c041e11526a`。実行時刻/環境/command/source、PT017～024のmethod一意対応、V008/provision source hash、sanitized実結果・全体manifestへの存在/hash検証済みリンクを含む。秘密値・DB dump・raw電文は保存しない。未確定の削除機能を合格へ加算しない。
