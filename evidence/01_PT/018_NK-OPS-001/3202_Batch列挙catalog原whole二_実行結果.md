# Batch列挙catalog原whole二・実行結果

仕様3201/PG-D1029。2026-10-31、dev-foundation/HEAD e2c6835bef421e8eb20263c55ed32f149c2a409e、Production6b53/normal14216不変更未配備。JDK25.0.4+7-1-26.04-Ubuntu/Linux7.0.0-38-generic/amd64、原JVM23:04:23.652926～23:04:24.371810 JST。新自己JVM/session PG16477-BATCH-ENUM-CATALOG-ORIGINAL-TWO、checked entry d77450df/session57145終端e9f524真正0。

|原whole/Test ID|結果|
|---|---|
|batch.repository.EnumValueCatalogCompatibilityTest / PT-F03-ENUM-BAT001|1 PASS|
|batch.platform.EnumValueCatalogCompatibilityTest / PT-F03-ENUM-OPS001|1 PASS|

F/E/S/flaky/rerun/not-run0、newTestID0。実行commandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg16477_batch_enum_catalog_original_two_pt.py`、post16478/独立16480も同形式。原Test/Main/SS期待値不変更、前source5732等の成果は転用0。新2は既宣言の当source未参照caseだけ。

公開証跡はevidence/provisional下：raw PG16477-batch-enum-catalog-original-two-pt-v1/manifest.json SHA c4dd384d53a32ec054ba794e17234c0587711a08f0fd0d5e6099d16f38095801、exec887657a8ea37a31c54caff0b42f09736a8592b1a9560043e6ca8e4238da1788a。二XMLはraw/post manifestの一意hashへ結合。元runはwork/pgpt-runs/PG379/pg16477-batch-enum-catalog-original-two-pt-v1、外部jobではなく今回所有の終了済みJVM。

PG16478 post SHA d45441e00a12dcdc7070430d30b528a6d48625b026367af7ce311f6dadf8cc4d、session38524終端f26d16真正0。全8Source/28physical=20Code+8真正NoCode、12Codeは無record/未実行として分母保持。全測定はline760miss/109covered、method150/31、class12/8、branch590/10、strict四gate1（測定未達、隠さず保持）。CleanupKindのみ四100、ApplicationUnit/BatchStep/MaintenanceUnitは自然branch0三100。残り4Sourceは外側未実行のpartial。既存5Sourceのより広い証跡は置換せず新3Sourceだけ現registryに加える。手動除外/exec union/人工call0。

PG16480独立 SHA f3a17187aadb78ad5e9dee45699fb82b4272cba847ca6e71a913517a1ebe44c2、29f117真正0。固定literal/関係五oracle、27metadata負例、入口AST五検査、approved origin/main SS331341343同byte、元二XML/宣言集合を確認。四held・六nativeはtrueprobe0、Root回収27physical無record。RootStartupContext/BackupUnitStartClientはnested enumのみで、outer/native/factory/start/retire実行無しを保存counter/無recordで確認。SQL/実Unit/VM/DB/broker/鍵/私有raw/permit/回収/所有変更は0、HOLD不変更。

BUG2178/YKT1925：初版16476は27c333bd/5e4ba4でbody0だが入口欠落・manifest不在/試験0。元byteを凍結し合格計上0、16477の明示入口とAST元欠落拒否・新入口存在・再欠落拒否、16460の明示run.main/16446の明示mainによる非該当を確認。16476の本体前lintのみ失敗はbodyfalse、独立16480 unusedimportもbodyfalseで本体前修正、Product失敗ではない。旧試験の再演0、有限工具scope是正済み・commit/push後閉鎖。

正式1964PT/53scope・歴史17/190・QA051final・工数率null・G07/G13/F03全体/451は未受入のまま。

