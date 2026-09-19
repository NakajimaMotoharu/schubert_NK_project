# NK-DAT-001 質問・通知照会Inbox 実行結果

2026-09-20 最新確定: dev-foundation/source53c2f7bf8fc6bb45851cd088a78e8f9c590fc45b、正式PT-WEB-20260920-07（03:37:38～03:49:28 JST、Maven11:48/exit0）、全1495件（Protocol80/Storage82/API684/Web241/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。16collector/39scope整合・53負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＝73部分成果705PT（全1495の内数）、今回再開比+80PT/+8部分成果。PG189質問入力境界を認定、BUG211/YKT167・SSC070限定完了。PG190空回答providerは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、残量62%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

最新探索5: 2026-09-09 15:45:25 JST終了、31.200秒、exit0。PROCESSING候補外も追加、新8＋旧SQL8全成功。017の1件・019の6件も成功（28stage/112異常binding・8query Test ID負canary）。source固定後の全module正式回帰/coverage/解析/収集はこれからであり、まだ正式合格ではない。

PG-D-139/041/PT-DB-INBOX-161～168。探索4（2026-09-09 15:43:20 JST終了、30.258秒）は新8件＋既存SQL8件全成功。Protocol FieldCodec/StorageAttributeの依存module選択試験も成功。これはselected testで全module coverage/static gateは未判定。V015/Java4route/独立goldenとSQL・並行・故障PTをPGと並行実装した。正式証跡/source固定後に更新、未合格分を工程へ加点しない。BUG-014/YKT-012/SSC-049は3更新参照・main/OS/実backup等を残す。

探索command: 421のJAVA_HOME/ローカルm2を指定し `./mvnw -o --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=QuestionQueryInboxCleanupTest,InboxMaintenanceBoundaryTest,FieldCodecTest,StorageAttributeGuardTest test`。全試験無指定の探索2は全APIを実行、旧route oracle等で非合格。探索1の選択filterは依存moduleが0件となりfailIfNoTests gateが拒否した。gateを無効化せず、各依存moduleも明示選択した探索3/4へ切り替え、これを正式全体実施として扱わない。

BUG-113は誤public factory、114/117/119はfixture権限・ID/schema/roleを実DDLに整合、115/116は追加scope/routeの旧期待を承認SSへ反映。118はDDL23514拒否と公開JDBC投影のJava保護を分離、owner変更はid7限定・3synthetic tokenは異なる値にした。120はSS351の5固定Error code正系/未知負系を独立実行。Production権限/制約/enumを緩めていない。YKT-099/100は全8fixtureと旧28route matrixを再確認し、正式全回帰まで完了にはしない。

SQL V015はV010本体と4route文字列以外byte一致をPT168で検証し、既存guard/WHERE matrix PT049～056も全28routeへ横断。24h±1μs/strict cutoffはliteral期待map、5roleと専用role本文拒否、行lock/backup欠落・失敗、delete後/commit前・後不明/resource closeのrollback/再走を確認。100並行inspect、混在11行は5件時3削除/2保護、最終11/4/7/END、同run再読不変。証跡にはraw key/context/wire/token/暗号包絡/DB dumpを保存しない。
