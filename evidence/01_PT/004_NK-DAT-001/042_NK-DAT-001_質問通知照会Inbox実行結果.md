# NK-DAT-001 質問・通知照会Inbox 実行結果

2026-09-09 最新確定: dev-foundation/source3cac4ede9bffd328adada4078f7207494c0b7e8f、正式PT-WEB-20260909-47（21:30:23～21:37:30 JST）、全1111件（Protocol80/Storage50/API634/Web241/Batch65/CHR41）PASS、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのSpotBugs未解決0/NullAway・Enforcer・Spotless PASS。固定/run移植性指摘1件のmethod/ID限定レビューを明示（BUG142/005）、coverage除外なし、CHR runnerのSpotBugsは未設定。12collector・35証跡scopeの同run/source/branch/hash/参照、017の1件・019の16件負canary成功。DB26部品240 PT＋batch3部品37 PT＋OPS6部品44 PT＝35部分成果321件確定（全1111件の内数）。PG-D-150の同期DBロック引渡し8 PTを追加、BUG146/YKT114の資源取得2箇所修正・既存13資源境界の非該当根拠と全体再試験を確認。親制御/実backup artifact/設定publish/固定run永続化SSC055・全cleanup caller・通常Question writer/replay・Logout RERUN-001は未完了（460参照）。実root/systemd配布等は後続Linux IT/STで別確認し、未実装Productionを後工程へ移して完了にしない。QA045はLogin title差分の未回答でLogoutとは別。BUG-014/UIC-006/SSC-049/052継続、加重見積約4割（35～50%、456）を維持。週間残8%、新規大規模作業なし・中断準備。元dev-web Scenario3file保全・不算入。CHR41はrunner PTで実NK互換gateではない。以下は履歴。

最新探索5: 2026-09-09 15:45:25 JST終了、31.200秒、exit0。PROCESSING候補外も追加、新8＋旧SQL8全成功。017の1件・019の6件も成功（28stage/112異常binding・8query Test ID負canary）。source固定後の全module正式回帰/coverage/解析/収集はこれからであり、まだ正式合格ではない。

PG-D-139/041/PT-DB-INBOX-161～168。探索4（2026-09-09 15:43:20 JST終了、30.258秒）は新8件＋既存SQL8件全成功。Protocol FieldCodec/StorageAttributeの依存module選択試験も成功。これはselected testで全module coverage/static gateは未判定。V015/Java4route/独立goldenとSQL・並行・故障PTをPGと並行実装した。正式証跡/source固定後に更新、未合格分を工程へ加点しない。BUG-014/YKT-012/SSC-049は3更新参照・main/OS/実backup等を残す。

探索command: 421のJAVA_HOME/ローカルm2を指定し `./mvnw -o --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=QuestionQueryInboxCleanupTest,InboxMaintenanceBoundaryTest,FieldCodecTest,StorageAttributeGuardTest test`。全試験無指定の探索2は全APIを実行、旧route oracle等で非合格。探索1の選択filterは依存moduleが0件となりfailIfNoTests gateが拒否した。gateを無効化せず、各依存moduleも明示選択した探索3/4へ切り替え、これを正式全体実施として扱わない。

BUG-113は誤public factory、114/117/119はfixture権限・ID/schema/roleを実DDLに整合、115/116は追加scope/routeの旧期待を承認SSへ反映。118はDDL23514拒否と公開JDBC投影のJava保護を分離、owner変更はid7限定・3synthetic tokenは異なる値にした。120はSS351の5固定Error code正系/未知負系を独立実行。Production権限/制約/enumを緩めていない。YKT-099/100は全8fixtureと旧28route matrixを再確認し、正式全回帰まで完了にはしない。

SQL V015はV010本体と4route文字列以外byte一致をPT168で検証し、既存guard/WHERE matrix PT049～056も全28routeへ横断。24h±1μs/strict cutoffはliteral期待map、5roleと専用role本文拒否、行lock/backup欠落・失敗、delete後/commit前・後不明/resource closeのrollback/再走を確認。100並行inspect、混在11行は5件時3削除/2保護、最終11/4/7/END、同run再読不変。証跡にはraw key/context/wire/token/暗号包絡/DB dumpを保存しない。
