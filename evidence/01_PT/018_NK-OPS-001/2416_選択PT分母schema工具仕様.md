# 選択PT分母schema工具仕様

event2783/QUALITY_SCOPE_DIMENSIONS_SCHEMA_V1、着手前1/2/4pp cap10・primary WBS-F03、共有開始used3/reset1793774153。BUG2026/2027の再発防止追加工具費であり元PGPT受入や製品試験を増やさない。

対象quality_scope_dimensions.pyのbind/verify_qualification。ケース/一意suite/whole Test source/新旧ID/旧新physical Main-Testを別名で返し、source・真正終端・XML case集合・元hashと同runだけ結合する。countのbool/負数・重複/失敗/旧exec合成を拒否。物理数をsource数から推定せず、既に独立測定されたproof値を保ち資格metadataの同じfieldとだけ比較する。旧schemaの未提供fieldはfail closedであり補完推測しない。

入力は保存済みPG13104/13108/13112/13118の公開manifestだけ、shaはpg13124のPINSに固定。元3PT/compile/coverage/VM等は一切再実行しない。TOOL-DIM-001は実保存3/1suite/1source/1972旧Testphysical/新1/1843Main照合、002は全24の非同値metadata拒否、003は合成metadata一source→三physicalの受入でsourceと物理の混同を防ぐ（製品PTではない）。独立postで全pin/helper/source/manifest不変更・観測fieldと期待fixtureを確認する。

commandはchecked entry pg13124、独立post・全hash/actualは2417へ。NT/専有費/工数null、正式1964/53/17-190/QA051final/全actualと二保留工具は不変更。新規製品Test ID/実測coverage/個別受入0。
