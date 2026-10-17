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

Fixtureは公開合成時刻/例外だけ。既ExpiryAuditRepositoryTest・MorningExpirySession/ObservationInvariant・CleanupExpiryExecutionTestは専用PostgreSQL18.6/現DDL/borrowed Connection/実SQL・rollback/整合を独立確認する。storage/bootstrapの実suiteも選択しstrict NoTestsを保持。通常Mainにtest authority/CLI/ENV/permissionを追加しない。並行/再送は既同日元run参照・session/owner試験を併用し、pure helperがDB/OS成功を確証したとは扱わない。

command: `PYTHONPATH=tools/quality python3 -B tools/quality/pg4956_expiry_success_selected.py`。clean commitを新専用snapshotへarchive、全対象format成功→選択PT→fresh JaCoCo/SpotBugsの順。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0/GJF1.36.1/NullAway-Werror。Test IDはsuite/methodから一意に対応。元command/start/end/終了code/XML/hash/counterはPG4956 manifestへ保存、rawログはprivate/公開は許可列のみ。特にhelper二method＋successful内部bodyのline/method/branch未網羅0を要求。line/class/method/branch全program100は別未受入。

全選択Main byteを旧04bb全体の実PG4846と比較し、ExpiryAuditRepository外側1class変更＋同class宣言二interface追加だけを許容。他749Main不変を要求。旧native/3761を候補へ加算せず、Main変更群をまとめてfresh全回帰と新source正規配備/nativeを後続受入する。PG4952 test-only109は独立保存し算術3767等を作らない。Failed/flaky/skipped/not-runは合格へ算入しない。実結果/関連障害は694へ追記。

counter適用性：usingJdbcは明示条件分岐のないcatch/rethrow scopeで、JaCoCoにBRANCH counterが存在しない場合は非適用（0実測と捏造しない）。LINE/METHODは必須0miss、BRANCHが存在すれば別途miss0を検査する。verifySuccessfulAudit/元successful内部lambdaは実BRANCH counterの存在と0missを必須とする。全プログラムの例外・条件網羅や四counter要求を免除しない。
