# Backup公開後identity差分・独立PT仕様

Program NK-BAT-001、BackupArtifactVerifier.BundleSnapshot.samePublished / BackupBundlePublisherTest.bat2732001PublishedBundleRejectsEveryIdentityOrContentDrift、Test ID PT-BAT-2732-001。主担当WBS-P017-05、BAK/BKO/OPS009/UI251/SS341§6.10・343§5.3/SSC066/BUG204-YKT160。

独立fixtureは固定literalのmanifest digest、directory metadata、file/contents map。公開rename後もmanifest/device/inode/nlink/size/mtime/各file snapshot/contentsが一致する期待true、directory ctimeだけの変化は期待true。各固定項目を一つだけ変えた八差分はすべて期待false。期待値をProductionから生成しない。role mode/uid/gidは前段の二度のcaptureで認証済みという当predicateの事前契約であり、この試験をrole検査へ代用しない。

操作は純predicateのみ、Backup/Root/DB/VM操作なし。既readonlyCompatibilityのimmutable map/null試験、既publish実file後条件は維持。新一JUnit/十入力（同一・ctime差＋八拒否）、既F/E/S/flaky/not-runは合格へ算入しない。Production Main不変更、coverageは当methodと測定範囲を明記しclass全100へ読み替えない。

実command、対象Test commit、XML/coverage/hash/静的結果はPG2732限定manifestへ追補する。初期状態=未実行、関連新障害なし。必要な変更群全回帰と当native資格への統合・451・全WBS終了依存は別未完。
