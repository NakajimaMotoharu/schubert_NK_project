# NK-BAT-001 run退役実行結果

PG161/SSC055、PT-BAT-090～113。正式合格認定0、coverage未認定。正式対象source/branch/run/time/tool/command/exit/BUG/hashは全実行後に記録する。原本GCおよび親工程の完了へ算入しない。

探索記録（dev-foundationの未commit実装候補、正式sourceではない）:

- explore1: 2026-09-13 02:55:26 JST、record8件中7成功/1error、exit1。204byte markerのinode上限漏れをBUG171/YKT132へ修正前登録3edd9129。raw `/tmp/pgpt-retirement-explore1.log` SHA256 ee8bda090086984f3c1a013568448b2f9234ebc92a7b056dbcac26a00ce035b0。
- explore2: 03:03:55 JST、18.668秒、選択record8＋lifecycle14＝22件成功、exit0。全IO位置/公開削除crashの2件と全coverage/static/全reactorはこの実行に含めない。raw `/tmp/pgpt-retirement-explore2.log` SHA256 e1c41904336a275a0a6fe6d81478342b2a515c53fa0167e64e3ae8f91a95447a。JDK25.0.4/Maven3.9.12/PG18.6、OS/tool詳細421。
- review: BUG172/YKT133（先行0cb34dd0）は上記22成功から見つけられなかったpower-loss順序の不備。original不在の同期をplan消去前へ移し、metadata-onlyの実FD別sync順序/各同期失敗/再試行を追加する。修正後は全24件・旧部品・4coverage/staticを再実行するまで未検証。
- 実行commandはoffline Maven、`-pl src/schubert-nk-batch -am`、`-Dtest=LinuxFileLockTest,MaintenanceRetirementRecordsTest,MaintenanceRunRetirementTest#...`の選択試験。最終完全command/環境/source/hashは正式manifestへ記録し、この探索を正式証跡へ取り替えない。
