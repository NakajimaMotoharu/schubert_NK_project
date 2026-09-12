# NK-DAT-001 質問・通知照会Inbox 実行結果

2026-09-12 最新確定: dev-foundation/source e5d64a192c4274e7da3fe550b464a01c24836ec0、正式PT-WEB-20260912-06（23:18:07～23:25:41 JST）、全1161件（Protocol80/Storage58/API634/Web241/Batch107/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/runの2 method限定静的レビューを記録しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと18負canary成功。DB26部品240＋batch3部品37＋OPS11部品94＝40部分成果371 PT（全1161の内数）。今回は停止照会の取得済みstream所有/各getter null・runtimeを追加しBUG157/YKT122を全対象再試験で完了、試験method件数は水増しせず不変。R002環境file範囲は確定、親実子制御/backup artifact/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。PG156のimmutable run/activation/completionはSS/8PT仕様のみで未合格。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残85%でPG/PT継続中、元dev-web3file保全。以下は履歴。

最新探索5: 2026-09-09 15:45:25 JST終了、31.200秒、exit0。PROCESSING候補外も追加、新8＋旧SQL8全成功。017の1件・019の6件も成功（28stage/112異常binding・8query Test ID負canary）。source固定後の全module正式回帰/coverage/解析/収集はこれからであり、まだ正式合格ではない。

PG-D-139/041/PT-DB-INBOX-161～168。探索4（2026-09-09 15:43:20 JST終了、30.258秒）は新8件＋既存SQL8件全成功。Protocol FieldCodec/StorageAttributeの依存module選択試験も成功。これはselected testで全module coverage/static gateは未判定。V015/Java4route/独立goldenとSQL・並行・故障PTをPGと並行実装した。正式証跡/source固定後に更新、未合格分を工程へ加点しない。BUG-014/YKT-012/SSC-049は3更新参照・main/OS/実backup等を残す。

探索command: 421のJAVA_HOME/ローカルm2を指定し `./mvnw -o --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=QuestionQueryInboxCleanupTest,InboxMaintenanceBoundaryTest,FieldCodecTest,StorageAttributeGuardTest test`。全試験無指定の探索2は全APIを実行、旧route oracle等で非合格。探索1の選択filterは依存moduleが0件となりfailIfNoTests gateが拒否した。gateを無効化せず、各依存moduleも明示選択した探索3/4へ切り替え、これを正式全体実施として扱わない。

BUG-113は誤public factory、114/117/119はfixture権限・ID/schema/roleを実DDLに整合、115/116は追加scope/routeの旧期待を承認SSへ反映。118はDDL23514拒否と公開JDBC投影のJava保護を分離、owner変更はid7限定・3synthetic tokenは異なる値にした。120はSS351の5固定Error code正系/未知負系を独立実行。Production権限/制約/enumを緩めていない。YKT-099/100は全8fixtureと旧28route matrixを再確認し、正式全回帰まで完了にはしない。

SQL V015はV010本体と4route文字列以外byte一致をPT168で検証し、既存guard/WHERE matrix PT049～056も全28routeへ横断。24h±1μs/strict cutoffはliteral期待map、5roleと専用role本文拒否、行lock/backup欠落・失敗、delete後/commit前・後不明/resource closeのrollback/再走を確認。100並行inspect、混在11行は5件時3削除/2保護、最終11/4/7/END、同run再読不変。証跡にはraw key/context/wire/token/暗号包絡/DB dumpを保存しない。
