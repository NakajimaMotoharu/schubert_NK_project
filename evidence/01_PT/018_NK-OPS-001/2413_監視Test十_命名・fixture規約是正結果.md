# 監視Test十・命名/fixture規約是正結果

仕様2412/PG-D773/event2777、source42ae92a74d57a9e1d031613d5b558af3ebe2925c（Main不変更/十Testのみ、未配備）。BUG2023 private AT/at衝突十件・BUG2024 DEBUG fixture重複一件を修正前起票、元十source全文・全31原findingと81catalogを13070へ不変更保存。変更はAT identifierだけOBSERVED_AT、Transferの元11個のDEBUG String tokenだけprivate DEBUG_MODE_FIXTUREへ抽出。全元token逆と非同値52反例で、元time/input/assertion/期待/at factory/worker方式不変更を確認した。新Test ID0、下記81は是正影響再試験である。

## 実行・保存根拠

各entryを `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/<entry>.py` で実行、初回bind前pyflakes0。JDK25.0.4/Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15、実時刻・OS・branch/source・command/終了・全SDK/工具SHAは各manifest begin/invocationを正とする。公開provisional配下のmanifest.jsonは次のとおり。

| Run | SHA256 | 結果 |
| --- | --- | --- |
| PG13070-monitor-test-originals-v1 | faa795bf1bc06a56b4a926f48fdda20b60e7b8da7d0672439e0ab479628c598f | 原全文/同SHA/31finding/81catalog保存、製品PT0 |
| PG13072-monitor-test-preflight-v1 | 5d2af644b9565963525135f234de8f2f53de92f9bf991cfde721d9905931763e | token逆/52反例・20worker raw/CS0、gate1保持 |
| PG13074-monitor-test-plan-v1 | 26c3c4fd22d61e6bd8dc26ddbf4c47baee7b98c3963352123a0fac1d80f88a09 | 元whole81/十suite・Main十九閉集合固定 |
| PG13076-monitor-test-six-compile-v1 | 77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932 | normal六jar/NullAway/format/compiler0、製品PT0 |
| PG13078-monitor-test-host-v1 | 28f76d37bfd46dd38535f7418aafc31046fa3e40697956d85d9951d537cbdd6d | 81/10真正0・FES-aborted/container失敗0、一exec PG13078-MONITORNAME-JP |
| PG13080-monitor-test-static-v1 | 8dd2ba543269195d0e4479ea48e8a55cfb846acac98c3d413dc3b56729ad8732 | 変更Test十PMD20・CS0・六SB0、PMD本体4/aggregate1保持・timeout0 |
| PG13082-monitor-test-post-v1 | 911c0f6768b0672873c942d4d2a9e7e89c92c18f4a16d39ee9b4515ed4a44fcc | 同XML/session/CRC/全artifact・全Main不変/十outer＋一nested debug差 |
| PG13084-monitor-test-context-v1 | 172f097d528028d906b5e012a43d413b067f5b0e4c360c8ce2163c0032328125 | 原十一実是正・20workerの全attributes再束縛 |
| PG13085-monitor-test-context-post-v1 | fef9161cc2128717dadbcc1b131920e37c49128e07dd4aeb22aa52e288a60d63 | 九誤計上反例・raw/gate未達保持 |
| PG13086-monitor-test-trace-v1 | b816f79093abd3ca919909e236448cd5543e92ed824df302c82f4c7920870547 | 既992rowの十SHAだけ/他982全field/全owner-cost不変 |
| PG13087-monitor-test-trace-post-v1 | f4916614816f5af487cc4cccd55158d5cb6b4e9b41614becbd3f484033c89d25 | 八反例・485/486原semantic/全担当費/旧runtime保持 |

## 当sourceのcounter（各class合計、covered / missed）

| Monitor sourceとその内部型 | line | method | class | branch |
| --- | ---: | ---: | ---: | ---: |
| AsyncQueueMonitor | 24/0 | 6/0 | 3/0 | 16/0 |
| BackupHealthMonitor | 22/0 | 6/0 | 3/0 | 12/0 |
| DlqHealthMonitor | 22/0 | 6/0 | 3/0 | 14/0 |
| ExpiryBacklogMonitor | 17/0 | 5/0 | 2/0 | 6/0 |
| IntegrityHealthMonitor | 17/0 | 5/0 | 2/0 | 6/0 |
| RestartHealthMonitor | 19/0 | 5/0 | 2/0 | 12/0 |
| TimedDbPoolMonitor | 34/0 | 4/0 | 2/0 | 18/0 |
| TimedSyncLatencyMonitor | 39/0 | 4/0 | 2/0 | 20/0 |
| TransferHealthMonitor | 27/0 | 7/0 | 2/0 | 6/0 |
| WebLogBacklogMonitor | 18/0 | 5/0 | 2/0 | 12/0 |

十source所属23 Main classは適用四counter各100%、class集計239L/53M/23C/122B miss0。line集計はclass別counterの合計でsource行のunique和ではない。既定enum/record filterだけ、手動除外0。これは新規23classの初達成件数ではなく、修正したTestの新sourceでの局所再確認である。Main十九sourceに対応する44class全体では未使用clock/observeNow等の未達を保持しselectedMainCoverage100=false。全Batch artifactはline532/17885・method122/3083・class41/372・branch273/8185で未達、他五artifactも完全分母のまま保存し全451100を宣言しない。

全1843Main class同byte・Test全1972集合不変。十outer Testに加え、TransferHealthMonitorTest$Registry一つは追加定数行によるline/debug移動だけ、model/flags/field数/method署名/raw Code表現は同じ。CodeのCP indexだけを意味同一の証明とせず、元全token逆とnested body不変更を併せ根拠にする。残1961Test classは同byte、新physical0。全source/SDK/工具・唯一classpath定義・実Testclass pre/post同hash、全81XML・一exec CRC/全artifactaccount・own CWD空・closure外Product probe0。MonitoringObservationClock全methodとMonitoringPoller.observeNowは未使用0、実sampling/DB/JMS/FS/HTTP/Backup/Root/VM/native/Graph9/鍵操作0、既成功exec合成0。

## 障害・残件・計測

BUG2023/2024・YKT1771/1772は全十/DEBUG十一tokenを逆/52反例・当源81・static/独立postまで確認して当規約scope限定完了、完了日2026-10-28。修正source42ae92a74、証拠は上表、保存pushは456参照。既worker20は属性/順序/元messageまで一対一照合して保持、invokeAllとTWR closeには局所timeoutが無く専用JVM240が外側上限であるという限界を明記し、通常container Thread許可や全F03免除へ変換しない。

原raw8472→8461（Main1504不変/Test6968→6957）、既是正953→964（本群11は全Test）。参照3259は不変、既worker20のcurrent再束縛でpending941→961、未参照5213→5202、introduced16不変・actualViolationCountnull。全global再解析0、原source同SHAと変更token閉集合・current局所PMDの原十一消失を根拠にderivedを更新した。registry992/Java1819登録1817/UNKNOWN二不変、全WBS auditはactual1/HOLDを維持、正式1964PT/53scope・歴史17/190・新個別受入0・工数null/QA051final/実経路HOLD不変更。

bind済み工具/製品失敗・追加source再認証cycle0。原2/5/9cap10・旧窓開始86/reset1793599188から新窓0→1/reset1793774153へ移行、旧窓終端消費は未観測なので窓間/全群差を捏造しない。こちらからreset操作/券/課金0・変更原因UNKNOWN、実N/T/専有費null、元/v3/v4/v5予測不変更。新窓の次点検used5・残10以下新規停止を維持し通常群/保存/PMO待ちで停止しない。Program018のevidence/monitor-test-name-regression/manifest.jsonに既81 IDと当source/run/文書hashを結合する。
