# 画面復帰先URL port 単体テスト仕様書

Program NK-WEB-001 / SavedScreenTarget全method/normalphysical1。RD FUN-001/AUT-001..004、UI221/226、SS313 §4/9・314 §3/7.2・352。834/group3879原.5/1.5/4pp cap10、普通PGPT、第一Vの代替や全完了にしない。

入力は手書き相対URL・method・queryname・境界Stringだけ。JDK URI/URLDecoder/Pattern/UTF8のデータ解析であり、接続、navigation、redirect、HttpServlet/session/credential/key/Root/VM/actualfailedcohort処理を一切呼ばない。元通知や安全制限を探る試験ではなく、画面復帰保存の承認済みAPI契約を普通PTする。既SavedRequestTargetはseedFOUR100を再利用し、そのSourceの単独再測定/確認目的の別runは行わない。依存するpublicvalidation経由の失敗wrapは新SavedScreenTarget自身の契約として検査する。

|Test ID|class.method|入力と独立期待|
|---|---|---|
|WEB-SAVED-PORT-001|SavedScreenTargetPortTest.everyApprovedScreenFamilyRetainsItsIndependentLiteralLocation|全承認screenfamily23個/元location保持/redacted表示|
|WEB-SAVED-PORT-002|SavedScreenTargetPortTest.rawQuerySpellingEmptyFieldsAndBenignValuesRemainUnchangedAndObjectsIndependent|query空・重複・percent表記・値の語を保持/別instance独立|
|WEB-SAVED-PORT-003|SavedScreenTargetPortTest.unsupportedFamiliesReservedMediaAndOverDeepLocationsRejectWithNoValueInFailure|対象外family/予約media/download/深すぎるpath/case差は固定拒否|
|WEB-SAVED-PORT-004|SavedScreenTargetPortTest.eachSecretParameterNameRejectsInMixedCasePercentSpellingAndNonFirstPosition|全14secret querynameのplain/upper/percent/非先頭位置拒否|
|WEB-SAVED-PORT-005|SavedScreenTargetPortTest.rawAndEncodedPathParametersRejectWhileSemicolonsInsideQueryRemainData|pathparameter ;/%3B拒否、query値semicolon保持|
|WEB-SAVED-PORT-006|SavedScreenTargetPortTest.underlyingGetRelativeUriDelimiterDotAndFragmentFailuresAreWrappedAsFixedScreenFailure|GET相対URI/dot/encodeddelimiter/fragment/UTF8不正の固定wrap|
|WEB-SAVED-PORT-007|SavedScreenTargetPortTest.explicitNullContractsAndEveryNonGetMethodFailBeforeRetainingALocation|null2入口はfailfast、非GET6種は固定value-free拒否|
|WEB-SAVED-PORT-008|SavedScreenTargetPortTest.exactUtf8TwoThousandFortyEightByteBoundPreservesAsciiAndMultibyteQueries|ASCII/UTF8実2048byteは保存、2049byteは拒否|

期待値はUIの画面family/保存可能相対GET、SSの2048UTF8byte/原query表記保持・secret名不保存から独立literal表で作り、production methodやregexを呼びexpectedを生成しない。businessIDの実在/認可はこのallowlistの責任にせず、メディア配送/管理HTTP等の予約非画面は保存しない。query名の大小/percent解釈と値を区別する。secret名caseの値はpublic-fixtureという非機密文字列だけ。失敗はsaved screen target is invalid/cause null/suppressed0で入力を漏らさない。method/location nullはObjects failfastで正常結果扱いしない。APIはimmutableなlocationだけ、worker/再送/DBを持たないため実session並行/再送は別未実施、反復factory/別objectで状態独立を確認する。

Linux/JDK25.0.4、JUnit1.13.4/JaCoCo0.8.15。CoreMain7d2c・normal六module build/NullAway19270と六SpotBugs19272全0を同Maininput/hashで再利用、不要な再build0。既qualifier prepare/static/run/post saved_screen、compile19340/static19342→source固定/push→PG19348全8初回/post19350。normal全physical1/CRC/全@Test/単exec/session・line/method/class/branch全100/HELD四0、manual除外0を独立post。静的適用性・command/環境/対象commit/終了/各XML/coverage/関連BUG/証跡path/hashは835以降と039結果へ保存する。

実Web起動、認証/session保存、HTTP redirect、Current/NK実CHR/native/451/IT-ST受入には算入しない。正式1964PT/53scope・歴史17/190・工数null・新WBS個別受入0・同第一V HOLDを維持する。

Main method対応: fromGet→001～008、constructor→各正系001/002/005/008、location→001/002/005/008、toString→001、privateinvalid→003～008の拒否系。clinitは同unitの最初の参照時に共有実行し、各Testの起動順へ依存した期待値を作らず同一exec/原classinitlogへ追跡する。全8Test IDとtestmethodはsafeXMLへ一意対応する。固定前835、Main不変更、19340compile0/19342PMD0-CS0-parser0、suppressionなし。
