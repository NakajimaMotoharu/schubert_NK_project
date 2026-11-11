# 同期client原八件・未知例外所有回復 単体テスト仕様書

NK-MSG-001/WBS-P005-02、MQ003～005/UI212・231/SS312§3.2・321§6/9。Production Mainの変更はない。JmsRequestReplyClientとRegistry/Pending/Exception/Reason/Sender interface/Catalogの現7physicalを測定し、broker/provider/API認証/DB/file/VM/native/Root/held四・credential/keyを操作しない。

原JmsRequestReplyClientTest8件はSQL等の実環境を使わず全source閲覧済み。正常登録送信/clone、JMS・ISE送信例外、10ms timeout、deadline一致のlate、割込、configured1/12/20、全constructor/input長さ/time/null、closed Reasonを保持する。BUG2658のpool TWR close無期限をfinally shutdownNow/await5へ、Thread finally join2後の生存assert欠落を補う。PG26446で旧8への完全逆変換とGJF冪等、PG26448の最大入力追補でも旧8を不変更と確認。

|Test ID|method|入力/fixture|独立期待値|
|---|---|---|---|
|PT-JMS008-JMSCLIENT009|uncheckedSenderTypesPreserveIdentityCopyAndReusableCapacity|同じsynthetic ID、送信callbackが自身のcloneを変更し既知IAE/NPE/AssertionError各一回をthrow|同一Throwableを保持、呼出元byte0不変、callback一回、pending0。次の同ID成功はliteral reply4/5/6でpermitが返却されたことを検査。例外を正常応答へ読み替えない|
|PT-JMS008-JMSCLIENT010|duplicateAndClockOverflowDoNotSendOrCancelOtherOwnershipAndReleasePermit|別ownerが既に同IDで待機、capacity2 registry/1client。続いてClock=Instant.MAX、復旧NOW、最大1,000,000byte synthetic buffer|重複はISE/send0/既pending1・未完維持、別ID正常reply7で自己permit回復。MAXはDateTimeException/send増加0/pending0、NOW復旧後reply8。最大byteはSS321 literal1,000,000で長さ受理・送信clone変更が呼出元に非波及、既1,000,001byte拒否も保持。bufferは調整境界のsyntheticであり実layout wire合格を主張しない|

Client原8＋新2＝10、現在source不変のRegistry全7、現在Catalog全2を同じsource/sessionの一回19件へまとめる。Test固有method抽出・旧exec合算をしない。共有9件は新しい接続経路の全依存coverageを測る必要回帰であり新定義数へ加算しない。Main7の全実行可能classについてline/method/class/branch100%、全F/E/S/abort0とowner終端を必要とする。

Senderは単一abstract sendのみ、実装/default/static/initializerがなく実行可能counterは0。physical inputに保持しN/Aとする。JMS Reason/Catalogのvalues/valueOf/$valuesおよびdefault Reason enum constructorはjavacの自動生成でJaCoCo標準filterの対象、独自除外を追加しない。各値/名称はclosed enumとliteral6宛先のテストで確認する。JVM hidden lambdaのbodyはRegistry/Pendingのmethod内で測定し、adapterを別製品classとして捏造しない。

PG26450はJava25.0.4の`-g -proc:none -implicit:none --release25 -Xlint:all -Werror`で明示Main5 sourceとTest3をcompileし、現Protocol buildのCatalog一classだけをcopy。7physical全件が正常buildのclasshashと完全一致。LayoutDefinition.HEADER_LENGTHはSSの256に対応するcompile-time constantで、javapにruntime class/method参照なしを確認。Runtimeは当Main7/Test5、JMS API3.1.0/JSI1.0.1のみ、Protocolや他製品JAR/providerを載せない。

静的: 変更Testの26452 raw9は一件ずつ単独JUnitの自己所有Thread/poolとfinite finallyに基づき非該当、CS/processing0。26454は全7のbyteと同sourceによって既存正常NullAway/style0・SpotBugsのweb/protocol全ClassStats/Bug/Missing/Error0を対応。正常Main解析の確認目的再演なし、抑制・coverage除外追加なし。実環境はJava25.0.4/JUnit1.13.4/JaCoCo0.8.15/PMD7.28/Checkstyle14.3、OS/JDK・command・code・source・hashはmanifestで保存する。

再現: 1237 qualifier compile/static、1238preflight、source固定push後1237 run <source>、1239post <source>。一回用26450/52/54/56/58 namespaceを上書き・重複実行しない。Runtime header256/最大1m/全time入力は独立literalから期待を決める。SSのproducer call2秒・reply arrivaldeadlineと待機2秒を保持し、未実証のwhole-exchange/send時間解釈でMain/期待値を変更しない。

元追補.25/.65/1.3pp cap2（26442製造前）、最大入力の詳細化は同群内・新定義増0。元P00502全19sourceの残14 method・C04・全体451/F02F03/global2177・正式1964/53/元190新受入・工数率は未更新。BUG2658/YKT2338の当二ownerを再試験し結果4044へ記録する。現在19件は未実行。
