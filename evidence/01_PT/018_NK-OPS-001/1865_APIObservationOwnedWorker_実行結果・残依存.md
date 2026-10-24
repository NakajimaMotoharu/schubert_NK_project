# API観測owned worker・限定実行結果

2026-10-25/1864/PG-D635/group2096、Production `fdc229c9a7b7759cea106d1126c8da0f27a70e09` 未配備。開始4/7/10pp/cap10固定、fresh55残45→07:57:24 fresh56残44/reset1793382075、観測共有差1/専有費・他chat内訳null、N/T/工数null。直前54→55の群外境界1を付替えず、元/v4/v5を変更しない。usage abe482072991dc539c794574d7449ac4f9abf34a9b0fe307514d841572c2de80（未記録をtoken0/費用0としない）。

| 正本manifest（evidence/provisional配下） | SHA256 | 限定結果 |
|---|---|---|
| PG9132-api-observation-worker-six-compile-v4/manifest.json | e0ffc872d61a2eb6b4556de13eabcd0173e957ed9b832d2df29088f6308e4ac1 | normal六module/exit0/Compiler-NullAway-format等、PT0 |
| PG9134-api-observation-worker-host-v2/manifest.json | af479ed66e9be54b36e76ef70da64f1180ce4321336deb9f6d8605b0420e1cb6 | actual44/1suite、OBSOWN001～044、F/E/S/aborted/not-run0 |
| PG9133-api-observation-worker-static-v2/manifest.json | 9d844d3632a1dda9d9fcad0d36e1303a37786faefe1a786f431efbcedcef2832 | raw static1/PMD20-exit4、CS-SB0、元raw報告を保存 |
| PG9135-api-observation-worker-context-v1/manifest.json | c1be834044f886aaf6f92ce619da09f1e9a3c00923afa8cd387b105b3415b44b | 全20行を現source/全XML/vendor/formal designへ結合・未分類0/抑制0 |
| PG9136-api-observation-worker-post-v1/manifest.json | 24632ab8560ae2cf33785fff6868987375fb6e8d2a1de4e9cd8e7a9fdf0b3a12 | 全一Main L87 M7 C1 B46未網羅0/CRC0-session1、7receipt反例 |
| PG9137-worker-boundary-canaries-v2/manifest.json | 7cdbc517b96c3b00874121af6be266b0c94c34e79ad3c628e5ad002f746164a4 | 独立compiler三canary(0/1/1)・long6vectors・metadata12反例、製品PT0 |
| PG9138-api-observation-worker-trace-v1/manifest.json | 68dd79441376d60e705e0856e3e0077c59a40f7f76c6d9cace1b0e5045c10d37 | 全1841Main・旧1840同byte/244canonical owner/五arch0/15metadata反例、旧42Test＋共通fixture完全保持 |

各44件の入力/期待/独立根拠は1864個別表と同名Testのliteral、実際値/元XML・log/exec・1session・JDK25.0.4/OS/入力hash・実command/終了codeは元host/runに一意対応する。私有JVM Threadとfake JDBC/Clock/starter/Semaphoreだけを使用、全fixtureで私有Threadを回収し、UNKNOWN ownerのawaitを虚偽の正常に変更しない。元helper用Test outer四つはcompile-onlyで成功加点0。source固定、完全PYTHONPATH＋先行pyflakes0＋set-e、各new-only工具の成功確認再演0。実VM/Root/App Main/DB/native/既存サービスを起動・停止しない。

PMD20はDoNotUseThreads10（vendor J2EE/container管理thread前提がstandalone API jar/正式SS342/実Unit direct Javaに非該当）、native failure保持/rethrow8、private start claim lock1、自己Threadのexact reference identity1。現正式main8b91944df/SS SHA3775cb1f、vendor7.28.0 SHA068b2b5f、当source/span・全44の入力/後条件へ一行ずつ結合し、raw0/一律rule許容/旧PT転用としない。CS/SBは実0、context/全class四100は部品資格だけで全F03/451を合格にしない。

## 障害・横展開の限定閉鎖

| BUG/YKT | 原失敗・原因 | 修正/全対象確認・追加check |
|---|---|---|
| 1732/1483 | source3524cbbe0、9132v1原8c662000901fabaae5858ce62063c0daa61fd4f1f9162039314f6e7b4983316e、testCompile serial警告二/exit1/PT0 | e155e239a548ed1b99cfe42710cbf6da2056e1a2でCountDownLatch/Runnable fieldだけtransient。三role同Semaphore/Serializable fixtureは当Signalのみ、他五fieldはserializable型。9137v2が正0/各transient欠落1の実compiler3canaryと元型/七field・二modifier順を確認。新normalは全testCompile warning0/当44成功、Main変更をこの修正へ付替え0。 |
| 1733/1484 | e155/9132v2原7bb40d8e356d786af39cca5e28d53cf5371c0cd75a4e519ef8cba8069931325d normal0/PT0。初回Long.MIN_VALUEからelapsed減算でMAXへwrapし得るcode review発見（未実行を失敗/合格にしない） | ecd3fd0e6a060744e4a2dc50fb84fb1abd27c5fbで初回<=0を時計/減算前拒否。024の-1/MIN→後続MAXは初回一読・clock未読、025/026で増大/逆行拒否。9137v2独立Java long vector/元source拒否・境界反例。三role同型stop予算は当workerのみ、pumpは正intervalを先行検査したsampling差分で非該当、元32再演0/旧Main全byte保持。 |
| 1734/1485 | ecd3/9132v3原9417e029957a0dd733db61ad1efa639d837fda32701865badf269b2a70bae935 normal0→9134v1原49a6e01ff9b674148bda7d5da4b0d5bb6ff9544436e047ad7c9fdc9bbaf60b25 actual44成功→9133v1原75b2382872ab79eefc69cc182911f11bd59d6737cef7b334573655f935be18a1 static1/SB2。timed wait falseを捨て終端再観測で正常化し得た | fdc229c9a7b7759cea106d1126c8da0f27a70e09でSemaphore通知はstop必須、latch/join falseは直ちに永久UNKNOWN。SB未警告のjoinも同causeで是正、三role monitoringの同待機三箇所すべて当worker。025を2ms-1ms=残1ms一回wait→timeout/clock-budget各2読の独立oracleへ根拠訂正、042へstopなし通知vector。9138が他42ケース/共通fixture完全保持と15metadata反例を実証。新44とSB0/全87-7-1-46四100で再資格。 |
| 1735/1486 | 9137原driver SHA1863438ea6934522cf479d6f0336712c5b58f5694c68e8a2323846bcb081f4ca、modifier順を文字列固定しAssertionError1・SLOT/子compile前。原script/失敗manifestを保存 | 未資格v1を変更せず新v2でfield名＋transient token集合を使い、transient volatile/volatile transient両形式の正例と各欠落を拒否。compiler3/算術6/metadata12を新出力で確認、製品44の確認再演0。他当群negative generatorは実source変更assert＋対象token/schemaに結合。工具修正は本1865保存commit、Productionの修正と区別。 |

全4件・全対象/非該当/再発防止が上記証跡で揃った当範囲だけ2026-10-25 CLOSED、検索だけ閉鎖0。原失敗・中間source/44は保存し新sourceへ合算0。四normalのうちv1失敗1、v2/v3/v4成功、v1/v2はPT未実行、選択44はv3/v4各一回=88実行でも新Test IDは44だけ。工具canary/metadataを製品PT PASSや実測coverageへ混ぜない。

## 残依存

actual API caller/既Pool・Manager/SDK・既残期限の接続、実API start/owned stop・VM/Root/DB/native・CHR・全source四100・451/全trace・G07未分類8379/QA051finalは未受入HOLD。次は同経路caller接続の承認済みsource/所有/deadline依存を限定し、許可されたassembly PG/PTへ進める。実ownerの保持policyは未確認release時に同frameを維持し、私有Thread回収・quiescenceを実資源解放へ読み替えない。

技術新44ID/一Main、累計812ID/40Main/config静的5は異sourceの部品測定。正式1964PT/53scope・原190新受入0/工数nullを維持し、PG/PT全体・IT/ST完了を宣言しない。通常報告・commit/pushでは停止しない。
