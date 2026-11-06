# NK-BAT-001 LogCleanupService transaction複合故障 単体テスト仕様書

- 関連: OPS-009/DAT-009、UI251、SS331 §3.14・SS332・SS341 §6.6/7.2/SSC337、BUG-2317/YKT-2062。設計正本origin/main854f0c1ac23ff01646b329c495d62ffce2a3c491 / PR205。
- Program/class/method: LogCleanupServiceのpublic execute/withOwner、constructor、transaction/check/owned/replace/known、SessionLease acquire/closeとChunkProgress。TestはLogCleanupTransactionPortTestの公開入口だけ、private抽出・reflection呼出なし。
- 状態: 試験設計・Test source作成中、実行未着手。旧source成功を新sourceへ加算しない。

## 独立oracleとfixture

Connection/PreparedStatement/ResultSetはJDKの自己所有memory proxy。DriverManager/DataSource/BatchDatabaseFixture、OS/DB/JMS/Root/VM、実鍵/credential/permit/intent/失敗cohortを呼ばない。SS331の固定SQLと出力列に基づく一行literal、queryTimeout固定値、正常/欠落/null/未知/複数行を用意する。既成功Production methodでexpectedを生成しない。

期待表の既知KはSQL・BatchRepository・CleanupStopped（fixture TIME_LIMIT）、未知UはIllegalStateException・NullPointerException・AssertionError。body SQLはRepository既境界の固定既知失敗を経由する。回復が正常なら元U identity・secondary0、Kは既reasonを保持。回復失敗はU primaryを同一identityで保持し固定DATABASE_FAILUREだけ一件、K primary＋U cleanupはU cleanup同一identity、K同士は固定DATABASE_FAILURE。回復故障後autoCommit=falseならSessionLeaseの独立失敗も同じ資源表で固定secondaryとなるため、U primaryの公開結果は固定secondary二件、K＋U cleanupは一件、K同士は最外側redact後0件。secondaryは新規・cause null・raw診断なし、元object自身へ追加しない。suppression無効ならsecondary0で同一primary、正常扱いしない。

rollback一回→正常時だけautoCommit復元一回、失敗時追加復元/commit/retry0。borrowed Connection close0。commit済み後の失敗はcommit1/rollback0でsummary返却0、durable mutationをrollback済みとしない。実DB永続後条件の実測はこのfixtureの証明外。

## Test ID群（Test source確定時にmethod/hashと一対一で結合）

|Test ID|目的/入力・操作|独立期待値・根拠|
|---|---|---|
|PT-BAT-LOGTX337001|constructor/API null、entry IRQ、時計負値/期限/計測中IRQ|契約拒否、INTERRUPTED/TIME_LIMIT、flag保持、DB作用0|
|PT-BAT-LOGTX337002|空完了・未完→次chunk完了・hold累積|固定counts/exit0又は10、commit回数、normal回復なし|
|PT-BAT-LOGTX337003|LOCK_BUSY/BACKUP_GATE|元停止reason、rollback復元後のみ解放|
|PT-BAT-LOGTX337004|累積不足/前回累積競合|固定DB失敗、未commit、rollback一回|
|PT-BAT-LOGTX337005|lock行欠落/null/false/複数|固定失敗/LOCK_BUSY、取得済flagに応じた解放|
|PT-BAT-LOGTX337006|unlock行欠落/null/false/複数|summary未返却、固定DB失敗、借用close0|
|PT-BAT-LOGTX337007|body K/U×回復正常|前述K/U表、元U identity、rollback→復元|
|PT-BAT-LOGTX337008|body六型×rollback六型|前述独立36-vector表、復元0、未知identity/固定secondary|
|PT-BAT-LOGTX337009|body六型×復元六型|前述独立36-vector表、rollback1/復元1|
|PT-BAT-LOGTX337010|同一未知objectの再送×rollback/復元|self-suppression0、元identity、fresh固定secondary|
|PT-BAT-LOGTX337011|rollback失敗の後条件|復元/commit/retry/borrowed close0|
|PT-BAT-LOGTX337012|五所有resourceのbody/close/同一/close-only競合|SS341327の独立225-vector、資源ごとの一度解放、未知primary/cleanup優先|
|PT-BAT-LOGTX337013|commit後owner既知/未知故障|commit1/rollback0、summaryなし、caller破棄条件|
|PT-BAT-LOGTX337014|正常commit後autoCommit復元故障|commit1/rollback0、未知identity/固定失敗|
|PT-BAT-LOGTX337015|開始setAutoCommit(false)自体の故障|開始成立を推測rollbackしない、追加commitなし|
|PT-BAT-LOGTX337016|withOwnerの既期限・固定timeout binding|同owner check、literal5s/5000・最大5、owner null拒否|
|PT-BAT-LOGTX337017|providerのnull statement/result|NPE契約非正常、未取得資源成功扱い0、借用close0|
|PT-BAT-LOGTX337018|別connection/別ownerの独立並行|各counts/result/close回数独立、同connection共有を許可しない|
|PT-BAT-LOGTX337019|suppression無効な未知primary|同一primary、cleanupの失敗を成功へ変換しない|

## 実施・品質・証跡

実行前にTest source/hashと各IDのmethodを確定する。既PG19740のMain-only normal JARで修正前redを一回採取し、原失敗を保存、期待表を変えずPG後の新source normal JARでgreenを実施する。共有selected-class qualifier一つを明示profileへ拡張して再利用し、javacはこのTestだけを指定する。RootFailed二Testを読取/compileせず、JUnit --select-classを固定、held四dynamic classの初期化hitを独立に確認する。

必要なMain-only Maven compile/NullAway・静的checkは実command/版/source/真正exitを保存。JUnit XML found/started/succeeded/F/E/S/abort、JaCoCo当source/session/全物理classを照合する。LogCleanupServiceのline/method/class/branch100%を要求し、未達は未完、abstract interfaceの実行code0は根拠を明記する。除外や旧exec合成、動的HOLDをPASSにしない。

原red、green、入力/期待/実際、environment/JDK25.0.4、branch/commit、tool hash、command/exit、BUG/SSC、coverage/manifest/hashをProgram017/evidenceの未使用runへ保存する。秘密/実session/token/DB dumpなし。全451/native/CHR/正式1964-53は別未完了であり、この限定PTでPGPT完了を宣言しない。

## 実行前凍結（Main未修正・Product実行前）

修正前CoreMain28af、normal PG19740。PG20102 TestだけのGJF/javac25 -Xlint:all -Werrorは真正0、Main再compile0/Test実行0。共有qualifierを既存profile不変の明示Log JSON一つへ拡張し、対象Test/正常JAR/dependencyを固定した。

|Test ID|class.method|
|---|---|
|PT-BAT-LOGTX337001|LogCleanupTransactionPortTest.boundariesAndDeadline|
|PT-BAT-LOGTX337002|LogCleanupTransactionPortTest.emptyAndLoop|
|PT-BAT-LOGTX337003|LogCleanupTransactionPortTest.knownStops|
|PT-BAT-LOGTX337004|LogCleanupTransactionPortTest.cumulativeDeltas|
|PT-BAT-LOGTX337005|LogCleanupTransactionPortTest.lockRows|
|PT-BAT-LOGTX337006|LogCleanupTransactionPortTest.unlockRows|
|PT-BAT-LOGTX337007|LogCleanupTransactionPortTest.bodyFaultsWithCleanRecovery|
|PT-BAT-LOGTX337008|LogCleanupTransactionPortTest.rollbackMatrix|
|PT-BAT-LOGTX337009|LogCleanupTransactionPortTest.restoreMatrix|
|PT-BAT-LOGTX337010|LogCleanupTransactionPortTest.sameFailureIdentity|
|PT-BAT-LOGTX337011|LogCleanupTransactionPortTest.rollbackGatesRestore|
|PT-BAT-LOGTX337012|LogCleanupTransactionPortTest.allResourceBoundaries|
|PT-BAT-LOGTX337013|LogCleanupTransactionPortTest.postcommitOwnerFailure|
|PT-BAT-LOGTX337014|LogCleanupTransactionPortTest.successfulCommitRestoreFailure|
|PT-BAT-LOGTX337015|LogCleanupTransactionPortTest.beginFailure|
|PT-BAT-LOGTX337016|LogCleanupTransactionPortTest.ownerTimeoutBinding|
|PT-BAT-LOGTX337017|LogCleanupTransactionPortTest.providerNullResources|
|PT-BAT-LOGTX337018|LogCleanupTransactionPortTest.independentConnectionsInParallel|
|PT-BAT-LOGTX337019|LogCleanupTransactionPortTest.suppressionDisabledPrimary|

Test SHA256 `c36d1626a09970c99ed9223c92644284a71cd9958def7e9b72e728476122c80b`、shared qualifier SHA256 `4f6e55731a119580f6f38f426790f766aead16bdc1dbd35928790ed1fe3bcffa`、red profile SHA256 `f81ece0ca9817d95b30ca188db882d6f932abf288a79ff1b382c7b0936042a24`、prepare manifest SHA256 `f21dd9cc0ea45f5c6f0e3015472cda2bcce9dacf210499b13657a68b483e7ad7`。実runではTest凍結commitを引数にしてGit object/hashを再照合し、JUnit exact class19件だけを選択する。既存DB fixture Testはcompile/実行しない。

## Green準備時のformatter差分

PG20116のTest compileは0。再度のGJF1.36.1がprogress role代入直前の改行/indent一箇所だけを変更し、追加のbyte同一assertは1で停止した。原red/Test c36d1626…はGit41e1ce63とPG20102/20104へ不変保全。現在Test12417a8b…は上記一箇所以外完全一致を独立byte置換比較で確認し、Java token/文字列/期待表/19methodは不変。Test classの行番号等は異なるため同一byteとは主張しない。evidence/PG20116-oracle-format-equivalence-v1/manifest.jsonに両hashと差分を保存。Green自身の入力/compile/source/classCRCを新たに固定し、その一runだけで判定する。旧red execは合成しない。

## 依存postと必要な再資格

PG20118は新D8の19件F/E/S0、L156/M15/C3/B68全miss0を計測したが、独立postは不要なstorage JARのclasspath混入で1となり未受入。原結果を保持し、既no-storage/no-native条件を変更せず、共有profileから不要JARだけを除いた。frozen Testはformat check-onlyへ固定し、PG20126 compile0・format検査0、Test source/全Test class byteはPG20116と完全一致。新profile712/PG20128で依存条件変更に必要な一回の再資格を行う。Main build/六SpotBugsと旧成功PTを確認目的で再演しない。原postの記録はevidence/PG20118-post-dependency-unaccepted-v1。

## Test静的規約の是正（BUG2318/YKT2063）

PG20127の58生指摘のうち15件（重複literal6/if literal7/field-handler同名2）を修正前起票し、独立fixtureの定数化・handler名だけ分離した。期待literal/制御条件/19methodは変更せず、format前の変換は逆変換で元sourceへ完全復元できることを確認した。PG20136 Test compile0、PG20137 PMD43/Checkstyle0/processing0。残43は各source/line/SSと目的を個別照合し局所適用違反0（抑制追加0）、全F03/451受入ではない。Main30件は所有資源/未知例外/IRQ確認、Test13件は自己所有thread9/Fixture独立map3/JDK Proxy loader1の目的である。詳細evidence/PG20137-log-tx-static-context-v1。

Test版変更に必要なwhole19再試験/単一exec四counter/strict postはprofile713・PG20138へ固定する。Main D8のbuild/NullAway/6SBはbyte不変なので再実行しない。BUG2318は再資格未完、PG20128の限定成功は別証跡として保持し加算しない。
