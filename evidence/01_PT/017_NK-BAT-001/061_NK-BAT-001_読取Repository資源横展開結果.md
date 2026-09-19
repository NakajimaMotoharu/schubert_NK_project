# NK-BAT-001 読取Repository資源横展開結果

探索log SHA256: red=`550f507e2b3292e0042693bdc9cbcc2728df0825fc73ac0f3120ac913bcec797`、green=`282ddca6305bebe3c9d120a776095f01d8b45311838426f6b89584055d8ea2d7`。原logは/tmp、正式manifestは次の単一clean verifyから生成する。

PG179/SSC063/BUG195・206/YKT154・162、060/BAT087・121。正式未認定。

修正後 `/tmp/pgpt-pg179-green.log`、00:39:34 JST/37.681秒/exit0。Storage8＋Batch28（Log12＋read-only16）の36 PT成功、failed/error/skipped0。新136複合・元4反例とPG178の225複合も成功。新JdbcResourceFailuresは1class/1method/4line/8branch、変更RunReference1/4/52/24・Summary1/4/55/24、全missed0。NullAway/Enforcer/Spotless/SpotBugs成功、抑止/coverage除外なし。JDBC4scopeの実live0/close各1・借用Connection不変更・元projection/NULL/歴史UTC/lock・並行を確認した。次の全reactor/同source認定前で新JUnit/部品加算0、広域YKT154/162は未完了。

修正前 `/tmp/pgpt-pg179-red.log`、2026-09-20 00:36:00 JST/11.514秒/exit1。Storage8成功、対象2JUnitは各2反例が失敗。providerのIllegalArgumentException単独とrow.next/row.close同一IllegalStateExceptionの双方で、期待元identityに対し実際BatchRepositoryExceptionへ置換された。公開合成例外だけを使用、実JDBC resourceはclose後に故障を注入。Production sourceはe80a3cb5/仕様282dc191のまま、test追加のみ。再現commandは060の選択から `ResourceScopeTest,RunReferenceRepositoryTest#interruptionAndRuntime,InspectionSummaryRepositoryTest#interruptAndRuntime`、goal=testへ限定。

これらの失敗を合格へ含めない。次は4 JDBC scopeのdirect finally close、狭いmodel validation catchと136複合、既存全16件・PG178の225複合・全coverage/staticを再試験する。広域候補が残るためBUG195/YKT154/SSC063、YKT162全体は継続する。
