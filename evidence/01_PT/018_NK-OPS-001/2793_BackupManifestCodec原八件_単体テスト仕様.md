# 2793 BackupManifestCodec原八件仕様

event3186/low-base-high .5/3/7pp、source6b53/normal14216固定。Program BackupManifestCodec encode/decode/field/digest/invalid・全Source closure。関連BAK/BKO/UI251/SS341§6.4/SS343§5.3、原PT-BAT-186～193、WBS-P017-05。原Test298行、公開Fixture、必要Main Codec145行/Manifest/Versions/FileDigest/BatchRun/Step/StepAttempt全bodyを読取済み。

PT着手判定=NORMAL_PT。純粋なbyte解析と公開合成値、ownSLOTのtarget/backup-manifest-tracesへ固定公開JSON一回書込みのみ。原本DB/Backup/鍵/real credential/native/VM/Root/permit/意図退役とは無関係。manifestはclaimsであって真正Backup認証ではない。pool8/64の全結果は親180秒JVM期限、try-with-resources終了を保持。原whole8を分割/除外せず実行。

|Test ID|原method・独立期待値|
|---|---|
|PT-BAT-186|independentCanonicalGolden: 公開965byte/SHA733939f4…、独立JSONとencode全byte一致、decode全claims/713byte合計/固定directory|
|187|allFieldsAndMaximumLengths: 固定年月/uuid/id12桁/attempt99/schema/token128/size合計Long.MAX/1873byteをliteralで検証|
|188|structuralByteMutation: 全965offset×3変異、BOM/CRLF/非ASCII/余分・欠落改行を固定一般message/causeなしで拒否|
|189|noncanonicalScalarsAndDates: 非正規numeric/UUID/date/digest/attempt/id/schemaを拒否|
|190|missingUnknownDuplicateAndOrder: 欠落/未知/重複/順序/space/escaped/null/固定format/version異常を拒否|
|191|sizeAndNullBoundaries: 0/1/4095/4096/4097byte/null/129tokenを拒否|
|192|inputOutputOwnership: 入力変更非反映、出力配列独立とgolden保持|
|193|concurrentCanonicalRoundTrips: own8threads/64taskの固定golden全byteと別identityを確認|

期待値は固定JSON `backup/manifest-golden.json` SHA256 `733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e` と公開Fixture literal。Productionのencode結果だけをexpectedにしない。Test hash c474a1ee…/fixture dc52d8ad…/Main codec7e9fdc5e…。全旧914の再演0、新execだけのMain codec全class/CRC/session/四counterを測定、既helper Sourceの成功を新codecへ合算しない。

実行commandはchecked entry `pg14886_backup_manifest_codec_eight_pt.py`、JDK25.0.4/fresh javac proc:none/Werror/JUnit/JaCoCo0.8.15。実環境・終了code・input/output/hash/coverage/BUGは2794とPG14886/88/90公開manifestに保存。四100/N/A/実不足を区別、正式451/F03/QA051final/全HOLDは不変。
