# 監視Test十・命名/fixture規約是正仕様

群PURE_MONITOR_TEST_NAMES10_PGPT_V1/event2777、主担当P01809/関連F03追加配賦0、元2/5/9pp cap10、source7ced2d707/save5928afadd。BUG2023/2024・YKT1771/1772を修正前起票した。元原診断と現source SHAが全一致する十TestのAT/at命名十件とTransferのDEBUG重複一件だけを是正する。全Test実装の独立golden/期待/assertion/入力/境界/並行は変更しない。

## 閉集合・変更

batch.monitoringのAsyncQueueMonitorTest（9件）、BackupHealthMonitorTest/DlqHealthMonitorTest/ExpiryBacklogMonitorTest/IntegrityHealthMonitorTest/RestartHealthMonitorTest/TimedDbPoolMonitorTest/TimedSyncLatencyMonitorTest/TransferHealthMonitorTest/WebLogBacklogMonitorTest（各8件）、計81 method/十suite。元Test IDは各method名/既Program仕様へ追跡、13070で元全81 catalog/原31finding/各source全文・hashを保存する。現Source Test AT private field/全identifier参照だけOBSERVED_ATへ、factory at()を不変更。Transferの11個の"DEBUG" String tokenだけprivate DEBUG_MODE_FIXTURE一つへ抽出し、既"debug"拒否・STANDARD・metric literal・hash/text期待を不変更。各元全token逆と非同値反例を初回source固定前に検査、整形は全literalを不変更とする。

原診断集合=命名十＋DEBUG一＋既worker20で31。修正後の原是正目標11、自己worker20は残して全F03 PASSへ変換しない。無関係Testや既未対応rawへ範囲を拡張しない。新Test ID0・全81は修正影響の再試験であり既成功確認の無目的再演ではない。RD171/UI252/SS351/411/451、上位変更/QAなし。

## 実行資格・oracle

whole十とpure Main十九を全文確認済み。Main十monitor＋AlertLifecycle/ObservationContext/TransferMetricRecorder/MonitoringPoller/AlertThresholds/ContinuousConditionWindow/MonitoringModePolicy/MetricContract/MonitoringObservationClock。固定supplied count/time・pure lifecycleだけ、Transferはcaller所有SimpleMeterRegistry/MockClock（外部exporter/実clock/collectorなし）。各Test自己8pool/64tasksは既TWRを維持し、失敗も含め専用JVM240秒で上限を設ける。元pool/invokeAllを勝手に変えず、当実行は真正終端とempty own CWDを必須とする。

実DB/FS/HTTP/JMS/queue/Backup/Root/systemd/VM/native/Graph9/鍵・保留二工具へ接続しない。未使用MonitoringObservationClock/MonitoringPoller.observeNowはmethod probe0、他Mainもclosure外Product probe0を独立検査する。Source固定後一回六normal→元whole81/10→局所PMD-CS/六SB→同一exec全artifact/CRC/全Main不変・当十Test source所属physical差のみ/他旧Test不変→raw11是正と既20worker再束縛/owner/trace・Program索引を閉じる。counterは測定値を先に保存し、当十九Mainの未達や既定filterを隠さない。旧exec/別sourceを合算せず正式1964/53・17/190・工数null/QA051finalを維持する。

## 計測

開始old窓used86/reset1793599188→レビュー中fresh used0/reset1793774153の変化をevent2778へ保存。原因UNKNOWN・reset操作/券消費/課金0、窓間差を計算/相殺しない。原群見積は固定、実N/T/専有費はnull、次点検は新窓used5、fresh残10以下で新規停止する。元/v3/v4/v5予測を完成率に変換せず、2413に原是正/再認証/tool手戻りと実証/未証明を分けて記録する。
