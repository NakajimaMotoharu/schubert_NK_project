# NK-DAT-001 認証Inbox条件付き削除実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-25/source42d8bfbf0c0d88a27ba29a8f9cf0054d5cdacc58、09:26:44～09:39:24 JST/Maven12:39/exit0、全1679PT（Protocol80/Storage82/API689/Web420/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・76負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web20/179＝94部分成果889PT（全1679の内数）、今回再開比+264PT/+29部分成果。PG210 Music通信8PT・PG211分類/区分HTTP12PTを限定認定、BUG223/YKT179完了。PG212～214 Log表示/通信/入力は仕様のみ・SSC073対応中。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。Music2画面HTTP接続を根拠にWeb38～53%・固定加重40.85～52.35%（中心46.6%≒47%、約41～52%）へ更新。残量16%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/deletion-sql/manifest.jsonの現行SHA-256は `09340077e7c7107b841c32b2f4cc4b4a725d9e68a6bc1f58199f03952c67384f`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

最新回帰PT-WEB-20260909-18/source56935aa0、2026-09-09 09:44:09 JST終了、全838件/全Java coverage100%/静的解析0、条件付き削除8件も再PASS。現在の `evidence/deletion-sql/manifest.json` SHA-256は `fd139aec64fe27681a30e626a54368df3cf4f1990d398d26aa11e5bd46f648e9`。以下run16/hashは証跡commitd6f5d838の初回確定履歴として区別する。新しいJava検査削除接続の結果は012。

## 1. 対象・現在状態

PG-D-122、V009、009仕様PT-DB-INBOX-025～032を正式PT-WEB-20260909-16で確定。新規の条件付き削除SQLで、既存V001～008は不変更。SQLは暗号検証を行わず、Java接続・全layout・oneshot・BUG-014全体は未完了。

## 2. 探索履歴・障害

| 実行・終了日時JST | 結果 | 根拠と対応 |
|---|---|---|
| session48557 / 2026-09-09 08:43:36 | API31件中1failure/1error、skip0、exit1 | PT030: 存在しないWeb/ops role名、PT031: revokedだけ更新する不正fixtureでexpected55P03/actual23514。BUG-081/082・YKT-072/073を134269abで修正前起票 |
| session70100 / 08:45:44 | API31件中1failure、error/skip0、exit1 | PT031: UUID(0,104)と文字列末尾104の十進/十六進不一致で参照欠落。lock期待に対して例外なし。BUG-083/YKT-074をf283372eで修正前起票 |
| session34103 / 08:47:12 | 新SQL8・既存候補8・既存DB15の31件PASS、Protocol5/Storage16もPASS、exit0 | role実在と実connection拒否、失効複合条件、session参照JOIN1を事前assertしてlock前後/解放後を再試験 |

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InboxDeletionBoundaryTest,InboxInspectionBoundaryTest,DatabaseMigrationTest test`。branch dev-foundation、未commit V009作業中。実credential・平文・dumpを保存しない。期待値をコード都合で変更せず、正本role/制約/UUIDへfixtureを一致させた。

## 3. SQL全条件matrix・横展開

- 引数の各NULL、±infinity、transaction ID format/1～20桁境界、hash長・不一致、別/終了済transaction: PT026/028。
- Backup無し/片方/両方/別run/別日/FAILED/ended欠落、advisory競合、backup確認途中のSUCCESS追加をPT029（同じlocked snapshotだけで合否判定）。YKT-071のV009追加対象も再発防止試験する。
- WHERE: Message・暗号文hash・LGN/LOG pair・両version・PROCESSING/正常/error・NONE/AUTH_SESSION/他参照・owner/token・日時finite/order・168h±1µs/等号・cutoff±1µs/等号をPT025～028/031。owner/token/不正参照/created>completedは実CHECK拒否23514も確認。SQLが検証できないAES/refはJava gateへ残す。
- RETURN: DELETE1/0/既削除、rollback復元・commit確定・再実行をPT025。session/backup/userは非更新。
- 権限/catalog/PUBLIC/service role/任意DML/SET ROLEをPT030。V008/001の既存正本roleも照合（YKT-072）。
- 競合: 正しいFK参照JOIN1を前提に候補・参照・backupの更新が削除前後55P03、rollback後更新成功をPT031（YKT-073/074）。SQL単体によるSAVEPOINT暗号証明は主張しない。
- Migration新規/同時9件、全001～009/再適用0、resource10file、旧8migration不変、既存DB15をPT032/DB001/013/015で照合。

## 4. 正式証跡

正式PT-WEB-20260909-16/source2f375c92、dev-foundation、2026-09-09 08:55:19 JST終了、exit0。新8件を含む全822件（Protocol80/Storage34/API426/Web241/CHR41）成功、failed/error/skipped0、全5moduleのline/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。8collector・11scopeのchecksums全一致・trace正負canary成功、Current baseline843de94/V001～008差分0、秘密pattern検出0。

`evidence/deletion-sql/manifest.json` SHA-256 `1f10264619a37654ec15ba74fff50d169a33f872ab028941daabd0acdace5481`。実行日時/OS/JDK/tool/source/command/SQL matrix/独立oracle/全Test ID実結果/関連BUG・SSC/全体manifestへのhash検証済リンクとV009 source hashを保存。BUG-081～083/YKT-072～074は本正式再試験で完了。追加探索session64595/08:49:14 JSTも31件PASS、backup途中追加を55000で拒否し、同TXの暗号文変更後はfalse、rollbackで復元した。SQL単体を暗号/参照の証明として扱わない。
