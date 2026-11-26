# 素材metadata合成hashの並行一次診断

WBS-P019-03.02/2、F03、SS343・354、BUG-3958／YKT-2997。対象は表の既試験だけ。四種類、最大long、Unicode、固定32bit多項式、JVM独立identity、shared inputの64回評価を維持する。

| ID | 選択メソッド | 独立期待値の元仕様 |
| --- | --- | --- |
| PT-MIG-ASSETGEN003 | AssetMigrationManifestTest#assetGenerated003EntryHashUsesIndependentPolynomialAndJvmIdentity | [051](051_生成record契約八追加と実Code百三十七・独立仕様.md) |

各workerと入力の個数、5秒結果取得・10秒終了は元仕様に従う。一次失敗と終了失敗が重なる検証は既MigrationFixtureWorkers試験を参照する。各今回TestIDの終端を当正規Bootstrapの一つのexecで取得。通常の既済別試験、実DB／原本／領域アクセスは対象外。
