# PT-OPS-BFENCE-NIO001 / deterministic NIO collision

Program NK-OPS-001、BackupStartIntentFiles.begin/requireClear、OPS009/UI251/SS343354。Productionは変更しない。原4056/1396で同Mainの240/241行が並行fixtureの経路によって未実測となったため、既承認CREATE_NEWの拒否を自己所有TempDirで確定させる。既試験の結果はflakyではなく、未実装機能やProduction障害とは分類しない。

新BackupStartIntentCollisionTestの一@Test。fixtureのrequireClear最後gate（第2回）で空0600 markerを新規作成し、その後のbeginのCREATE_NEW collisionを必ず発生させる。独立期待はIOException、gate2、元inode同一・bytes空、後続requireClearも拒否/gate3、全descriptor解放。Filesのinode/bytesを直接読む。Production methodでexpected生成しない。実Root/permit/VM/failed-cohort/退役操作は一切行わない。

既RepeatedTest10のclassは選択しない。選択PG6466はbaseline12/7+本1/1=13/8、六module既format/NullAway/SpotBugs、reader6468は元artifactだけ回収・全851/1667/六Jar/PMD/Checkstyleを確認する。Commandは `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6466_nio_collision_selected.py`、真正0後のみ6468を一回実行。新Testsource固定・元4056証拠保持、別sourceへ旧coverageを合算しない。Global100/実native/正式受入は本限定試験では宣言しない。結果・hashは別記。

群見積.1/.25/.75pp、owner WBS-P017-06、F03/K01.01は参照費0。Test初稿作成後・実行前の記録であり着手時刻を遡及捏造しない。元見積/v4/工数nullを維持する。
