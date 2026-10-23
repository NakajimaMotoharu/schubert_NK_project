# 1583 FilesystemHealth観測 実行結果

source `bbc230f8a892d3ad2e47aeaccbe37bbb86bd97b6`、1582/group1840。PG7152-filesystem-health-host-v1原SHA `8ddd7c3c81b98e2481a7f360ada94627d04138fe5403a4694c6516cb31a8afd9` は真正verify0/83PT12suite/FES・rerun/flaky0・六format0。新10と同監視packageの必要回帰73を区別し、旧71sourceの73を当sourceへ加算していない。固定FileStoreの健康観測→既連続window→Filesystem警報を一経路として検証し、実filesystem/owner/collector起動は行わない。

PG7154-filesystem-health-post-v1原SHA `a86ed6ca91bc6df6d9bd886cf7b487a5253176a2f22b55c7b82b31657a5e110f`：原83XML/全25Java source/実21class＋metadata1、単一session・CRC差0、**L413/M97/C21/B199すべてmiss0**。親lint/Werror/NullAway・Spotless・SpotBugs/Checkstyle0。PMD raw15/exit4/processing0のうち既14はsource/byte不変・既1564/1569の個別理由を保持、新一行FilesystemHealthMonitor.observe/AvoidSynchronizedStatementを次のとおり分類する。

新一行=CONTRACT_REQUIRED（private final lock内で一pollの二統計読取と状態遷移を直列化し、外部からthis/class monitorを保持されない）。内側TimedFilesystemMonitor lockの順序は一方向、snapshotは内側だけ取得して外側へ戻るcallなし、FSINPUT007010の64並行read/poll・不変snapshot/countを実行。callerが渡すproviderの有限性や実polling deadlineをfixtureから証明したとはしない。JDK FileStore実呼出はblockし得るため、実source/finite収集期限・外側owner停止後条件は後続HOLDであり、当実装だけで本番のbounded collectorを認定しない。private lockをReentrantLockへ置換してもprovider自体の期限は保証しない。抑制/ルール削除/実違反の偽0化なし、未分類0。

FSINPUT001～007：0/80/90/100・不正total/usable・各getter IOException・非formatable IOException・Runtime/NPE/Error同一伝播・Long.MAX/total1・整数80/90/95一byte境界の独立IEEE literalを確認。checked失敗はUNKNOWNで非正常化、uncheckedをcatchして成功扱い0、path/name/type/attribute/toString呼出0/新metric-label0/借用close0。008～010：warning300秒/critical60秒、欠測が10分回復を切断してcount/firstSeenを保持、gap/逆行/null・64同elapsedでcount65を確認した。expectedは固定byte表・固定時刻/Severity/BigInteger/IEEE bitsから独立作成。

OS/JDK/tool/branch/source/実command・開始終了/終了コード/全input/期待仕様/Test ID/元XML/hash/coverage/staticは7152/7154 manifestと1582へ結合。新障害0（今回のMain/fixture初回を同oracleで成功）、上位QA/RDF/UIC/SSC変更0。標準Micrometerのdisk.freeは固定core1.17.1/9ca47dfaのDiskSpaceMetrics BootstrapMethodsにFile.getUsableSpace、disk.totalにFile.getTotalSpaceを用いることをlocal公開bytecodeで確認。健康入力の意味を合わせたもので、標準metricを独自exporterへ置換せず、そのSDKを今回Batch PTで実行したともしない。

全体451/native/CHR/当source全Web実行/正式1964-53/歴史17/別source新7/工数null/QA051final/PTALT0は不変更。原4222/common44/旧成功再確認0、原本/private環境/VM/Root/DB/鍵/配備HOLD維持。
