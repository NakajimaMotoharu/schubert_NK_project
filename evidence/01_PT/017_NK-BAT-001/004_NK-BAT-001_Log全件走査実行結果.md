# NK-BAT-001 Log全件走査 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-24/source5f2abbf26f67c19a4d60a0778057360313366759、09:06:27～09:19:08 JST/Maven12:39/exit0、全1659PT（Protocol80/Storage82/API689/Web400/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・74負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web18/159＝92部分成果869PT（全1659の内数）、今回再開比+244PT/+27部分成果。PG208 Music階層model8PT・PG209実template6PTを限定認定、新BUG/SSCなし。PG210/211通信/HTTPは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。Music HTTP未接続のためWeb33～48%・固定加重39.85～51.35%（中心45.6%≒46%、約40～51%）を維持。残量19%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

PG-D-138/003/PT-BAT-018～029。探索2は2026-09-09 14:54:20 JST終了、13.215秒、dev-foundation/100aea52後の未commit実装、exit0。新12＋既存17=29件全成功、新6classはline115/method16/class6/branch48/instruction493で全missed0、batch全14classも4coverage100%。NullAway/Enforcer/Spotless PASS・SpotBugs0。正式全module回帰/収集までは未合格。親OS/実backup/専用main/全batchは未完了。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify`。Log `/tmp/pgpt-log-service-explore-2.log`。探索1も29件/全gate成功（14:52:06、15.224秒）、探索2は欠落backup rowの追加matrixを含む再試験。

BUG-112/YKT-098は試験前reviewで起票。初回readの原因消去、直接helperはbatch非許可という根拠から、既存cleanupのreason→同transaction累積read→累積−chunkによる開始件数復元へ確定した。追加grant/SQL/保持条件変更なし、開始/最終/attempt期待値も不変。後続chunkでは直前確認累積との一致をcommit前に検査。初回/途中backup FAILEDと欠落、row/advisory lock、他SQL故障を別reasonで再試験した。

PT019: 保全10000＋後続eligible1は3commit、累積10001/1/10000/END、保全10000不変。PT020: 開始2/0/2→最終3/1/2、attempt1/1/0、既完了再実行はattempt0でもrun保全ありWARNING。PT021: 親session advisoryは自分の再入1回解放後も他connection取得不可、親の解放後だけ取得可。未取得親ではserviceの取得分だけ解放。OS flockを取得したとはしない。

PT023/024: 30分前/一致/超過、単調時刻後退/自然wrap、開始前/commit後interrupt（flag維持）。PT025/026: commit前故障はrollback、commit後不明は次run読取で二重計上なし、rollback失敗後restore0回・接続廃棄で暗黙commitなし。restore/unlock/資源close故障は成功summaryなし。PT027/029: NULL/欠落/多重lock・進捗/差引負/前chunk累積不一致を拒否、26 JDBC故障点を実注入回数で確認、programming/clock例外は伝播。Provider text/causeは運用例外へ残さず、close重複故障のsuppressedも固定CleanupStoppedExceptionだけ。

YKT-092の対象照合: LogはV014＋repository＋本serviceでcursor/件数/END/再開を接続。InboxはV012とinspectStoredNextのUUID cursor・同commitあり、既存PT073～088/097～104で保全1001行の進行を再試験する。notifications/questions/sessions/outbox/batch/progress cleanupは保全をcandidate外で除外し、非削除保全行を同chunk targetへ再計上しない（既存PT065～080/089～096/153～160）。全正式回帰で横断再試験してからBUG-104/YKT-092の当原因を閉じる。OS/main/実backup等はBUG-014/YKT-012側の別残件として継続し、他Programへ付け替えて基盤100%とはしない。

020 collectorはbatchの2class/29 Test IDを必須とし、欠落/重複/別class/未知/失敗/flaky/skippedを拒否。019へ独立12 ID・2class集合の負canary追加。017の1件＋019の5件は品質tool PTでありJava29件へ二重加算しない。
