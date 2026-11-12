# Backup例外分類七境界の製造と未実施PT仕様

NK-BAT-001 / BUG2743・2744 / YKT2359 / PG-D-355、RD BAK006008/OPS009共有・UI251・SS312331333341343352。対象ArtifactVerifier.observePending/retentionSizesAgree/verifyAtの三Runtime、Reader.findCleanupClaims/readClaimAtの二Runtime、Commit.completeの既知SQL両失敗fallbackと外catalog二境界。固定期待値はorigin/main SS312の有限cause/suppressed/SQL-next Error同一object、SS333/341の元型別primary/cleanup優先とnormal固定catalogから独立に作る。

PG28180の変更はRuntime五conditional helper/SQL三helper call/Commit import一だけ、guardを外す逆変換で元byte完全一致、GJF-CS0。checkedIO/crypt checked失敗・pureCodec IAE・ResourceScope/Publisher/Retention/transaction条件/IO順/Byte・期限・所有は不変更。共通StorageIoException公開classifierは既batch-storage依存内、実credential/Root/capabilityを作る入口ではない。

| 将来Test ID | 独立入力・fixtureと期待 | 現在状態 |
| --- | --- | --- |
| PT-BACKUP-GRAPH2743-001..003 | 各既Verifier fault portのDirectoryIteratorException/UnsupportedOperationExceptionから固定Error objectへcause/suppressed、同一cycle/duplicateを手作成。expectedはそのobject、通常StorageIOへ変換しない。Error無しは従来固定reason/byte-zero/全close。 | NOT_RUN・既native wholeFixtureHOLD・抽出なし |
| PT-BACKUP-GRAPH2743-004..005 | Reader既IO/iterator/digest Runtime fault portから同じ有限graph、expected固定Error identity。pureCodec不正Optional.emptyとIO-only既定・全9属性/完全handle/name/全closeの既oracle保持。 | NOT_RUN・既native wholeFixtureHOLD・抽出なし |
| PT-BACKUP-GRAPH2744-001 | 既wholeCommit fixtureの入口Connection SQL next→cause固定Error、expectedそのobject、transaction開始/commit/rollback無し・caller破棄。 | NOT_RUN・BeforeAll実DB wholeTestHOLD |
| PT-BACKUP-GRAPH2744-002..003 | 既知bodySQL＋既知cleanupSQLの両graphに固定Errorならprimary、primaryにErrorなしならcleanup。元top-level unknown130matrix優先・rollback/復元条件を不変更。有限非fatalcycleは固定catalog/原因や診断実体保持0。 | NOT_RUN・BeforeAll実DB wholeTestHOLD |

当表は将来入力/独立expectedの準備であり、新しいJUnit method実装/実行件数ではない。元wholeTestから安全そうなmethodやfixtureを切出さず、別DataSource/Root/keyや代用fixtureを用意しない。各通常PT・coverage・NullAway/PMD/SpotBugsと必要同source全451は未実施を保持、BUG全体未完了。既old69 success/旧native/execを新sourceへ合算しない。補助検証command・終了code・input/原byte/差分/hashは018のPG28180 manifestに一意対応。Rootsource固定・独立sourcejoinは後続追記する。
