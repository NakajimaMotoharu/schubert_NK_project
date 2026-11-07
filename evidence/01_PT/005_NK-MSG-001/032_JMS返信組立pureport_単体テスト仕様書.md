# JMS返信組立pure port 単体テスト仕様書

Program NK-MSG-001、JmsMessageFactory.INSTANCE/createReply。RD MQ003008/UI231 §5/UI232 §3/SS311/321 §8/322 §4-5。原1/4/8pp cap10、Main/source-expected不変更、新直接PT8。本文3716の独立性と元実broker/HOLDを適用。

|Test ID|class/method suffix|目的・入力・独立期待|
|---|---|---|
|PT-JMS-MFACT001|syncGoldenFieldsAndCallerOwnership|手書き256header+LOGRSP24=280。createBytes1/write exact bytes/correlation固定requestUUID/MessageID固定responseUUID/layout LOGRSP01/version001、全六setting callsのみ、caller input不変|
|PT-JMS-MFACT002|asyncAcceptanceGoldenFields|QSBRSP01 S/A/320、payloadはreceipt R×26/questionId000000000001/JST17/reserved9。上記properties/layoutを対応、send/transaction等の追加呼出しなし|
|PT-JMS-MFACT003|rejectsNullPortsBeforeProviderUse|null context/null arrayはNPE契約拒否、provider呼出し0。NPEをcatchして正常へ変更0|
|PT-JMS-MFACT004|rejectsMalformedCommonHeaderBeforeProviderUse|body0/255/予約非spaceはPermanentProtocolException、provider0|
|PT-JMS-MFACT005|rejectsRequestAndInternalEventBeforeProviderUse|LOGREQ Q/SとQWK E/Iはheader-valid独立vectors、factory方向拒否IAE/provider0。request UUID self、event auth/result absent|
|PT-JMS-MFACT006|enforcesByteLimitAndExactDeclaredLengthBoundaries|header280のbody279/281/1,000,000はdeclared-total不一致、1,000,001はwire cap超過、全IAE/provider0。正常280/320は001002で確認|
|PT-JMS-MFACT007|retainsCheckedFailureAtEveryAssemblyStage|write/correlation/三propertyの各JMSExceptionを同一objectで伝播、当stage以降settingなし/owner close等0。手書きsix-step prefixで照合|
|PT-JMS-MFACT008|preservesProviderRuntimeFailureIdentity|createBytesMessageの固定JMSRuntimeException identity、CREATE一回のみ、JMS owned endpoint/closeなど0|

全期待値は手書きASCII byte positions/field長・固定literal、Mainをexpected計算に使わない。全headerの予約とdata予約はspace、numericはzero-pad。context a×64とpublic UUIDは非live synthetic fixture、実認証/operation token生成なし。FixtureはJMS interface呼出しだけを厳格記録、未許可methodはAssertionError。入力/予想properties/出力はsource/公開hashへ対応。

null/欠落/未知header/byte最大境界/全短絡条件/各checked-exception/Runtimeを含む。並行・再送・transaction所有・Artemis実接続は当stateless assemblyの責任外で既owner範囲のHOLDを保持。単体port成功でそこを受入にしない。

JDK25.0.4/Platform1.13.4/JaCoCo0.8.15/JMS API3.1.0。exec command/OS-JDK/branch/固定commit/exit/XML/FESabort/line-method-class-branch/実初期化/全正常CRC/単一exec/不足/関連BUG/manifest hashは033実行結果へ記録。新Test未実装の最初のTDD失敗はBUGにしない、実装済みMain違反を発見した場合は修正前915/916へ登録。
