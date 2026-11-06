# WebSessionSnapshot 不変値 単体仕様

NK-WEB-001/WBS-P015-01、RD FUN001/AUT001..004、UI226/242、SS314§7.2.4/331/352・SSC041/PG-D098。MainD8不変更、public constructor/getters/toString全体。PT_DEFAULT、965/event3999原0.5/2/4pp cap6。

fixtureは固定合成ID・row・空anonymous属性のみ。ASCII A×43のSHA256はPython hashlibで独立計算した0f007385b6f9d4b7eeb2748605afe1a984a0a3bfa3f014d09e2a784ce9e5cd1aをrowへ直接指定、expectedをProduction lookupHashから生成しない。ciphertextは長さ29のdummy配列（認証/復号していない）、fixture-v1は架空key IDで実key/providerを使わない。正常一致/不一致・null三境界/同一保持・redaction・期限切れ技術行/TTLとversion上限/配列copy所有/自己所有2worker8task・10秒joinを確認する。immutableデータ型に再送/実認可保証はなく、期限切れrow保持を認証成功と解釈しない。

既normal20112 web/protocol JARとJSpecifyだけ、shared012/profile067 prepare/static→source固定→全8単一JaCoCo/全physical1/四counter100/CRC/strictpost。初期化は当snapshotと値型六＋その既知lambda/新Testだけ、Cipher・sessionstore・storage/bootstrap/DB/JMS/VM/Root/鍵/held4を呼ばない。実cookie/session/token/raw wireを証跡へ保存しない。標準JDK SHA256は固定値digestのみ。成功済六Main build/SBは再演しない。結果049/manifestへ環境/command/source/終了code/counter/XML/BUG/hashを保存、群末freshは真正終端後に結合する。全session認可/暗号/DB/451/正式1964-53/歴史17-190/工数null未受入。

|Test ID|method|
|---|---|
|PT-WEB-SNAP001|matchingIndependentHashRetainsInputObjects|
|PT-WEB-SNAP002|mismatchedIdentityRejectsWithFixedMessage|
|PT-WEB-SNAP003|nullSessionIdentityRejects|
|PT-WEB-SNAP004|nullRowRejects|
|PT-WEB-SNAP005|nullAttributesReject|
|PT-WEB-SNAP006|expiredRowRemainsDataWithoutAuthenticationGrant|
|PT-WEB-SNAP007|retainedPayloadKeepsDefensiveByteOwnership|
|PT-WEB-SNAP008|parallelSnapshotsKeepDistinctRows|
