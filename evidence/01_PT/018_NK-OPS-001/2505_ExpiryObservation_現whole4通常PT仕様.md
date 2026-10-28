# 2505 ExpiryObservation 現whole4通常PT仕様

2026-10-29、PG-D818予定、START2884/開始0.5/2/4pp cap10/freshused28残72/reset1793774153。source17ab52b25/保存bd313c6702f07d7852acee6b38abe1bd2a1c12b0/push39690真正0/remote一致。主F03/canonical担当費P01701参照のみ/追加予算0、normal13596/静的13599同source参照・確認再演0。

## PT_DEFAULTと全到達範囲

既MorningExpiryObservationInvariantTest180行/全4method、ExpiryReceiptFixture107全body、Main nested ExpiryBegins/ExpiryObservation全ctor/toString、BatchRun/Step/StepAttempt.time/Result、ExpiryAuditRepository.Snapshot/Priorの全到達bodyと静的初期化を確認。fixtureはBackupUnitReceiptGateのpackage-only四port constructorへno-op Contextと同AtomicReference snapshotを返すProbe/Terminalを明示注入、capture/observeResultの全経路はそのmemory supplierだけ。Gate/TerminalReceiptのtarget/exit getter、Target enum/maintenance enum、InspectorUnitSnapshot416全bodyはString/Map/number/UUID parser・predicateだけ。

Gate.create/defaultRoot/NativeReader/kernel観測/Unit start-stop/permit/DB接続を呼ばない。outer MorningDatabaseSession/ExpiryAuditRepositoryの接続ownerインスタンスを作らず、nested recordの値整合性だけを検証する。Javaのtest-only receiptはhandwritten stateから得た入力で、実kernel/permission/原本Backupの証明ではない。実Root/DB/JMS/HTTP/VM/native/credential/key/Graph9操作0、旧HOLD whole抽出0。現Test SHA7daa2c14…は13400前46e19b30…からliteral1同値変更後、fixture SHAabf309d8…は現normalと完全一致。旧成功を当runへ転用しない。

NK-BAT-001/DAT009/OPS009、UI251、SS331/341/343・SSC126/ISSSTEP002、既EXP1749001..004。source/fixture/currentJar・JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15を固定する。

|Test ID|入力/操作・独立期待|
|---|---|
|EXP1749001|固定Run UUID/cutoff、START/END、SUCCESS2/2/0/200、SKIP0/ALREADY_SUCCESSFUL。freshのended/target/bytes・同receipt identity、skipのcurrent START/元audit ENDを直接literal assert、redacted toString。dataをauthorityへしない。|
|EXP1749002|ended<START、BACKUP target receipt、freshにSKIP、audit ended/status/target/success/failure/bytes各一差分を固定入力から作りreject。比較expectedをProduction constructorで生成しない。|
|EXP1749003|skipのended/result/audit/current receipt code10の個別反例をreject。元auditをcurrentSKIPへ上書きした期待を作らない。|
|EXP1749004|current step wrong、skip/prior presence不整合、current/prior/各observation fieldのnull、ended+1ns（micro precision不正）をreject。実DB/IO前の値境界。|

時刻/UUID/counter/期待status/field差分はTestの固定値、input receiptは別Gate factoryから作るだけでrecord出力をexpectedへ再利用0。新ID/JUnit method0、vector/loopを新件数として数えない。null/欠落/未知値/正常・境界・不整合・fresh/skipを対象とし、並行/再送/実DB後条件はこのimmutable data componentの対象外で後続programに残す。

## 実行・coverage・工具

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13732_expiry_observation_whole_four_pt.py`、新only SLOT/固定六jar/empty ENV設定。自己試験12観点と独立13728を確認した不変SharedSelectedJunitReporterV1＋固定Mapの11行binderだけを使い、既host/helperは変更しない。期待4はMap一箇所から導出、whole四/一意case/FES-abort-container0だけ成功。工具自己fixture/Driverはclasspathへ追加・実行しない。

13734は原4XML/全source/SDK/extra Java hashes/単一exec-session/同normal CRC、完全二nested component `MorningDatabaseSession$ExpiryBegins`/`$ExpiryObservation`を測る。これはouter JDBC source file全体の資格ではない。JDK25 recordの自明generated accessor/equals/hashCode/toStringは固定JaCoCo既定filter、手書きctor/明示Observation.toString/全業務分岐を除外しない（2348の生成構造原則）。除外追加0・旧exec合算0、miss/未測定を100へ補完しない。正式1964-53/17-190/工数null/QA051final・全actualHOLD/全原本/二held工具保持。
