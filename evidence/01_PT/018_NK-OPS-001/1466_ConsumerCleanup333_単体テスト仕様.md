# ConsumerCleanup333 ordinary secondary保持 PT仕様（実装前）

BUG1604/YKT1357、SSC333、NK-MSG-001/002、API SyncRequestConsumers/WebLogConsumers/QuestionWorkConsumersおよびWeb ArtemisReplyConsumersのstartup/close。RD MQ003～010/UI212213231、SS312321354（342参照）。主費WBS-P005-02、P005-03/P006-05/P012-01は同群共通参照で追加費0。新群開始前見積は着手eventで固定し、現PG6668全体群や当初/v4を減額・完成扱いしない。

設計only dda2965e0/PR197→main0caf68c60c8dac43ecf2b29941deb12a4ff15850、二SS/914三fileだけ通常merge/remote確認済。実装/tools/evidence混入0、添付cap100一回失敗/迂回0。現PG6668/sourcef16fは実行中、元真正終端/原資格までMain/Testは変更しない。本書は次群の独立oracleであり、PT実施/PG完了を示さない。

## PT_DEFAULTの安全なfixture/独立oracle

JMSContext/JMSConsumerの自己所有interface proxyだけ。factory/open・set/start/close・owner callbackをliteral counter/listへ記録し、broker/DB/HTTP/VM/Root/原本/鍵/permit/実native等の操作は一切発行しない。start時に事前固定NoSupp Runtimeを投げる。NoSuppはテスト用RuntimeException subclassの標準protected constructorでsuppressionを無効にするだけで、権限/実環境挙動の試験ではない。expectedは事前固定Error identity・必要close数/順序・既ordinary catalog/causeのliteral、Production methodを期待値生成へ使用しない。

API新4method/Web新2methodを予定し、初期snapshot=f16f相当Main固定で原反例を先行する。実装後は全新旧Test byteを固定、元必要PG四Mainだけを同一oracleと既domainへ検証する。

|Test ID（予定suffix）|入力/操作|独立期待値|
|---|---|---|
|333001 SyncStartupSecondaryAfterEveryOwnedClose|NoSupp startup primary、notification/close側各cause/suppressed/JMSlinked/SQLnext Error、四context|factory4・start1・通知1、全四close各1/順序固定の後に元Error。追加start/ACK/commit/business0|
|333002 WebLogStartupSecondaryAfterOwnedClose|同入力、single context|factory/start/通知/close各1の後に元Error、処理再送0|
|333003 QuestionStartupSecondaryAfterOwnedClose|同入力、single context|同上、work processor呼出0|
|333004 SyncMultiClosePreservesDeferredFatalAndSuccessfulPhases|返却済四context、第一close NoSupp Runtime・第二close Runtime graph Error・残二正常、次の明示closeは故障二件だけ正常化|第一回は四close各1の後に元Error、二回目counter2/2/1/1、三回目不増、ready false。第一故障で残closeを飛ばさない|
|333005 ReplyStartupNoSuppSecondaryAfterSingleClose|Web NoSupp startup primary、close側四edge Error|close1/業務0/DLQ0/既startup通知追加0の後に元Error。close自身の既wrapper/graphを消さない|
|333006 ReplyDirectPrimaryCloseAndOrdinaryCatalogRemain|primary直接Errorと同一/別close Error、ordinary primary/close、same Runtime|既primary Error優先、自己抑制0、nonfatalは既fixed startup catalog/cause/suppressedとclose1を保持|

各故障/identity判定前に取得数・必要全close順・回数・通知・禁則操作0をassertし、fixture未知操作は即AssertionErrorで予定反例から区別する。API通知が正常returnした後だけの動作を検証し、native専用onUnconfirmedの既UNKNOWN/非帰還保持を回避・認定しない。API直接Error/通知Error・直接closeの既選択や普通cycleは新controlと既owner試験で回帰する。元直接例外identity/public checked/通常cause・suppressedが変わればoracleを実装都合で変更しない。

## 実行予定・保全と品質

新only run/source/Test hash/実commandは着手時に追加。赤はAPI新4/1＋六baseline12/7=16/8（API停止時実10/5・F4を予測）、Web新2/1＋六baseline12/7=14/8（Web停止時実12/6・F1を予測）。原readerは予定boolean assertion/source/archive/phase0,0,1・終了1/元XMLを厳密照合。失敗意味/compile/error/skipped/flakyが異なれば加点しない。修正後greenは既consumer77/20＋新6/2=83/22予定、全六compile/format/null/staticを維持。真正0後に原六Jar/XML/全8511667/四Main差/actual四counter/raw診断を照合、必要全体は最新trigger/sourceに固定して実施する。

現当群の動的PT/PGは未実施。旧selected77/31や実全体4170の将来結果を新sourceへ合算しない。全4176/640は新六追加後の予定であり合格実績0、coverage未測定を100%へ補完0。現Bug1604/1357/F0332保留/正式1964-53/個別17-190/工数null/QA051final/全HOLD/代替0は保持。終了code/timestamp/OS/JDK/tool/branch/commit・input/oracle/actual/hash/関連BUGSSCは元begin/manifestと実結果へ記録する。
