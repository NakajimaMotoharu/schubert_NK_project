# 1268 Expiry監査read 未修正の独立再現

1267/EXP310001/PTPRE032、BUG1530/YKT1290/SSC310。Test-only source **d3acc4b7e44d462e6a26f11ea8bac7b5e32dc4ac**、Mainは8c869d7cea21d587b859b3e72e3516d9d2deb5c8と同一、branch dev-foundation。`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:../toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6052_expiry_combined_selected.py red`、元exec65282、2026-10-20T12:34:49.432635Z～12:36:46.531998Z。OS/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0は既toolchain、全実command/begin/owner/XMLはWorkPG379/pg6052-expiry-combined-red-v1へ保存。

真正command **exit1**・phase[0,1]、13件/8suiteの全identity一致、**既12成功・新EXP310001一件失敗**、error/skipped/flaky0・source全入力不変。元AssertionError同一性を期待したが、実値は`BatchRepositoryException: batch repository operation failed`。rows.nextのErrorをrows.closeのSQLExceptionがplain finallyで置換し、外側SQL catchが固定例外にする反例を再現した。静的疑義を実証したが、redをPT PASS/代替PT完成/実coverageへ算入しない。

| 元証跡 | SHA256 |
|---|---|
| source.tar | 05c1aa4d5fea1fb132f43c2ad524d2c8d3870d1f01c7a467e9c2b6ef805d26b6 |
| manifest.safe.json | 0d396cc944155dd0ef230189fe935bf17be26ed63eed2ccd8991b8346940a79c |
| 当新Test原XML | 60fc0ace775a03737937095564f05edc3f8c12769ecd208b7b2b2405e008e9ef |

六format0、前五module SpotBugs0、batchは当JUnit失敗により後続package/report/static未実行。targetCountersの未測定0/0を実100%にしない。元全3976の成功/六static0とは別source/run結果であり、これを上書き・再演しない。proxy以外のDB/VM/サービス/権限/failed-cohort操作0、秘密は固定public markerだけ。

SS331SSC200/332SSC063199と343SSC304の適用性を照合し、SSC310はread内二scopeだけを補足する。未知provider同一性と既不正DB投影の固定拒否を分離し、successful直下TWR/stage/finish直下は別契約維持。設計only公開後の局所PG、独立68合成/正常null・既実DB影響回帰/同source品質は未実施。正式1964/53・17/190/工数null/QA051final/実VM等HOLDは不変更。
