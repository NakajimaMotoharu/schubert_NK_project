# 693 SSC304 Expiry既成功監査・JDBC所有scope単体テスト仕様

Program NK-BAT-001 / WBS-P017-11、ExpiryAuditRepository.successful/verifySuccessfulAudit/usingJdbc/内部JdbcRelease・JdbcRead。RD DAT-009/OPS-009、UI251、SS331§8/341§9/343 SSC304、設計PR150/main c7325c55f。実効Java25旧bytecodeの未網羅3分岐を確認済み。変更は既末尾比較とnonnull資源scopeの分解のみ。SQL/順序/期限/借用Connection/例外redaction・既strong read不変更。

| Test ID末尾（PT-EXP-4956-） | 独立入力・操作 | 期待値の根拠 |
|---|---|---|
|001|literal SUCCESS、ended=observed/1ns前|正常、時刻境界は固定UTC literal|
|002|WARNING/FAILED/RUNNING/UNKNOWN/空/小文字|固定BatchRepositoryException、cause/suppressedなし|
|003|SUCCESS・ended null|拒否。内部predicate負試験であり不正DB受理ではない|
|004|ended=observed+1ns|拒否|
|005～006|code/summaryが空または公開synthetic文字列|拒否/診断漏洩0|
|007～008|snapshot/observed null|即契約拒否。NPEを正常化しない|
|009|正常body/close|同一Optional、body→close各一回、close成功前返却なし|
|010|body SQL/IO/Runtime/Error|同一primary・close一回・suppressed0|
|011|正常body＋close SQL/Runtime/Error|同一close例外・成功へ変換なし|
|012|body四型×close三型の12組|同一primary/secondaryと順序。ProductionでなくJava25 compiler TWR参照と比較|
|013|nested rows/statement＋body IO/close SQL・Error|body→rows→statement、元IOのsuppressed=[rowsSQL,statementError]|
|014～015|null release/read|body/close未実行で拒否|
|016|body/closeが同じSQLException object|Java TWR同様IllegalArgumentException/cause元同一・自己suppressed追加0|
|017|release port null|body未実行で拒否（014はowned resource null）|
|018|実admitted resourceをreleaseへ引渡す|同一objectだけを一度close、別資源に置換しない|

Fixtureは公開合成時刻/例外だけ。既ExpiryAuditRepositoryTest・MorningExpirySession/ObservationInvariant・CleanupExpiryExecutionTestは専用PostgreSQL18.6/現DDL/borrowed Connection/実SQL・rollback/整合を独立確認する。storage/bootstrapの実suiteも選択しstrict NoTestsを保持。通常Mainにtest authority/CLI/ENV/permissionを追加しない。並行/再送は既同日元run参照・session/owner試験を併用し、pure helperがDB/OS成功を確証したとは扱わない。

command: `PYTHONPATH=tools/quality python3 -B tools/quality/pg4956_expiry_success_selected.py`。clean commitを新専用snapshotへarchive、全対象format成功→選択PT→fresh JaCoCo/SpotBugsの順。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0/GJF1.36.1/NullAway-Werror。Test IDはsuite/methodから一意に対応。元command/start/end/終了code/XML/hash/counterはPG4956 manifestへ保存、rawログはprivate/公開は許可列のみ。特にhelper二method＋successful内部bodyのline/method/branch未網羅0を要求。line/class/method/branch全program100は別未受入。

全選択Main byteを旧04bb全体の実PG4846と比較し、ExpiryAuditRepository外側1class変更＋同class宣言二interface追加だけを許容。他749Main不変を要求。旧native/3761を候補へ加算せず、Main変更群をまとめてfresh全回帰と新source正規配備/nativeを後続受入する。PG4952 test-only109は独立保存し算術3767等を作らない。Failed/flaky/skipped/not-runは合格へ算入しない。実結果/関連障害は694へ追記。

counter適用性：usingJdbcは明示条件分岐のないcatch/rethrow scopeで、JaCoCoにBRANCH counterが存在しない場合は非適用（0実測と捏造しない）。LINE/METHODは必須0miss、BRANCHが存在すれば別途miss0を検査する。verifySuccessfulAudit/元successful内部lambdaは実BRANCH counterの存在と0missを必須とする。全プログラムの例外・条件網羅や四counter要求を免除しない。

BUG1397/1398後の追加前提：owned resourceをgeneric scopeへ明示し、`WillClose`は実装どおりの所有契約（抑制annotationではない）。同一resourceを型付きreleaseへ渡してcloseする。実DB/zero-liveFDと例外matrixを再試験しfresh SpotBugs0を要求する。条件bodyはJava25実`lambda$successful$2`/ResultSet先頭signature/8BRANCH、外側$1は無条件設定bodyなので誤指定しない。修正後commandは`PYTHONPATH=tools/quality python3 -B tools/quality/pg4960_expiry_success_selected.py`、全53PT/7suite予定（旧35＋新18）。Main/Testsourceは新commit、旧4958は51PT成功部分だがstatic2/Maven1・資格1のまま保全。

## SSC304取得scope追補後の現行仕様（旧試行は上記の履歴として保存）

design-only main8a02a6eb20d1fafc5a63b60c888ea3bb732cfc68/PR151。限定read-onlyレビューは実bytecode/SpotBugs4.10.4 detectorを確認し、取得後のcallback構築中Errorが旧helperのtry外にある実gapを特定した。全acquire/release/read port構築とnull検査を先行し、helper内で取得→既required→直ちにtry/readへ入る。nested row port構築はouter Statementの所有scope内。WillCloseはもはや資源引数がないため除去、ルール抑制0。null取得戻りは元BatchRepositoryException（014期待をこの既契約へ一致）、port nullは取得前NPE契約拒否。SQL/read/owner/期限とJava TWRの未知identity/self-suppressionは不変更。

現行新24件＋関連35件=**59PT/7suite**予定。019:null acquire port→body/close0。020:acquire SQL/Runtime/Error→同一throwable/body-close0。021:全port構築→acquire→body→closeのliteral順と両portへの同一resource。022:inner self-suppression→IAE(cause元P)にもouter失敗Sをsuppressedしrows→statement各一回。023:同一secondary Q二回を[Pのsuppressed Q,Q]として保持・dedup0。024:body-port構築のsentinel Errorでacquire/close0（JVM OOMを起こさず実言語評価順の反例）。既001～018/実DB全suiteを同一snapshotで再実行する。

現行command=`PYTHONPATH=tools/quality python3 -B tools/quality/pg4972_expiry_success_selected.py`。Main宣言は内部Acquire/Release/Read三件、全六Main予定1650、当選択三module753。strict byte比較は旧750の749不変＋外側一class変更＋新三interfaceのみ、全941ソースartifactの差は当一fileのみ。BUG1401のformatter HANDLE再flowを旧一行へ戻し、CLI --skip-reflowing-long-stringsでSpotless規約自体を変えない。record三件をdebug差として受入/除外せず再生成byte一致を要求。

測定対象の条件bodyはsynthetic ordinalを推測せず、実lambda名prefix＋末尾明示ResultSet引数/Optional戻りdescriptorで一意に選び、実8BRANCHと0missを必須にする。実compiled name/descも証跡へ記録。helperのcatch-only BRANCH非適用は維持、例外matrixは全24に含む。fresh三module static0・format0・59/7全成功後だけ限定公開する。whole/新source native/全program四counter100/正式は別未受入。
