# 残encoder24site文脈レビュー結果

G03.01、群2389/開始0.5/2/6pp・上限10、sourceb8234ad5a1403e944acaf8e13f1e5f07a22309bd。PG10252非共有wireValue/encode/decode/fromWire/fields/Codec/normalize候補53中、既是正role/code29を除く24site/14sourceを確認。構文selectorの文字列一致は欠陥/PASS判定ではなく、人手で期待側/実際側/元入力・helper由来を区別した。

|分類|site|文脈・判定|
|---|---:|---|
|API canonical fields.size|3|UserMutationはTest明示Field list、Media/Scenarioも呼出し元の手組Test Field listを期待し、Production canonical.fieldsはactual。個別field/LP byte期待も別にある。対象count文脈に新欠陥認定なし、HMAC/DB等の動的検証ではない。|
|StartupProofFrame fields|1|固定GOLDEN原文をJDKのline/等号splitでMap化。Production parser/encoderからexpectedを生成しない。実Root/証明/起動の資格にしない。|
|WebLog goldenWire/Revocation fields|3|2336byteの固定UI232/235 offset、固定LP AAD/日時/目的文字列・JDK/JCE独立計算。Production serializer/hash/encryptionを期待値生成へ使わない。public synthetic fixtureであり、鍵/暗号の動的再演なし。|
|WebBusiness CONTEXT.wireValue|1|AuthenticationContext.of("a".repeat(64))で用意した不変のTest入力文字列参照。出力enum encoderの計算とは区別し、ここでは元入力echo/callbackのproperty。新欠陥認定なし、全codecの独立性認定ではない。|
|Question/Notification state.wireValue|6|UI236のstate/label期待がSUT encoder共有。追加fixture二を含む全八/二sourceをBUG1829/YKT1580へ先行起票。|
|SessionAttributeCodecTest.tokens|7|Test固定QSB purpose/UUID sequence/日時からのimmutable record list。sessionが元入力値を保つpropertyで、Production session serializerをexpectedに呼ばない。constructor/codec全体を今回認定しない。|
|SessionSecurityContext p.role().wireValue|1|Spring authority期待・fixtureのProduction role encoder共有。横断九件中七/六sourceをBUG1830/YKT1581へ。actual側で独立literalと比較する二assertionは保持。|
|JDK Normalizer|1|JDK NFC＋trimという独立参照。Production adapter/helperを期待生成に呼ばない。|
|ScenarioSearchTemplate fields.get|1|Test明示フォーム入力Mapの値とDOM選択値を比較。Production bind/renderer結果からexpectedを作らない。|

合計24。変更済みQuestion/Notificationの元line番号を現在値として使わず、現SHA/実selector位置を照合。元role18/code15/Media是正は重複加算しない。新指摘は二つのoracle独立性不足で、製品誤動作は観測していない。新source/実行Test ID/受入加算0、正式1964/53・17/190・工数null・QA051 final/全安全HOLDを保持する。

PG10426が24/14の元selector行・現SHA/line有効性、state八/二sourceとauthority対象七/六source・actual assertion対象外二を実検索して束縛する。自動独立判定ではない。次は別群の見積りを凍結し、Web enumの期待/fixtureの固定文字列化という一つの変更経路で全15/八sourceを是正、元assertion/他token保持・必要static/normal/source post、独立性を確認したtyped projection PTだけを選択する。権限設定/実アクセス経路/Productionは変更しない。
