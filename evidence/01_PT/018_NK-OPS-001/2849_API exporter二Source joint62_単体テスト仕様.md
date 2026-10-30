# 2849 API exporter二Source joint62 単体テスト仕様

NK-OPS-001/WBS-P018-09/RD171/UI252/SS351/1753/1757/1771/1773、Production6b53/normal14216/dev-foundation固定。event3245で2/6/10pp cap10着手前固定。原Scalar24/Duration24は新48、既ApiMetricScrape14は新二Sourceのcatalog optional有枝を同じexecで閉じるための必要反復。成功再確認を目的としない。generic原48だけではpublic approved methodsとcatalog.isPresent枝が未実行になるため、既存原Scrape14全wholeを同execに限定選択し新規数に加算しない。旧94反復を保持し今回14追加で108と区別する。

原新Test970行、Scrape全body/Bundleの全field initializers、三Main（actual exporter二＋Scrape）/Catalog全body/必要SDK-only recorder依存を確認。APIにMetricText.javaは存在せずScopeに追加しない。固定literalCdf3/1.002/0.001:1/1:2/+Inf:3、nanosecond1e-9、2^53-1可/2^53拒否、Long.MAX_VALUE count/巨大有限sum、scalar2.5/最小最大正値、NaN/±Inf gauge・負/非有限counter拒否、escape/generic key deep-copy/重複・null/空/未知/型不正、snapshot/name/tag/value各一回だけ、IOException cause固定message/Error identityを独立期待値で検証。

approved oracleはSS351のAPI sixteen family name/type/label・10gauge/4counter/2histogram/900sample・51unknown、DB1ns/MQ1.5sと累積境界、固定layout/result/state/domain不正拒否、値getterによるtag変化後も捕捉済みimmutable labelsだけ出力。Production methodからexpected生成しない。finite4worker64job/Future10秒/finally close、親180秒。

当方ownSDK/MockClock/Noop provider/ByteArrayOutputStreamのみ、実DB/JMS/HTTP/VM/Root/Graph/鍵/ファイルIO/外部/配備/実session0。IOExceptionは固定throw seamで実ファイルを書かない。拒否対象の再演や境界探索ではない通常PT。各Test IDは下記原method名と元XMLで一意対応。

command: `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15132_api_exporter_joint_sixty_two_pt.py`。Java25.0.4/freshjavac -proc:none -Xlint:all -Werror/固定六normalJar。post15134は当一session/CRC/全二Source二Code closureを測定し、独立15136で原全62宣言XML/48new14repeat/SS351/Code/実ownerを別読照合。元OS/JDK/時刻/command/exit/source/hash/input/XML/exec/coverage/BUGを2850/public manifestへ保存。実測前coverage未確認、manual除外0/公式filter不変/execunion0、Failed-flaky-skipped-not-run合格0。障害は修正前915/916。

正式1964-53/歴史17-190/工数null/QA051final/451-F03-G07/全安全HOLD維持。Scrape/Catalog/他recorder Mainのcoverageや旧sourceを今回二Sourceへ合算しない。

## ApiScalarMetricExporterTest（新24）

- `scalar001LiteralCounterNameAndFraction`
- `scalar002GaugeUnknownZeroNegativeAndInfinityArePreserved`
- `scalar003FiniteCounterExtremesRemainExact`
- `scalar004InvalidCounterIsNeverClamped`
- `scalar005EmptyAndUnselectedAreNotFabricatedZero`
- `scalar006SelectedWrongMeterTypesFailBothPaths`
- `scalar007NullApiBoundariesAreNotUnknownObservations`
- `scalar008NullNamespaceNameSetOrElementFails`
- `scalar009InvalidNamesAndCounterSuffixFail`
- `scalar010InvalidMissingExtraLabelsFail`
- `scalar011DuplicateTagFixtureActuallyContainsDuplicate`
- `scalar012LiteralLabelEscapingRemainsLossless`
- `scalar013BorrowedSourceIsNotClosedAndClosedSourceFails`
- `scalar014NamespaceDeepCopyPrecedesProviderMutation`
- `scalar015CounterRuntimeIdentityRetained`
- `scalar016GaugeRuntimeIdentityRetained`
- `scalar017CounterErrorIsNotSuccess`
- `scalar018GaugeErrorIsNotSuccess`
- `scalar019CounterCheckedIoCauseAndOwnerRetained`
- `scalar020GaugeCheckedIoCauseAndOwnerRetained`
- `scalar021CounterNameAndValueEachReadOnce`
- `scalar022GaugeNameAndValueEachReadOnce`
- `scalar023MultipleFamiliesAndSeriesKeepSeparateMetadata`
- `scalar024ConcurrentCallsAndOtherSourcesDoNotShareState`

## ApiDurationMetricExporterTest（新24）

- `sumenc001LiteralCdfBecomesClassicHistogram`
- `sumenc002ZeroAndNanosecondSumAreNotIntegerTruncated`
- `sumenc003LabelsAreEscapedByOfficialWriter`
- `sumenc004FamiliesAndMultipleSeriesAreNotLost`
- `sumenc005EmptyAndUnselectedMetersAreNotFabricated`
- `sumenc006SelectedWrongMeterTypeFails`
- `sumenc007NamespaceAndLabelContractsRejectUnknownValues`
- `sumenc008NullBoundaryAndCollectionElementsFail`
- `sumenc009NegativeTotalCountAndInvalidSumFail`
- `sumenc010EmptyBucketsFail`
- `sumenc011NonFiniteAndNonPositiveBoundsFail`
- `sumenc012UnsortedAndDuplicateBoundsFail`
- `sumenc013NonFiniteNegativeAndFractionalCdfFail`
- `sumenc014DecreasingAndAboveTotalCdfFail`
- `sumenc015Binary64FiniteCdfAmbiguityFailsWithoutClamping`
- `sumenc016LongTotalCountAndExtremePositiveSumRemainPositive`
- `sumenc017SnapshotIsTakenExactlyOnce`
- `sumenc018BorrowedRegistryNeverClosedAndClosedInputRejected`
- `sumenc019ProviderRuntimeFailureIdentityIsPreserved`
- `sumenc020NullSnapshotAndBucketRejected`
- `sumenc021EmptyLabelSetAndMutableCallerNamespace`
- `sumenc022DuplicateProviderLabelRejected`
- `sumenc023CheckedWriterFailureRetainsCauseAndConstantMessage`
- `sumenc024WriterErrorIsNotCaughtOrNormalized`

## ApiMetricScrapeTest（必要反復14）

- `apipol001StandardReadsNoDetailedSourceOrValues`
- `apipol002RealInitialSixteenFamiliesAndNineHundredSamples`
- `apipol003IndependentSuppliedValuesAndCumulativeBoundary`
- `apipol004PureModeSwitchDoesNotResetOrClose`
- `apipol005EmptyCompatibleRegistryDoesNotFabricateUnknown`
- `apipol006UnsupportedSourceRejectedBeforeRead`
- `apipol007NullAndUnknownModesNeverReadSource`
- `apipol008ClosedSourceNotReopenedOrReadByStandard`
- `apipol009ProviderRuntimeAndErrorKeepIdentity`
- `apipol010LaterFailureNeverReturnsPartialText`
- `apipol011UnknownProvidersIgnored`
- `apipol012FiniteConcurrentCallsKeepSource`
- `apipol013AllThreeCodecsRejectPoisonedLabelsAndPolicyRecovers`
- `apipol014NameLabelsAndValueCapturedOnceInSameApprovedModel`
