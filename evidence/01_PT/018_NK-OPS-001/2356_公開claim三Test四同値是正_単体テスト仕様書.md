# 公開claim三Test四同値是正 単体テスト仕様書

2026-10-28、PG-D749/BUG1986/YKT1734、変更主F03・元canonical owner/cost保持。着手前見積3/6/9pp cap10、fresh共有69/残31/reset1793599188、N/T専有費null、原見積/v3/v4不変更。既saveb723d99213618ad8f2363649b3e5d39dc6416323/push1013真正0を保持、sourceBefore2ef。

## Scope・独立oracle

四反復literal（pid=300、dump_size=3、固定run UUID、固定cutoff）各四・全16だけをprivate static final Stringへ移す。三wholeTestはStartupLaunchRecordTest全四/BackupWorkerRequestTest全九/CleanupWorkerRequestTest全七の20 methodで、古いJavadocの件数rangeを実JUnit数としない。全原method/helper/条件/golden/expectedを四定数だけ逆展開して原全tokenへ一致させ、誤値/参照/宣言/型/無効case/期待assertion改変を非同値反例で拒否する。Main/POM/全設定/他Test不変更、新TestID0。

|元Test ID/whole Test|独立入力・期待・検証観点|
|---|---|
|LAUNCH既001～006関連 / StartupLaunchRecordTest四|手書きNKLAUNCH1の八固定field、両service、UUID/hex/PID/ticks/末尾/ASCII/長さ/未知/欠落/null、fixed SHA256(abc)=ba7816bf…15ad、算法例外/未知RTE identity・固定redaction。文字列/byte比較は手書きGOLDから作りProduction encodeでexpectedを生成しない|
|PT-OPS-BREQ既001～008/verification追加関連 / BackupWorkerRequestTest九|手書きNKBACKUP1及びVERIFY1、所有byte成功/失敗消去、固定日時からJST directory literal、年0001/9999・µs/前後境界・nil UUID・overflow/非canonical/未知field/ASCII/length/null、返却byte別物・固定32自己taskのparser非干渉|
|PT-OPS-CREQ001～007 / CleanupWorkerRequestTest七|手書きNKCLEAN1/four fieldの順序/末尾/ASCII/length・nil/distinct UUID/年µs/hex/null、入力消去、redaction/immutable、二virtual taskで独立consume。parser replayはCleanup再実行の許可ではない|

設計根拠SS341§6/SSC092、SS342/343SSC104137・既1488の公開相関codec境界を使用。既完了の境界追加Testを探して同じ成功確認を再演せず、当変更三wholeTestの影響回帰だけを行う。原Test間のbyte/hash値・unknown例外原文は合成fixtureであり実key/credential/session/boot/runを取得しない。

## 着手前判定・閉鎖範囲

PT_DEFAULT。三wholeTestと全helper、Startup/Backup/Cleanup Main全本文、MaintenanceOwnerFrame全本文、BatchRun/CleanupProfile/同sealed siblingは読取済み。操作はJDK byte/String/UUID/Instant/MessageDigest及び自己所有有限workerだけ。StartupのParentは値constructorとinvalid/静的dataだけで、MaintenanceOwnerFrameのparentsGuard/FFM/実parent認証は使わない。Cleanupはouter record/BatchRunだけ、Expiry/failed receipt/snapshot/DB権限を操作しない。実Root/noargs・permit/intent・Unit/VM/DB/Backup/鍵/私有raw/ネットワークへの接続0を事前確認し、実行後に同source/CRC/明示method probeで追加照合する。公開相関dataのencode/parseを起動権限発行へ読み替えない。

候補読取時にMaintenanceOwnerFrameTestはparentsGuardからLinuxMonotonicClock/ChildStartupContextへ進むためwholeTestをHOLD、純部品だけを抽出しない。InspectorLaunchConfigurationTestはInspectorSettings.databaseNameが既Graph329/330のInspectorDatabaseConnectionsへ依存するため、今回の動的許可に含めずHOLD。これらを実際に拒否されたPTと断定せず、安全/既scope条件が未認証の予防保留とする。Startupの既独立whole四methodはそれらの代替や新fixture抽出ではない。

一source normal六/PT0→原20/三suiteを一fresh owned JVM/exec（外側240秒）→当三TestのPMD/CS→五Threadのscope/method/原ID/現XML・自己ownerのTWR/有限task・局所無期限get/invokeAllと外側上限の区別を個別結合→独立XML/全input/全Main1843不変・Test物理差/許可外probe0/全artifact分母と未到達→trace/集合/完成。実counter未達は未達、FFM等を除外して100%を作らず、旧exec/別source成功の合算0。静的rawは九→残五の予定であり0へ正常化しない。

実command/時刻/OS/JDK/tool/branch/source/hash/input/expected根拠/実際XML/終了・coverage/BUG/YKTを新manifestへ保存する。別sourceの成功を当sourceのfresh正式に転用せず、F/E/S/aborted/flaky/not-runをPASSへ算入しない。C02/実Unit・正式1964-53/17-190/工数null/QA051final/全F03-451/HOLDは、個別終了依存が実証されるまで不変更。通常小群/commit/報告/PMO待ち停止なし。
