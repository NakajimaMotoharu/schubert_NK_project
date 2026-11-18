# BUG-3263 API四Recorderの固定modeと独立反例

WBS-F03/2-2（第58版実行順82）、WBS-P018-09、NK-OPS-001、RD171、UI252、SS351/354。Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。AsyncJobMetricRecorder（ASYNCGAUGE001–008）、OutboxRowsMetricRecorder（OUTBOXMET001–008）、OutboxAgeMetricRecorder（OUTBOXAGE001–008）、OperationMismatchMetricRecorder（OPMIS001–008）。元1623/1643/1647/1660の全32項目、同条件、期待値と1000反復・64並行・別owner・正確な件数は保持する。新slotはF03の該当分岐検証であり、元行価格追加0。

設定不正の元4項目で独立既知値DEBTfとSTANDAQcを追加する。文字列コード値を31進桁として合成すると、それぞれDEBUGの64,921,139とSTANDARDの2,095,255,229に一致する（PG39230固定oracle）。SS351から型はIllegalArgumentException、固定理由はCONFIG_INVALID、登録呼出とmeter数0。元null・空・未知値・正modeの期待は維持。合成値は製品methodから取得しない。元workerはinvokeAll最大10秒、終了待ち10秒で成立済み。

Linux amd64・JDK25.0.4・Maven3.9.12、branch dev-foundation・固定試験commitは実行記録。許可済closed-host profileで Micrometer 1.17.1の自有memory Registryに限定し一回の全32を実行。実process/backend/保護型への依存なし。独立postはXML/終了/CRC/物理一覧、constructor生B、実Classの四counter・残不足を同execのfilter除外なし計測で照合する。生成record/enum counterや別既存分岐の不足は実測を記載する。試験結果、command、入力、hash、BUG/YKTをPG39264と4652へ連結する。
