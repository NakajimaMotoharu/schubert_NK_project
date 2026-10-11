# NK-BAT-001 PG1405～1411 限定結果

仕様078/023/SS331/332/341/343/451。Production Main769ddb15・VM PG1292/BOMecae187/schema028は不変更、変更はBatch二testの追加3method。実行source254435330、branch dev-foundation。静的/selected PTと後続独立counterのsource/runを別記する。正式1964PT/53scope・全WBS受入不変更、IT/ST完了ではない。

|Test ID|期待値/実際値・独立根拠|結果|
|---|---|---|
|PT-BAT-RUN1405001|non-Backup ordinary resumeはattempt1 RUNNING/0/NULL、finish後SUCCESS/5/3/0/9/NULL/NULL、verifyFinished前後全行不変。手書SQLliteral/SS331根拠|PASS、実隔離PG18.6/DDL28、public fixture・tmpfs。normal/再開/非重複発行の限定契約|
|PT-BAT-RUN1405002|skipped handle及びend=started-1sをIllegalArgumentException、JDBC probe種類empty/statement-row0/全DB不変|PASS、異常/境界をDB参照前に拒否。Production期待値生成0|
|PT-BAT-PROFILE1405003|0x7fは許容ASCII0x20..0x7e外、IllegalArgumentException/全所有input wipe0|PASS、既literal goldenをbyte一箇所だけ変えた独立negative|
|PT-BAT-SELECT1409001|batch二suiteのみstrict test、XML fresh/名前/実時刻、20＋4=24/FES0、NullAway compile/Spotless/SpotBugs0、全Batch Main classbyteが1279と等しい|PG1409 actual0、2026-10-11T01:53:31.889332Z～01:54:03.670482Z。依存三moduleは1408 compile-only/Main byte資格を再確認して再buildせず、未試験をPASSへ加算0|
|PT-OPS-CLOSING1411001|独立手書session/probe matrix（別session/start、dump逆転/範囲外、probe欠落/false、class-name/id/length、null/empty/duplicate）とactual terminal→closing subset|Werror0/20assert0、同session・probe単調包含を実証。raw terminal保持、coverageへlatest closing一件だけ選択、same-session union0|
|PT-BAT-COUNTER1411001|Root8＋Bootstraplatest closing1/host6/新selected1=16exec、全6same Main/JAR CRC0/全counter/独立XML|actual0、旧1410二dumpunion診断と全6counter値は同一。miss L896/M176/C12/B719、新gainはL1/M0/C0/B4。BatchRunRepository/BackupProfile両classは独立XMLのL/M/C/B missed各0|

PG1406は非対象protocolの厳格no-testをCLIでoverrideできずexit1（batch not-run24）。古target XML18＋3は当run成功ではない。PG1407は依存install lifecycleのverify/既未達coverage checkでexit1、freshXML0/not-run24。PG1408は依存compile-only資格0の後、追加test一箇所formatでexit1/not-run24。BUG1092/YKT861、1093/YKT862、1094/YKT863を修正前登録し、独立scope/old-fresh-missing XML/phase literal負例とnew1409actual0で再試験。旧失敗・XML・ログは私有保全、再実行/成功化0。

BUG1095/YKT864: 既1401/1402/1410のsame-session二dump投入を品質再点検で発見し、1411最新closingのみへ是正。旧union診断は不変更で保全するが、現在の選択policyや正式証跡として流用しない。捕捉physical10と選択native9は別数値。二dumpのsubsetを実証したので、以前のgain数値自体は変わらない。四100/全正式同source/runが未達であることも不変更。

環境Ubuntu26.04/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/JaCoCo0.8.15/SpotBugs4.10.4、host空き約0.87GBを確認してprivate tmpfs fixture/768MiB Maven heapで実行。VM・原本/Backup・Currentへ接続/書込0、既native/旧failed/stash7削除0。実DB fixtureは試験がowned stop/closeし、Gitへdump/raw session/password/credentialを格納0。

実command/UTC/branch/source/exit/環境/旧証跡hash・XML/static/exec/Class byte資格は私有`PG379/pg1409-batch-boundary-selected-v1/manifest.safe.json` SHA6fe5deb4c97ec31066fd4eac6091ddc8323acbb30478255c46a241c5c6ff981b、最新選択/20assert/counter/XMLは`PG379/pg1411-latest-closing-counter-v1/manifest.safe.json`へ記録。公開manifestはhash/count/固定fixture期待値だけ。別source全回帰成功へ加算0、旧3569全体と新selected24（うち新3method）を新全体3572成功とは表示しない。

残はBootstrap合法Inspector1L1M、API22L2M/0B、Batch873L173M12C719B、Log/replay/故障競合・残CHR/QA051最終比較・451/trace/引継ぎ。二classの技術counter閉鎖をWBS親leaf全受入へ加点0。
