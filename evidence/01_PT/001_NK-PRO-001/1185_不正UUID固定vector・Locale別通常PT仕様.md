# 1185 不正UUID固定vector・Locale別通常PT仕様

Program NK-PRO-001/TypedFieldValues.requiredUuid・semanticと関連null境界、Test SemanticFieldValueTest。関連NK-PRO-001、UI232§3/243、SS323§2/10・354、BUG1863/YKT1614、WBS-P001-03主担当/参照P00101/P00102/P00201、工程PG/PT。群event2465、開始1/3/7pp cap10、base source682/Main21d。大文字UUIDの生成式を明示golden inputへ置換するTest-only PGで、Production/承認済wire期待値を変えない。

固定fixtureはlowercase UUID `123e4567-e89b-12d3-a456-426614174000` と、独立記載のuppercase `123E4567-E89B-12D3-A456-426614174000`（36 ASCII byte/8-4-4-4-12）。Productionのencoder/parserをexpected生成へ呼ばない。uppercaseはcanonical lowercase契約に違反し、requiredUuidはLayoutValidationException、cause IllegalArgumentException、固定safe semantic診断・raw UUID非出力が期待値。hexに実Locale障害を観測したとの主張はしない。

着手前区分PT_DEFAULT：既存純粋な二methodだけを、Protocol jar＋同module Test classes/JUnit/jspecifyと専用出力directoryの新JVMへ限定する。全候補四methodから、変更negative methodと直接関係するnull methodの二つを選ぶ。正常encode/value比較二つは無変更であり、同じ成功の確認だけの再演として今回は起動しない。元Programの他試験を免除・合格扱いしない。Test/TypedFieldValues/値factory/PathSyntax/JstWireTimestampを読み、処理がmemory上の文字列・日付・UUID・NFC/境界検査のみ、DB/JMS/HTTP/実file/credential/key/Root/VMを使わないことを確認済み。synthetic HEX_Aは型検査用公開値で実tokenではなく、出力へ保存しない。

| Test ID | 対象method/入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-PRO-LOC-N-JP/TR | semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects、ja-JP/tr-TR別JVM | 上記大文字UUID/不正日時Feb30・invalid文字列・絶対/空path等を拒否、元固定semantic診断/IAE cause/raw UUID非出力。SSのcanonical型と明示literalがoracle、Production戻値をexpectedに使わない。 |
| PT-PRO-LOC-Z-JP/TR | semanticEncodingHelpersRejectNullReferences、ja-JP/tr-TR別JVM | 各encoder/Optional factoryのnull referenceはNPEを送出し正常値へ変換しない。Test helperはNPEをcatchして製品の正常処理へする実装ではない。 |

同時実行/再送/DB transactionは純粋な無状態型検査に非該当、二Localeは別processで同じTestIDの環境variantとして記録、Locale.setDefaultで共有状態を変更しない。元Graph9・DB/鍵等HOLD Testを取り出すハーネスは作らず、この独立Protocol二methodだけの固定JUnit catalogを使用する。

PG: new Test-local定数一/生成式一置換、全他token/Main/他Test保持をmetadata反例と独立逆置換で確認→sourceをcommit固定→必要型/静的/当source普通PT。予定実行はJDK25＋JUnit programmatic selector固定二method、`-Duser.language=ja -Duser.country=JP` と `tr/TR` の専用JVM、JaCoCo別exec/session/新規XML。新source・実command/OS/JDK/tool/version/開始終了・終了code/target class CRC/全scope counter・F/E/S/flaky/aborted/not-run、input/実結果・BUG/hashをmanifestと1186へ記録する。source固定前や同job生存不明時に重複起動しない。

期待件数は各Locale二Test/一suite、計四実行・二固有method。失敗/skip等0でのみ当実行成功を記録する。全Program/class/branchを100と見せるために範囲を狭めず、対象Mainの完全class counterを別Locale別で報告し、未網羅は未完のまま残す。二execや旧sourceのcoverageを合成しない。正式1964-53/17-190/工数null・QA051final/元安全HOLDは別判定、全451/PT完了宣言をしない。
