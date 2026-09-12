# NK-BAT-001 run退役実行結果

正式認定: PT-WEB-20260913-04、source956a2f47c04730c940dc15b0817721b1c7848b49/dev-foundation、2026-09-13 03:33:29～03:48:59 JST、exit0。全1247 PT（Batch183）のうち新規BAT090～113の24件がすべて成功、failed/error/skipped0。Batch58class/309method/1699line/843branch missed0、全6 moduleの4coverage100%、Production5静的解析未解決0。全13collector/36scopeと017・019の24負canary成功、BUG171～174/YKT132～135完了。GC部品を認定するが親結線/SSC055全体・実reboot・IT/STは未完了。

実行command/environment/source/期待値/実際値は evidence/manifest.json と input/run-retirement、output/run-retirement の5golden・6768位置inventoryを参照。hashはmanifestとchecksums.sha256で一意に追跡する。全実行commandは421指定JDK/M2のoffline `./mvnw --no-transfer-progress clean verify`。raw log /tmp/PT-WEB-20260913-04.log SHA256 467c3707a36af8f04f9d4bc38e9756a6164050b1662be7107dc93b8abf23d8f5。以下の未認定表現は探索時点の履歴である。

最新探索e0a31cb2（正式認定前）: 全Batch183/Storage58成功、failed/error/skipped0、2026-09-13 03:28:23 JST終了、8分02秒、exit0。Batch58class/309method/1699line/843branchすべてmissed0、6,768全IO位置を実行。コマンドは421のJDK/M2を指定したoffline `./mvnw -pl src/schubert-nk-batch -am test org.jacoco:jacoco-maven-plugin:0.8.15:report`。raw `/tmp/pgpt-retirement-explore6.log` SHA256 ba851009a27987babeb8f80dcbfb24ccd43d824c9d463b4d6c0cdbd9ca10e1fc。

静的解析: compile＋SpotBugs checkを同reactorで実施、03:30:48 JST終了/12.441秒/exit0、指摘0（raw `/tmp/pgpt-retirement-static7.log`）。先行static6のgoal単独実行はstorage jar未解決で非成功だったため合格に数えない。compile phase付きで依存を確定して再実行したもので、PT skipやoffline依存を外していない。

BUG174/YKT135: 実IO証跡とcollectorの照合でlocale順序の期待値不備を検出し先行435bd5f5で登録。ASCII/Java自然順へ修正し、旧誤順序を拒否する負例・実5golden＋IO証跡の再照合・019の23canaryを成功確認。詳細はevidence/logs/BUG-171-174-YKT-132-135.md。全module正式run04と13collector/36scopeを完了するまではPG/PT正式完了へ加算しない。

PG161/SSC055、PT-BAT-090～113。正式合格認定0、coverage未認定。正式対象source/branch/run/time/tool/command/exit/BUG/hashは全実行後に記録する。原本GCおよび親工程の完了へ算入しない。

探索記録（dev-foundationの未commit実装候補、正式sourceではない）:

- explore1: 2026-09-13 02:55:26 JST、record8件中7成功/1error、exit1。204byte markerのinode上限漏れをBUG171/YKT132へ修正前登録3edd9129。raw `/tmp/pgpt-retirement-explore1.log` SHA256 ee8bda090086984f3c1a013568448b2f9234ebc92a7b056dbcac26a00ce035b0。
- explore2: 03:03:55 JST、18.668秒、選択record8＋lifecycle14＝22件成功、exit0。全IO位置/公開削除crashの2件と全coverage/static/全reactorはこの実行に含めない。raw `/tmp/pgpt-retirement-explore2.log` SHA256 e1c41904336a275a0a6fe6d81478342b2a515c53fa0167e64e3ae8f91a95447a。JDK25.0.4/Maven3.9.12/PG18.6、OS/tool詳細421。
- review: BUG172/YKT133（先行0cb34dd0）は上記22成功から見つけられなかったpower-loss順序の不備。original不在の同期をplan消去前へ移し、metadata-onlyの実FD別sync順序/各同期失敗/再試行を追加する。修正後は全24件・旧部品・4coverage/staticを再実行するまで未検証。
- 実行commandはoffline Maven、`-pl src/schubert-nk-batch -am`、`-Dtest=LinuxFileLockTest,MaintenanceRetirementRecordsTest,MaintenanceRunRetirementTest#...`の選択試験。最終完全command/環境/source/hashは正式manifestへ記録し、この探索を正式証跡へ取り替えない。
