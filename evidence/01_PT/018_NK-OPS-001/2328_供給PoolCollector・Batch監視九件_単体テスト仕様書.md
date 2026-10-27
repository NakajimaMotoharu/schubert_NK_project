# 供給PoolCollector・Batch監視九件 PG/PT仕様

2026-10-28/PG-D739/BUG1968YKT1716/event2692。元source e2a04c5d5775b8629ce3c4f17259d8378b2bb5f9、先行save38d1127c9/push32680真正0。RD171/UI252/SS311341351、原1639/1728/1615/1700/1543、canonical owner/cost P01809、changeOwner F03。着手前2/5/8pp cap10/fresh62残38/reset1793599188、N/T/専有費不明null。

対象はwhole DbPoolMetricCollectorTest八/whole WebDbPoolMetricCollectorTest八/whole TransferMetricRecorderTest八/whole MonitoringRetentionConfigurationTest八/whole MetricContractTest六=原38五suite。九重複String（active/DEBUG二ずつ、.part/.ready/DEBUG、CONFIG_DRIFT、CONFIG_INVALID）を同値定数へ移すだけ。固定期待値・型・例外・全method/helper/control/並行oracleを独立token逆で保持。Main変更/新TestID0。Test IDとclass/method/inputはplan/逆検証の原catalogへ一意記録する。

期待値根拠：POOLCONN/WEBPOOLCONNはfakeMXBean getter3,5,2,8・invalid最大0/真zero/unknown・provider例外identity/SDKgauge/cardinality/owner独立・publication lockの遮断。TRANSFERMETは2+3=5files/1024+2048=3072bytes・long overflow/固定double丸め9,223,372,036,854,776,000・四gauge・独立owner・snapshot identity。RETCONFはSS351 decimal15日/5,000,000,000byte、前後1境界/未観測・負数・最大・generated fixedhash705033170/466/−31とfixedtext。METRICは独立testresource TSV全26行と九bucket literal・label欠落/余剰/未知/null/並行。productionからexpected生成しない。

PT_DEFAULT：五Test/五新Main（collector二・TransferMetricRecorder/MonitoringModePolicy/MetricContract）全文確認、observer二/recorder二とfakeFixture二は前群全文＋同Main/currentSHAを照合。自己SimpleMeterRegistry/MockClock、JDK Proxy四getterだけでHikari pool/config/JMX接続/DB無し。batchは純値/enum、metric-catalog.tsvはfrozen classpath resource読取だけ。新所有空CWD、有限64/100worker/TWR又はfinally shutdownNow+await10秒。API collector/retention/transfer/catalogのinvokeAll/get局所無期限は外側240秒と区別し保持、Web collector5秒・latch5秒/2秒spin/100ms負観測を保持。snapshot==は同一instance契約、equals(null)はgenerated contractを意図しており機械置換しない。

ApiSyncDispatcher/HttpValveは保留中例外typeへ実依存するため実行/部分抽出しない。ApiOutboxCleanupは全support closure未確認で当群外。実VM/Root/DB/JMS/native/鍵/Graph9・保留二工具はHOLD。元run確認再演0。

実行commandは各checked entry `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg<番号>_<対象>.py`。12374plan/12376独立逆→source固定/12378六normal PT0→12380原38一exec→12382実PMD-CS→12384独立XML/CRC/全Main・Test物理/同source四counter→残文脈/trace/current集合。draft AST/import参照検査、固定TC GJF --skip-reflowing-long-strings、正常build Spotless/NullAway/JSpecify/Werror維持。100%未達を正直に記録し除外・合成・未実行加算無し。実結果/環境/時刻/branch/commit/command/終了code/証跡hashは後続manifestと2329へ。正式1964/53・17/190・工数null/QA051final/全F03-451/HOLD・元予測を維持する。
