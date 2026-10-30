# Backup manifest値 原whole8仕様

2026-10-30、主P017-05/関連P017-03.01追加0、着手前.5/3/6pp、source6b53/normal14216、BAK/BKO/UI251/SS341§6.4/343§5.3/SSC058。元BackupManifestValuesTest全285行/八methodと公開literal helper64行、全対象Main/依存repository値型/initializer全body確認済み。実Backup・DB・OS原本・鍵・credential・dumpには触れず、見かけのdigest/public version文字列と固定時刻の値型だけ。

対象全三Source/三physical=BackupManifest/BackupVersions/BackupFileDigest。BatchStepAttempt/BatchRun/BatchStepはfixture依存で、その全域資格は本群に含めない。TOKENSは公開release文字列でoperation/session tokenではない。

|Test ID（元method順）/method|独立入力・期待値|
|---|---|
|PT-BAT178/completeIdentityAndDirectoryName|固定UUID/時刻/size1+512+200→total713/config712、既存literal directoryName、run/step/claim getter。|
|PT-BAT179/fileDigestBoundsAndOverflow|size1/Long最大、負/zero拒否、lowerhex64と長/文字/Unicode/改行境界、Long総計overflow拒否。|
|PT-BAT180/versionTokenBoundaries|schema001/999正常と000/桁/Unicode異常、他token1/128/ASCII集合正常と長/先頭/空白/path/quote/control異常。|
|PT-BAT181/stepAndRunBinding|BACKUP_DB/CONFIGの固定対応、skipped/同id/異run-cutoff拒否、id/attempt正常境界。|
|PT-BAT182/timeAndPrecisionBoundaries|開始前/終了前/最大/1ns、年上限拒否、Tokyoの古いLMT/DSTは固定literal（0001/1582/1887/1948/1952/9999）で独立期待。production formatterやZoneIdでexpectedを作らない。|
|PT-BAT183/nullAndRedaction|全九field/eightversion/一digestのnullはNPE、固定redacted診断三種。|
|PT-BAT184/immutableAccessors|同値/非同値/同値hashとgetter、helper TOKENSの固定値と比較。|
|PT-BAT185/concurrentValueUse|own8 threads/64 read-only jobs、各total713/config712と固定directory literal。外側実Backupの並行安全性ではない。|

拒否時のIAE/cause null/suppressed0は原helperで確認、実プロセス/署名/権限/鍵操作なし。command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14702_backup_manifest_values_eight_pt.py`、一fresh JVM/八原試験/一suite、F/E/S/not-run0。独立14704で全normal input/六Jar/静的14224/元ENV、公開helper hash、一exec-session-CRC/三Source全closure/四counter/八metadata反例を照合。未達保持、製品再演/旧coverage合成0。manifestに環境・source/branch/commit・command/start/end/exit・case/XML/exec/coverage/hash、結果2750。正式1964-53/工数null/QA051final/実Backup等のHOLDは不変。
