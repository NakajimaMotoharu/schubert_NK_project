# PG309 security横断回帰：修正前不合格保存

Source `3002ab8f9` / dev-foundation、2026-09-28 00:49:39 JST終了、exit1。SSC092のshared credential/NSS/Unit security変更、D01/04/05がtrigger。開始からXML/hash収集までsource/test/settings/tools差分0。

Protocol80/Storage149/Bootstrap127/API734/Web555/Batch476、計2121PT実行、failure1/error0/skip0。Batch CleanupRepositoryTest.moduleDependencyBoundaryがBootstrap所属Loaderの旧api.file packageをAPI依存と誤判定した。BUG276/YKT209を修正前起票。全suiteのhash/件数/失敗case、source inventory digest、log hashは `evidence/provisional/PG309-regression-RED/manifest.json`。Batchはtest失敗後report/static未到達（null）、前回結果を流用しない。他5module static0。

本結果は不合格で正式認定しない。既知native/main coverage gapを除外せず、formal run24/source858713c/1964PT/53scope/中心48.3%を変更しない。修正後は関連境界PTと105canary→必要回帰を行う。Production依存/POM/上位仕様を変更しない。
