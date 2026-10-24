# 1742 Web四Recorder 実Prometheus SDK 実行結果・追跡

NK-OPS-001／WBS-P018-09・C07／RD171 MON005010013・UI252・SS311/333/351／1741／PG-D585。群1968、開始見積3/5/9pp・群上限10ppは変更しない。

## 結論・対象

製品Java/POMのsourceは **e196d0816c8a4920696d4f601f8b4cf97e9e8b48** のまま。当四Recorderの新しい実SDK試験8件と、必要な既存42件は、是正後の一JVMで **50件/7suite・全成功、F/E/S/aborted0**。宣言した四Recorderと直接契約の実15classは、この一execで **line288/288、method71/71、class15/15、branch117/117**。CRC不一致0・session1・旧counter合算0。全Web25classや全451の合格ではない。

実PrometheusMeterRegistry1.17.1/client1.7.0上で、固定5family/49sample、NaNと実0、正規counter suffix、独立1..36の合計666、二Long.MAX_VALUEのdouble累積、64×7=448、caller所有・部分登録例外・二owner独立・STANDARD未登録を確認。expectedは1741とTest sourceの固定値、Production methodで生成しない。HTTP scrape、server、Timer、DB/実pool/JMX/collectorやVMを動かした結果ではない。

## 元job・是正と独立検査

|証跡|実際の結果|manifest SHA256|
|---|---|---|
|PG8178-web-prometheus-gauge-host-v1|初回50起動49成功1失敗、終了1。新8は成功だが全体不合格|0fff1080331e7848d2f1a5da8028c0fa1d8dbb1dc37a090d8cc19d96530b50de|
|PG8182-web-prometheus-gauge-host-v1|是正後50/7全成功、compile/JVM終了0|8b3954cbcab6572f96ea8e6d0c0cba605417f80de9f49d907825f24ca945ba0c|
|PG8184-web-prometheus-gauge-post-v1|元XML/byte/全15四counter・単一exec独立検査、終了0|42c93ba67c719e30cdb102503e4f8d2153a57da150c0bd0b90b5afbb958cb4f1|

公開manifestは各 `evidence/provisional/<上記ID>/manifest.json`、own元log/XML/exec/開始・PID・終了receiptは `/home/mini/codex/project1/work/pgpt-runs/PG379/pg8178-web-prometheus-gauge-host-v1`、同 `pg8182-web-prometheus-gauge-host-v1`、同 `pg8184-web-prometheus-gauge-post-v1`。manifestに全実command/input/hash/source/OS・時刻・actualExitを収録。元run/source/toolは保持し、再発行しない。

BUG1689/YKT1440は、fresh javac方式に独立route fixtureの同梱を落としたPT工具障害。初回source6246af085d07c11b7d3ce93b73c7cc92296ea55dを保持して先行起票、修正 **0567be8fd**。期待値・製品codeは変えず、元e196/current/copyのfixture SHA `1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331`を束縛。既六Test＋新Test全七sourceを検索し、resource参照はHttpMetricContractTestの一箇所だけと確認。他六は固定in-memory fixtureで非該当、旧8124はtarget/test-classesを含む正常経路で非該当。postはfixture欠落/改変を含む独立7metadata反例を拒否し、全対象確認・再発防止・再試験完了。製品MainのNPEと混同しない。限定CLOSED、完了日2026-10-24。

post実行byteは4051d8eca commitで保存。初回Pyflakesの未使用変数1件を実行後削除し、三Python工具の現sourceはPyflakes0。これは未使用binding除去だけで元coverage/XML処理・期待値の変更なし、元postの実行byte/結果は保存したまま。修正前工具が静的0だったとは記載しない。新二Java helperは固定google-java-format1.36.1（skip-reflowing-long-strings）適用、実javac25/-Xlint:all/-Werror/-proc:noneで警告0。

## 同sourceと静的・生成契約の扱い

PG8122正常六compile証跡SHA `75ca9dd88ce045dc0acdbdd878e9382a30584a1da34fb8d37bc04d2ca4d4a53b` の全input/六Jar/正常実classpathと現在Production inputを当run前後に照合。新正常六compileを実施したとは称さず、既存の同製品byteに、新Test/helperをfresh compileして新SDKを載せた試験である。古いM2内部artifact/test-classesは使用せず、全15SDKの元8170/8173・現物hash、JSR305/JUnit/agentも束縛した。Production POMや配備BOMへ新SDKを導入した成果ではない。

当15class/5Main sourceはPG8126/8132と完全同byte。静的解析は元same-sourceの実raw16・個別理由を保持し、当5Main該当1件（HttpMetricContract.Routeのimmutable INDEX factory）を限定再結合。元CS/SB/processing/missing0と他15件の対象外program理由を隠さず、**今回新しい静的解析jobを実行したとは記載しない**。全10生成type/36methodも元byte・独立typed Testのsourceを照合して、当42件の真正実行へ追跡する。別sourceの成功や除外追加でcoverageを上げない。

当限定の実行例（repoルート、既slotへ再実行不可）:

```sh
env PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg8182_web_prometheus_gauge_host.py
env PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg8184_web_prometheus_gauge_post.py
```

子JVMはPATH/LANGだけの最小env、own空file/最初classpathの空prometheus.propertiesを明示し、実config/secretを読まない。SDK new registry/MockClock、HTTP/process/JMX binderなし、自己有限workerは各5秒上限とfinally停止。新SDK15Jarの同じhashを当run前後に確認。再現する場合も新環境/新only runへ、現slotやunknownjobの再実行は禁止。

## 計測と残件

今回新しい検証は8Test、必要既回帰42、是正手戻り1回、独立post1。製品新Main0・正式/原190の新個別受入0・工数率null。群開始19残81/reset1793382075に対し、直近API使用19残81/reset1793382076と1秒差を観測したため、同窓差分/専有費を推定しない。reset発生・予算再基底化とは扱わない。usage cursor48ade08b/11:01:47JSTは明示record0・完全性未証明、実N/Tはnull。元/v4/v5・群開始見積りは維持。

正式1964PT/53scope、QA051final/PTALT0、F03 Root11と実VM/Root/cohort/native/DB/Backup/鍵/intent/permit/配備等HOLDは維持。Timerのnative longsumやactual endpoint、mode切替、実BOM/daemon/容量/CHR・whole451は未受入で、当限定成功から外挿しない。次も後続成果索引で重複を避け、承認SS351に根拠のある独立PG/PTを選定して継続する。
