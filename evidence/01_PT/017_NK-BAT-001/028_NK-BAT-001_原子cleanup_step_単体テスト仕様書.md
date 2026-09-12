# NK-BAT-001 原子cleanup_step単体テスト仕様書

独立JDBC inventory（実装適用前にSQL/資源順序から計数）: 前後RunReference各16=32、V020 queryはprepare1/timeout1/bind7/execute1/next2/get7/close2=21、合計53。method map: connection.getAutoCommit/isReadOnly/getTransactionIsolation各2、prepareStatement3、statement.setQueryTimeout3/setObject7/setLong1/setInt2/setString1/executeQuery3/close3、row.next6/getObject14/getString1/close3。known/unknown累積/FKの型値は違っても全7列を読むため正常観測53。各SQL故障positionは固定map全発火と所有0/rollbackを確認し、実mapからexpectedを生成しない。

PG164/SSC057（先行78bde51a）、OPS009/DAT009/UI251 §6・11・12/SS331 §3.14/332/341。PG163正式07中はsource/collector変更禁止、現在は仕様のみ・未実装/未実行/認定0。既存V001～019/削除predicate/保持/Current baselineは変更しない。

| Test ID | class/method | 目的・事前条件/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-162 | CleanupStepRepositoryTest.actualSevenKindsAndStepTotals | 実PG/全7kind・同step複数kind・chunkと保存累積/END/限定7bind7列を独立SQL確認 |
| PT-BAT-163 | CleanupStepRepositoryTest.borrowedStateAndMapping | autoCommit/RW/READ_COMMITTED/自己lock/fullhandle/kindstep/LOGS/skip/null前条件・借用connection不変更 |
| PT-BAT-164 | CleanupStepRepositoryTest.nullAndProjection | 7列の各NULL/片側NULL/型・0/複数row・未知reason/件数/complete不整合・nullstatement/rows拒否 |
| PT-BAT-165 | CleanupStepRepositoryTest.allJdbcFailures | 独立JDBC固定call mapを別途SS/資源順序から計数して全位置・複合close発火/所有0/rollback検証 |
| PT-BAT-166 | CleanupStepRepositoryTest.rejectionReasonsAndUnknownTotals | gateLOCK/BACKUPのoptional emptyを0にしない、FKdeferredだけ保存累積既知、正常へ正規化しない |
| PT-BAT-167 | CleanupStepRepositoryTest.utcFullHandle | 手書SQL年0001/1582/1900/1970/9999・3timezone/µs・id/attempt/started/run/dayの完全束縛 |
| PT-BAT-168 | CleanupStepRepositoryTest.interruptRuntimeAndResourceOwnership | 開始/最終interrupt保持、SQL/IAE固定redact、unknownRuntime/NPE/Error伝播・全ownedclose |
| PT-BAT-169 | CleanupStepRepositoryTest.concurrentTransactionsAndRollback | 別TX/owner/advisory/step rowlock、commit前不可視・rollbackのDELETE/累積同時復元/同handle再読 |

Fixtureは隔離PG18.6/Flyway/JDBC42.7.13・公開literal run/handle/時刻/件数のみ。期待値はSSの固定SQL後条件/候補predicate/型・byte/手計算差分/固定JDBC呼出表で別途定め、Productionの出力・観測mapからexpectedを生成しない。正常/境界/異常/例外/NULL/未知/割込/再送/並行/commit不明を全分岐で網羅する。故障は修正前915、共通原因は916、設計修正はSSC057等へ先行する。

実行は421 JDK25.0.4/Maven3.9.12/M2を用いるoffline Mavenの該当module -am test/clean verify。対象commit/branch/command/日時/OS/tool/終了code/input/期待・実際/line・method・class・branch100%/static/BUG・SSC/証跡path・SHA256を029_NK-BAT-001_原子cleanup_step_実行結果.mdとmanifestへ実行後記録する。failed/flaky/skipped/not-runは合格にしない。未実装の親OS/実子/実backup/通常Question/pending revoke・全cleanup順序を本部品の試験だけで完了にしない。
