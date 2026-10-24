# 1756 HTTP CDF寿命是正 結果・横展開

NK-OPS-001/RD171/UI252/SS351/1755、PG-D593、WBS-P018-09主費用/C07共有参照0加算、group1982開始0.5/2/5pp・cap10固定。

## 増分と限定成果

新独立観点 **4件**（初回計画3＋発見是正に必要なatomic保存則1）、既必要28込み **32件/4suite** が修正source **f02fae44edbcf7abba214a6507935c15ae5f9ee9** で全成功。新規Mainを増やす工程ではなく、既HTTP provider一source/二classの累積CDF障害是正。旧3失敗、途中source32、別sourceのSummary58を足して現在の全体試験数にしない。

最大値maxの時間窓と、count/正double total/九有限CDFの一生涯を分離。private ReentrantLock下の一atomic stateを使い、delegate record/Clock/callbackは外、null/負数/全七単位/二Long.MAX_VALUE/境界/例外/借用寿命/close/無関係timer/partial factoryの既契約を保持する。global config/marker/SDK内部/SS/画面/処理結果/Current baselineは変更しない。現在sourceは未配備、actual runtime UNKNOWN/HOLD。

## 元証拠と原因（BUG1696/YKT1447）

PG8284は元source7cba・工具73fe10641、新HTTPCDF001～003が全3失敗/終了1。原manifest SHA **27bd965b2b2c9d78b14830284ebd6af0ed7b0da89da10a80f4d5f3fcc42c221c**。001は初期正CDF/count/sumを通過、3秒後max0を確認した後CDFで失敗。失敗期待値を実測へ変更しない。

PG8286 own memory scalar診断は終了0/PT0、原 **c22ff356d6b923b11f3e5a401fc8f5291d3666e51b2dbac4f1abbd0cf773c33a**。HTTP count1保持/CDF全1→全0を確認、delegateのtime-window histogramCountsをpublic snapshotへ転用していたのが原因。native helper Gaugeは前後1でpublic snapshotとは別の内部cache値、これをCDF代用にしない。診断のDB/MQ finiteCDF全1と、API helper欄の未測定literal0を区別し、後者はunknown/非実測として扱い成功根拠にしない。

|横展開対象|全対象の是正/非該当根拠・再発防止|
|---|---|
|HTTP public Timer count/totalTime/takeSnapshot/measure|修正f1a898b58でprivate lifetime stateへ、追加並行保存則004。さらにf02fae44eでvalidation/delegateとlock状態操作を分離。同じ独立vectorsと既全七単位/境界/null/負数/callback例外/二MAX・count/mean/measure/借用/closeを32件で再試験|
|HTTP max/registry fallback/auxiliary factory|既delegate窓維持・unknown timerは従来SDK、012/005/010/011と新001～003を同sourceで確認。helpersをremove/rebindせず、部分factory例外やownerを改変しない|
|native helper Gauge/全Production consumer|source検索でHTTP public snapshotのhistogramCounts転用が唯一の同原因。native GaugeはSS public familyではなく別suffix/cache。新formatterは承認名の選択した型のsnapshotを使い、helper Gaugeをpublic familyへ昇格しない。新Timer encoder/実endpointは後続未実装として保持|
|API DB/MQ ExactDuration/二histogram|同sourceでprivate atomic long CDFを自前保持し、Clock/TimeWindowを使用しない。1754/8272のexDur008がclock読取禁止でも観測保持を検証済み、source/全Jar byteは8302で不変。8286 own snapshotは補助観測でPT成功の代替ではない。新sourceへ旧coverageを合算しない|

## 実行・品質

公開manifestは evidence/01_PT/018_NK-OPS-001/evidence/provisional/、元command/input/XML/log/exec/終了receiptは /home/mini/codex/project1/work/pgpt-runs/PG379 の同小文字slotに保全。JDK25.0.4/Maven3.9.12/offline、clean own environment/明示emptySDK設定、独立route fixture SHA **1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331** を元snapshot/現在source/fresh classpathに束縛。

|段階|確認結果・manifest SHA256|
|---|---|
|PG8296-http-cdf-six-compile-v1|新source正常六build/NullAway/Spotless成功、PT0/UNRUN。**51309cd76e4e5d2c3822813dba8e1e75a944f895769767831e7325f00908b8bd**|
|PG8298-http-cdf-fixed-host-v1|新4＋既factory12/Recorder10/Contract6＝真正32/4、F/E/skipped/aborted0、新一exec。**e69c0ed6965ce7bab662778764182f9bac747b957541cb2d2b74d40576a982b9**|
|PG8300-http-cdf-fixed-post-v1|当変更2classのline69/method21/class2/branch20、**全miss0/100%**、CRC0/一session・union0。PMD/Checkstyle/SpotBugs/missing各0、空markerはfields/methods/init0を明示証明、独立fixture/七receipt反例拒否。**7e694a9407761514a925e00ddfb823619c40ba4aa679127335063f716ae5e35e**|
|PG8302-http-cdf-six-trace-v1|全1801physical/原1669byte不変、変更inner＋outer debug/line tableの2だけ（他1799完全同byte）、src差分一source/全159owner、五architecture0・target init0。**0eb09bf4e6da405733ad99eb9c81084450c5f55ca1acfe4dec83f55db59565fb**|

実commandは既PYTHONPATHの python3 -B tools/quality/pg8296_http_cdf_six_compile.py → pg8298_http_cdf_fixed_host.py → pg8300_http_cdf_fixed_post.py → pg8302_http_cdf_six_trace.py。全て新only、既jobを再実行せず元receiptを読む。全source/current/archive/deps/fixture/byte/対象Test IDを上記manifestへ対応させた。実VM/DB/network target/service/Root/Browser/Backup/鍵等0-HOLD。

途中source f1a：PG8288正常六原302163c1、8290の32/4成功原ea4d0449、8292は四100（68/19/2/20）・PMD/CS0到達後SB CWO_CLOSED_WITHOUT_OPENED二件で拒否。各lock取得後try/finallyのコードを無視/抑制せず、validationと純状態lock helperを分離する同値構造へ是正した。途中post未合格はPG8293原 **fc19de437ca31d719e5535ebf95c3051599c5fda11abf3d6e3ca01bc28418b32** へ全元hash/五step終了を保存。必要な変更source再認証費で、確認だけの原4222/common44再演は0。

BUG1696/YKT1447は本限定範囲の全対象是正/非該当と同source再試験/静的/traceを結合しCLOSED、完了日2026-10-24。実Root/他障害/未特定拒否操作を閉鎖しない。

## 計測と後続

fresh24残76/reset1793382075、開始23との差は丸め共有1pp、専有費とはしない。元計画新3、追加発見の保存則1、障害是正、静的手戻り/変更source再認証/工具metadata解釈を別記録。usage be63da9a/13:41:35JST、明示record0/完全性未証明・N/T/工数null。元-v4-v5/開始0.5-2-5の減額/再基底化0。

次は公開scan/保存/push→別fresh bounded群でHTTP Timer＋counterを標準textへ接続する実PG/PT。Summary encoderの既58を確認だけで再演せず、共通部分を変更する場合にだけ必要同source検証を追加する。実endpoint/owner/source/CHR/native/全scope同runの451は未受入、正式1964-53/原190新受入0・QA051final/PTALT0/全actual HOLD不変。小区切りで全体停止せず継続する。
