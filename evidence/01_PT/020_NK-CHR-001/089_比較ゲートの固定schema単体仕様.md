# 比較ゲートの固定schema単体試験仕様

NK-CHR-001、WBS-P020-01.03/2、RD TST-001/TST-004、UI264、SS355 §5・§10（CHR-G01）、BUG-3805。対象は `GateContractValidator.validateSchema`。承認済みのcatalog schemaから、versionの整数定数1、cases配列、各itemのobjectを固定期待値とする。公開定義6点を読む通常PTであり、変更はJVM内の新しいJSON treeに限る。

| Test ID／method | 独立入力と操作 | 期待結果 |
|---|---|---|
| PT-CHR-DEF-SCHEMA001／fixedSchemaVersionAndContainerTypesAreCheckedIndependently | 原定義、versionの文字列1・整数2・欠落、cases typeのobject・欠落、item typeのarray・欠落。各変更は別のコピーで行う。 | 原定義は空の診断。versionは `SCHEMA_VERSION_CONST`、casesは `SCHEMA_CASES_TYPE`、itemsは `SCHEMA_CASE_ITEM_TYPE` の各1件。 |

関係する既存の正負試験は変更後の同一runで選択する。baseline、実ブラウザ、実サービス、追加の環境権限を必要としない。実行対象source、command、結果と未加工coverageは実行結果とmanifestで追跡する。
