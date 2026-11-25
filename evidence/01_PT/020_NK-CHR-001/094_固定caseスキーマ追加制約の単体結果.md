# 固定caseスキーマ追加制約の単体結果

BUG-3809／YKT-2967、PT-CHR-DEF-SCHEMA002。修正前は非変更の主クラスと新規合成試験で1件失敗し、五層に追加した制約の診断がすべて欠落していた。未登録の宣言があれば固定診断を返すよう修正した。正常の定義、既存case/DIF、Current baselineは同一。

修正後の先行26件は成功したが、書式差があった。整形済みsource `5a53ca6ea5eb79855acb63870551d3dff9066a73` を固定した最終26/26は失敗・エラー・スキップ各0。書式、Checkstyle、通常Maven包装は終了0。正規JARのGateContractValidatorとValidationResultの2物理は単体に使用したbyteと一致した。

この選択範囲で追加のhelperとlambdaの実行命令はすべて測定された。クラス全体の四指標と全製品451には残りがある。実CHR、正式受入は未成立。 [直接証跡](evidence/PG44804-fixed-schema-additional-rules/manifest.json)
