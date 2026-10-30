# 2815 Supplied health十whole81仕様

P01809、着手見積2/6/10pp/cap10、source6b53/normal14216。原十whole81の全2672 Test行・必要Main625行を読了。NORMAL_PT：供給済みscalar/Duration/Instant/boolean/MemoryUsage、own SimpleMeterRegistry＋MockClock、有限poolだけ。実Queue/DLQ/Expiry/Backup/restart/integrity検査・修復・回収・システム時計/heap/GC/VM/Root/鍵/DB/network操作は行わない。既1090とsuite/完全Source非重複を事前確認した。

|原suite/TestID|件数|独立期待値・観点|
|---|---:|---|
|AsyncQueueMonitorTest/ASYNCQUEUE001～008+ASYNCBYTE002|9|count4999/5000/8999/9000とstorage70/90%を別次元、long境界/欠測・partial/回復5-10分/不正不変/並行64/record値|
|BackupHealthMonitorTest/BACKUPMON001～008|8|scheduled-success独立boolean×連敗0/1/2/MAX、欠測partial/回復/gap/負・逆行/null/並行/record|
|DlqHealthMonitorTest/DLQMON001～008|8|全service/現在count1-MAXと増加・未調査、0とflag矛盾拒否、自動close禁止/欠測/immutable/並行/record|
|ExpiryBacklogMonitorTest/EXPIRYMON001～008|8|999/1000/4999/5000/MAX固定severity、欠測/5-10分/gap/null・負・逆行/並行/record|
|IntegrityHealthMonitorTest/INTEGRITYMON001～008|8|0/1/MAX・常時critical/保護alert自動close禁止、全service/欠測/gap/負逆行/null/並行/record|
|JvmHeapHealthMonitorTest/HEAPCONN001～008|8|fake beanとclockのみ、600秒warning/unknown max回復gap/失敗同一性・再送なし/getter回数/null・逆行前無副作用/並行64|
|RestartHealthMonitorTest/RESTARTMON001～008|8|供給count0/1/4/5/MAXとrateLimit独立flag、partial/5-10分/原因確認/gap/全service/不正不変/並行/record|
|TransferHealthMonitorTest/TRANSFERCONN001～008|8|3.5/4.5GBと5000/9000files・suffix合計、STANDARD/DEBUG、欠測NaN/gap回復/borrowed meter所有・registration例外/並行|
|WebLogBacklogMonitorTest/WEBLOG001～008|8|5000/9000または5/30分、ns手前/長整数端/partial/回復/gap/null負逆行/並行/record|
|TransferMetricRecorderTest/TRANSFERMET001～008|8|閉4gauge/suffix label、固定2+3=5/1024+2048=3072、MAX double固定literal、null負overflow/NaN≠0/immutable atomic/partial登録失敗/借用registry|

全10Sourceと全24Code closureを同一new exec/sessionで測定。各Source四counter非空100と自然B0/LMC100を区別、未達は未達保存・除外で補完0。record公式JaCoCo filter不変更・manual除外0、手書きinvariant全対象。期待値はSS351の承認table/独立固定literal/回数・時間境界、production値からexpected生成0。

JvmHeapHealthObservationTest、MonitoringObservationClockTest、FilesystemHealthObservationTestは既読のFixture/FixtureClock/FixtureStoreをfresh compileする依存fileだけで今回の選択suiteには含めず、旧27methodの再演/加算0。synthetic-test-only-no-allocation Errorは通常の同一object伝播のみでOOM誘発・graph解析・動的管理API0。Registryは外部exportしないSimpleMeterRegistry、実プロセス所有は当試験childだけ。own pool/registryはtry-with-resources、親JVM180秒。

command checked entry pg14982_supplied_health_monitors_eighty_one_pt.py、JDK25.0.4/JUnit/JaCoCo0.8.15、fresh javac proc:none/Werror、Main六Jarはnormal14216固定。入力pin/全command/元ENV/実時刻/exit/XML81/exec/一session/CRC/全counter/owner/独立反例は2816と14982～86へ。原本/旧成功失敗/stash7/Currentbaseline/二held/HOLD/正式1964-53/工数nullを保持し、PGPT全体受入に換算しない。
