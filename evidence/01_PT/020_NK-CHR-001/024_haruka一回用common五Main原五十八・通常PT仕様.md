# haruka 専用一回用common5 Main・原58件通常PT

NK-CHR-001/WBS-P02001/F03/F04・TST004/UI355/SS355/451、仕様022/023を継承。対象MainはArtifactComparator/GateCli/GateContractValidator/TargetAdapter/CorrelatedLogEvidenceValidatorの全5/10physical。全6Testをmethod抽出せず原class全体で選択: ArtifactComparator9/Gate12/GateContract8/GateContractValidatorNegative17/TargetAdapter3/CorrelatedLogEvidenceValidator9=58。新JUnit定義0、旧46との合算なし。BUG2873 GateworkerとBUG2876 Correlatedworkerの所有期限を是正し、原全literal/入力/期待JSON/Main不変を独立照合する。

GateContractTestはCharacterizationEnvironment.renderCaddyConfigをstaticに呼ぶ。このtest helperは全classを同byteでcompileするが、instance生成/field初期化/start/close/DB/Socket/Process/Playwright等のlive methodは呼ばない。static initializerなし、renderはPath/portから文字列を作るだけ。helperのlive方法を分離/替玉/別sourceへ置換しない。Native/Current Test本体/Root2Test/Actual4classや実原本/鍵をsnapshot/compile/selectに入れない。

Snapshotは固定GitからMain5/Test6/必要whole helper CharacterizationEnvironment・既public tests/resources、Current baseline27/report固定入力、root/characterization/module POM・.mvn/mvnwだけ。各byte/hashとpath集合をtransport前後照合、元baselineをread-only保持。新規runは正規haruka/miniと専用strict knownHosts、既/opt JDK25.0.4/Maven3.9.12。同host既jobや不可視cwd3を読取/停止/成功認定しない。新規一回用namespaceをO_EXCL0700・flockで所有、boot/PID/startTicks/source/archive/budget/terminalを固定、Maven repositoryはpublic既cacheから当run専用copy（元cache変更0）、source/current/originalDB/サービスへ触れない。準備/実行が既存なら再発行せず元receiptを観測する。

実高disk20GiB以上にsource target/preflight、実低tmpfs20GiB未満に当runのJunit tmp（起動時JAVA_TOOL_OPTIONSでMavenとforkへ同じtmpを固定）。空き/mock/期待値変更で合わせない。CPU/RAMは4/6.7GiB基盤、MavenXmx2g・fork/java同時数とmemory現値を確認。SSH/root/permit/Unit/VM/アプリ/DB/native/Current capture/実業務CHRは禁止維持、aru接続照会全面禁止。

通常Root compiler/NullAway/lint-Werror/Spotless、full root PMD/CS/SBとsource別適用性、JUnit XML真終端/58全件FES0・独立期待値・全10CRC/初期化/四counter/実JVMCode/同source/単一execを確認。未網羅・不合格は原値を保存しPT合格へ算入しない。helper Test codeの未評価、生成filter等をglobal451未完として残す。raw私有Mavenlog/認証情報はGitへコピーせず、必要XMLはproperties除去・原hash保持、実coverageに代替確認や旧execを混ぜない。必要追加試験/是正は別原因/見積りで記録。

追加見積り.8/2.4/4.8= workerREWORK.1/.3/.6 + 新haruka専用runner/tool.3/.9/1.8 + 通常58/static/独立post.4/1.2/2.4。元資格の残所有.05/.15/.3は追加せず内数に併記し、総群.85/2.55/5.1 cap6、一群10以内。S/V/原費用・原群見積り保持、共有混合消費と専有token欠測nullを区別。実Root/DB/業務CHR/全PGPT受入・ITST完了0。
