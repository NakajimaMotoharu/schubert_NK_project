# NK-CHR-001 比較scan二是正・通常工具試験仕様

Program: GateCli.containsAny/secretScan/prefixes、ArtifactComparator.compare。関連RD互換・秘密保護、UI264、SS355 §8/§9/20260901binary検査強化、451、BUG2811/2812、YKT2403、WBS-P020-01.01/.02/.03。Production src eeba9dd506は変更しない。

PT-CHR-G06-STREAM-001: TempDir所有の10MiB+37byteを0xffで埋め、UTF8固定markerをoffset0/8191/末尾へ独立配置する。全3位置で含有true、異末尾/空needleはfalse。aaaaabからaaaab=true・aaaaac=false、空file/空list=false、nullPath/list/要素=IllegalArgumentException、欠落file=IOException。fixture usersは固定合成markerだけ、11MiB弱reports末尾に配置してsecretScan結果を固定相対path一件とする。production searchでexpectedを生成しない。外部credential/master/Current/NK/VM/DBなし。

PT-CHR-DIF015-001: 元24case/16DIF/相関正例fixtureからDIF015のNKとexpectedNkだけを/changed-pathへ変更。期待失敗はCONTRACT_CHANGED一件、未登録CHR-A01:/dif/DIF-015、未使用DIF015で計3件・他失敗0。別fixtureはDIF001のexpectedNkだけwrong-expectationとし、NK_VALUE・未登録CHR-U01:/dif/DIF-001・未使用DIF001計3件。単独原因であり、重複claimや他失敗で欠落を覆わない。元allowlist/Currentbaseline不変。

通常実行はwhole ArtifactComparatorTest9/GateContractTest8/GateContractValidatorNegativeTest17（10plain+7parameter）/TargetAdapterTest3/CorrelatedLogEvidenceValidatorTest9、計46予測。元44invocationと期待値を保持、新定義2。GateCliTest whole12は実空き20GiB前提を満たせずHOLD、抽出method/fake容量/skipで合格へ変換しない。全5Main物理classをcoverageへ含め、未網羅を保持。選択46成功だけでは全工具coverage100/451/実CHR/正式1964-53を更新しない。

Root固定Java25/Maven offline testとJacoco reportを同一snapshotで実行予定。verify bundle100 checkは未達前提のため未実行HOLDとして明記し、要求は変更しない。source/run/command/exit/XML/四counter・静的結果・baseline前後hashは結果manifestへ記録する。実行前の状態NOT_RUN。
