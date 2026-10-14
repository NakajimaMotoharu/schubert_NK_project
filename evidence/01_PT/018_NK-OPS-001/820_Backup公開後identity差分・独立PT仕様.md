# Backup公開後identity差分・独立PT仕様

Program NK-BAT-001、BackupArtifactVerifier.BundleSnapshot.samePublished / BackupBundlePublisherTest.bat2732001PublishedBundleRejectsEveryIdentityOrContentDrift、Test ID PT-BAT-2732-001。主担当WBS-P017-05、BAK/BKO/OPS009/UI251/SS341§6.10・343§5.3/SSC066/BUG204-YKT160。

独立fixtureは固定literalのmanifest digest、directory metadata、file/contents map。公開rename後もmanifest/device/inode/nlink/size/mtime/各file snapshot/contentsが一致する期待true、directory ctimeだけの変化は期待true。各固定項目を一つだけ変えた八差分はすべて期待false。期待値をProductionから生成しない。role mode/uid/gidは前段の二度のcaptureで認証済みという当predicateの事前契約であり、この試験をrole検査へ代用しない。

操作は純predicateのみ、Backup/Root/DB/VM操作なし。既readonlyCompatibilityのimmutable map/null試験、既publish実file後条件は維持。新一JUnit/十入力（同一・ctime差＋八拒否）、既F/E/S/flaky/not-runは合格へ算入しない。Production Main不変更、coverageは当methodと測定範囲を明記しclass全100へ読み替えない。

実command `PYTHONPATH=<既構築quality/runtime> python3 -B tools/quality/pg2732_backup_published_selected.py`、Test source ea670ff9514d681b03c41baf5858a336567ad4ad、PG2732/session19167 actual0/一JUnit/FESAbortedNotRun0/全1643Main mismatch0/javac warning0/VM操作0。独立PG2734/session35821 actual0で一意XML-case/hashと全coverageXML hashを確認。XML SHA256 `0947799ab997d9beab6e3ee916da2c3f18e8f4ea963fadd04377a363fa1b0cf3`、exec `a4033e460d07280d1ddf166464f5f6dc5db26231111435e852b640584a5d10f3`、server manifest `fd0f977c098ca31fd2622d2b3884b58449ca9a162792cc6591c87628ab0b85c6`。Test input SHA11aefdee、私有PG2732/2734のmanifestへ保存。

当samePublishedはLINE8/METHOD1/BRANCH16/全counter miss0。ただし元同methodは既存別publisher fixtureですでに網羅済み、追加coverage gain=0。残class aggregate12branchを当methodの未網羅と誤認しない。新十入力は独立oracle補強として保持、試験件数/工数/正式への重複加点0。必要な変更群全回帰と当native資格への統合・451・全WBS終了依存は別未完。

## PT-BAK-2736-001 保持判定の真正未網羅admission

BackupArtifactVerifier.retentionSizesAgree、BackupRetentionBoundaryTest.backup2736001RetentionRejectsNonrootCrossDeviceAndParentDrift。PG2722当source gap/XMLにある264 effectiveUID、282 child device、314 parent二読の三false条件を着手前に確認。固定開始clock100、公開人工三archive＋MANIFESTを持つ既BackupArtifactFixtureの実Linux FD/IOを使用し、root権限/metadataだけを試験portへ注入する。実Master/DB/Backupは使わない。

入力はnonroot UID1、childだけdevice+1、parent二読目だけinode+1の三独立ケース。各StorageIoException.UNAVAILABLE、cause無し、削除証明を返さず、全file bytes不変・全handle解放を期待。nonrootはentry open0、parentDriftは正確に二回読んだことも確認。期待値はSSのowner/device/inode再認証から独立固定。通常/欠落/hash不一致/null/例外の既2120四PTは維持。

初回v1/session73077、Test source296259737、actual0/一JUnit/三入力/FES0/javac warning0、server manifest b083b306b565abcc1db95fee361bdd1a1c82ef5437a00437e5f33997501d76e2、host-only残branch869→867/増加2・Main不変更。parent inode差分は既網羅済みの補強。行314の未網羅はparent一致ではなく、その次の終了時effectiveUID検査と訂正する（元event0720は保持）。

v2はlateNonrootを追加：二回目parent metadata読取時だけeffectiveUIDを1へ変え、正常metadataなのに終了時UID再認証でUNAVAILABLEを期待、parent二読を確認、bytes不変/handle解放。四入力/一JUnit、別new-only PG2736-selected-v2、初期状態=未実行。v1の成功をv2へ流用0。method/line単位と一意XML/hashを確認し、class/global100は別判定。新障害なし。

v2/session65821 actual0、Test4cfa1aa15、PG2738/session9733独立actual0、XML8c9bbb24/execadf44285/server49e34b79、retentionSizesAgree L20/M1/B4 miss0・host869→866/追加3branch。v1増加2とv2増加3を合計5へ加算しない。native unionは未統合、全PGPT/formalは別未完。

## PT-BAK-2740-001 pending bundle admission

BackupArtifactVerifier.observePending / BackupArtifactVerifierTest.backup2740001PendingRejectsEveryAdmissionDriftAndKeepsAllPublicBytes。当source gap163/171/182/188/229と実sourceを着手前照合。固定run/開始日時から既公開fixtureを`.part`へ配置、MANIFEST無し・三archive bytesを独立事前保存。

nonroot、child device差、file負size、raw→capture inode差、file device差、parent二読inode差、終了UID差の七種を三file roleごとに計21入力。各UNAVAILABLE/cause無し、全三file bytes不変、MANIFEST生成なし、全handle解放。inode raw→captureは正確に二読で拒否、parent差/終了UIDは正確に二読まで到達を確認。期待はSS343の所有/device/保持inode再認証、期待生成にProduction methodなし。既正常のliteral三hash/未知・欠落/null/例外試験を維持。fixtureの`.part` directory roleは実held FDの末尾名（DIR+.part）を使用し、final名roleのchildへ誤接続しない。

command=pg2740_backup_pending_selected.py、初期未実行、Main変更/VM/DB/Backup操作なし。Testと工具を固定後、実XML/入力hash/coverageと静的を独立確認する。既group全体認定/人工native加点0。
