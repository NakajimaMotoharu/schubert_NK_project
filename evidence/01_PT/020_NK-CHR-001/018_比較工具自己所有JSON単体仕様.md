# 比較工具 自己所有JSON単体仕様

Program NK-CHR-001、WBS-P020-01親・費用leafP020-01.02（484比較/DIFnegative）、UI264/SS355§8/12・QA051/054。対象ArtifactComparatorとComparisonResultの全1source/2physical。製造reviewでは既24case/16DIF限定比較を確認し、empty JSONのNPE仮説は原21090で不成立のためMain変更不要と判断する。原診断のIOException必須というTest仮定はSS355の明示FAIL契約で訂正しBUG2373/YKT2118へ管理、Production/期待値の都合変更なし。

自己所有TempDirのsynthetic project/Current/NK/observationsだけを読み書きする。公開catalog・DIF allowlist設計JSON2fileをGit byte固定しdesign-only私有copyへ置き、既Test SOURCE_ROOTを当copyだけへ向ける。compareのprojectRootはさらに各Test自己所有fixture、実repoを渡さない。real Current baseline/capture/adapter/Browser/DB/JMS/Root/VM/held四へアクセスしない。既Test内GateCliは明示compare-nk分岐だけで自分のJSONを出力し、capture/run/promote-currentを呼ばない。CorrelatedLogEvidenceValidatorTest.fixtureは純粋JSON入力のcompile-only helperで当16Testをselectしない。

現在のstrict source proof未登録に加え、原execution-kit6b53にはCorrelatedValidator自体が無く、現在のQA054依存/fixtureを含む比較器の再認証が必要（PMO600041）。旧ArtifactComparatorTest8を新規実装数へ加算せず、新EOF1＋結果collection境界1と分離する。成功全回帰の確認再演はしない。期待値は独立ORACLESの24case/16rule/14raw差分・16観測/field/mode/selector/valueと公開correlated入力、SS355の不合格条件をliteral化し、比較器自身でexpectedやマスクを生成しない。原21090の1/F1/OS1/source087はそのまま保全する。

|Test ID|class.method|目的・入力・独立期待|
|---|---|---|
|PT-CHR-CMP001|ArtifactComparatorEmptyInputTest.emptyJsonInputsFailClosedWithoutNullDereference|新規1: catalog/allowlist/observations/Current/NK各empty・whitespace→FAIL/該当理由/比較件数、NPE無し|
|PT-CHR-CMP002|ArtifactComparatorTest.acceptsTwentyFourPassCasesAndExactlySixteenApprovedDifferences|既method source再認証: 独立24/24case・16DIF/14raw/16observation・未登録未使用0・自己所有CLI出力part残0|
|PT-CHR-CMP003|ArtifactComparatorTest.rejectsNullMissingAndWrongInputTypesWithoutNpe|既method source再認証: 全4引数null/dir-file型違い・明示拒否/NPE無し|
|PT-CHR-CMP004|ArtifactComparatorTest.reportsCatalogArtifactStatusSetSymlinkAndUnregisteredDrift|既method source再認証: catalog/case/status/集合/symlink/JSON object-array差分を限定FAIL|
|PT-CHR-CMP005|ArtifactComparatorTest.rejectsMalformedObservationEnvelope|既method source再認証: version/配列/重複envelopeの不合格|
|PT-CHR-CMP006|ArtifactComparatorTest.rejectsUnknownOutOfScopeBroadWrongOverlappingAndUnusedObservations|既method source再認証: 未知DIF/case/範囲/広いpointer/field/mode/selector/value/missing/overlap/unused拒否|
|PT-CHR-CMP007|ArtifactComparatorTest.rejectsMissingOrUncorrelatedL01ProjectionEvenWhenDifClaimsAreValid|既method source再認証: 欠落/不相関L01/Current-NK artifact紐付け不一致を拒否|
|PT-CHR-CMP008|ArtifactComparatorTest.rejectsNonIntegralOrOversizedObservationVersions|既method source再認証: 非整数/過大version拒否|
|PT-CHR-CMP009|ArtifactComparatorTest.lexicalArtifactNamesRejectNullAndNamelessPathsBeforeDereference|既method source再認証: null/nameless artifact pathを明示拒否|

|PT-CHR-CMP010|ArtifactComparatorEmptyInputTest.comparisonResultOwnsImmutableNonNullListSnapshots|追加発見の新規1: four list入力snapshotの防御copy/不変・各list NULL/要素NULL拒否、結果型constructorのinvariant|

全10同source一run・選択2Testclass/helper1 compile-only。全F/E/S/flaky/abort/not-run0、全physical2 line/method/class/branch100/CRC通常jar/単一session、手動除外/旧exec合成無し。工具counterを六Production Main/実CHRの成功やcoverageへ合算しない。合格/不合格結果のimmutable listも既仕様に沿って確認する。比較はlocal同期処理、DBtransaction/業務再送は非該当、複数自己所有fixtureを分離し順序/集合/全JSON shape差分を確認する。

JDK25.0.4/Maven3.9.12、normal21088はtool Main5/物理10をTest/baseline/capture内容取得前に除外してbuild。実compile CPをoffline Mavenで解決したJackson2.19.2三jar/Jspecify/JUnitだけで、PostgreSQL/Playwright/本番App jarをruntime CPへ入れない。SpotBugs当tool Main5/10class指摘/欠落/解析error0と対象Main+新旧Test/helper PMD-CSを組合せる。Test定数だけの修正ならMain/jar同byteのSBは参照し再演しない。BUG2374/YKT2119のcatalog位置literal1は修正前登録・CATALOG定数化、全raw指摘の個別適用性を記録し抑制しない。

Command: 020/input002 prepare→static→source固定→run <source>→post <source>→独立post。実日時/OS/JDK/tool/branch/source/command/終了code/input/expected/actual/XML/CRC/counters/BUG/hashはmanifestと019結果。SDK class-init/Jar/JDK metadata/syscalls全0を主張しない。Null/欠落/空/未知はSpotBugsとnegativeで組合せる。実CHR-A01/L01/G01～G06・QA051final・Browser/IT-ST/全451は別未受入、fixtureのPASSを実NK/Current合格へ変換しない。

結果recordのimmutable/null契約を当source constructor reviewで追加確認が必要と判定しCMP010を追加。新規method2/既8再認証を区別、群開始見積1/3/6 cap8は不変更、元9想定・旧compile/staticは保全する。Main変更は不要でTestと期待値補完だけ、既Main五/10class SpotBugs0はbyte一致で再利用する。
