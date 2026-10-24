# 1755 HTTP histogram CDF寿命・独立追加PT

NK-OPS-001/RD171/UI252/SS351/1725/1752/1754、WBS-P018-09/C07、group1982。開始0.5/2/5pp・cap10、候補Main source7cba540ba同byte/正常8270を参照する。後続索引は1752/1751/1725、元httpDur005はmax/count/sumの窓経過だけでCDF未検証。この新三観点は確認だけの元12再演ではない。

|Test ID|fixture/操作|独立期待値|
|---|---|---|
|HTTPCDF001|MockClock、expiry1秒/buffer2、供給ns=0/1/50000000/50000001/5000000000/Long.MAX_VALUE二件。3秒進め再snapshot→1ns追加→100日進め再snapshot|count7、有限9CDF=3/4/4/4/4/4/4/4/5、3秒後も同値でmax0。追加後count8/CDF4/5/5/5/5/5/5/5/6、100日後も同値。sumは独立BigDecimalの整数ns加算/1e9、binary64全範囲の固定8µs誤差内、Production出力をexpectedへ使わない|
|HTTPCDF002|同MockClock・別registry二owner、A50ms/B5秒、3秒経過後Aだけ50ms+1ns追加|A/BのfiniteCDFを別literalで保持、maxだけ0へ、別ownerへ増分漏れなし。sourceをexport操作でcloseしない|
|HTTPCDF003|own4worker・64供給イベント各1ns、有限Future待機/cleanup後3秒・さらに3秒経過|count64/全9CDF64/sum64ns/max0を両時点で維持。実thread timingをlatency oracleにしない|

すべてordinary memory SDK PT、実HTTP/Browser/DB/JMS/VM/Root/時計OS変更なし。bucketは秒のSS九境界に対応するliteral ns、cumulative countの寿命は窓maxと区別する。元SDK bytecodeだけから成功と推定しない。

## 失敗後の内部PG判断・追加観点（開始見積り不変更）

BUG1696/YKT1447を修正前起票。8284新三件全失敗、8286原c22ff356のown診断でHTTP public snapshotのCDFが全1→全0、count1保持を確認。native helper Gaugeは前後1（cache等の内部値でpublic snapshotと異なる）、これをpublic familyのCDF代用にしない。API DB/MQの診断finiteCDFは全1、API nativeHelper欄0は引数literalの未測定placeholderでありGauge実測ではない。この欄からAPI Gauge0の成功/異常を推定しない。APIの時計非依存は既同byte exDur008/source/8272を根拠に区別する。

PG-D593：HTTP wrapperがprivate ReentrantLockでlong count/九有限CDF/正double totalを一atomic観測として所有し、maxのみ既native窓へ委譲する。delegate record/clock/snapshotをlock外、callback/単位/負入力/close/未知timer/既partial factory契約を保持する。SDK内部/marker/SSを変更せず、cached helper Gaugeを削除・再配線せず、明示選択するpublic Timer familyのsnapshotを是正する。

追加HTTPCDF004は4×256 supplied1nsと並行snapshotの独立恒等式（count−各CDF=0、totalNs−count=0）/最終count1024・全CDF1024を検証する。expectedはliteral0/1024でProductionから生成せず、スケジュール依存の途中countをgoldenにしない。修正後は既factory12＋新4＋必要HttpMetricRecorder8/HttpMetricContract5=29/4を予定、実一覧を実行前照合して凍結する。全changed2class四100/static/全physical traceが完了するまで障害OPEN。

実行前最新一覧でRecorderは010まで10/Contractは006まで6と確認、旧仮8/5を訂正し**32/4**に確定（12＋4＋10＋6）。まだ実行していないので成功加算ではない。両caller Testの独立resource `/monitoring/http-route-labels.txt` は現source/正常snapshot/fixture既SHA1777c471へ束縛してfresh classpathへcopyする。

是正途中f1a source：8288正常six成功、8290真正32/4全成功（原ea4d0449）、8292当2四100到達（L68/M19/C2/B20）/PMD-CS0後、SB CWO_CLOSED_WITHOUT_OPENEDがrecord/totalTimeの二箇所で発生し未合格。source上は各lock取得直後のtry/finallyでunlockし、count/snapshot同形はraw0。警告を無視/抑制せず、validation/delegate操作と純粋状態更新・読取のlock区間を別private methodへ分離し、全lock helperを取得から開始する同値構造へ修正する。BG1696の未受入是正途中の追加静的検証手戻りとして分離記録、原post/exec/XML/静的ログを保持し同新source32/4/四100/staticを必要再認証する。max/単位/負入力/例外/oracleは変えない。

まず新三件だけを同source六Jar/SDKでfresh JUnit実行（PG8284）。既Main変更0なら新限定観点のactual成功だけを記録し、旧source coverageと合算しない。既実装が累積histogram契約に違反したら修正前915/916起票→原因/最小是正→必要既12＋新3等を同新sourceで実行し四coverage100/静的/traceへ。snapshot/operator/fixtureの誤りは先に独立根拠と照合し、実際値へoracleを合わせない。

未実行/失敗をPASSへしない。1756と公開manifestへ実command/JDK/OS/source/actual XML/終了/exec/hash/BUG/再試行費を記録する。現時点PT0/coverage未測定、正式1964-53/原190新受入0/工数null/QA051final/PTALT0/全actual HOLD不変。次Timer/counterの標準encoderへ継続、通常小区切り停止0。
