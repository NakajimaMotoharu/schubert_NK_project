# 2633 WebBusinessWireClientsTest 元whole十二件 単体テスト仕様書

2026-10-30 JST / dev-foundation / source6b53efeec87f3ec36a840dd8e7759656cb4aee5c / HEADf6c88692fad2d084ef80e1d2348dce72781d487d、PG-D881。群3020開始0.5/4/8pp cap10。元Test全782行/12method/全Fixture・helper・callback・static固定値を確認。Main façade五件/ProtectedReadWireClient/Exception/JmsRequestReplyClient/Registry/Sender全688行とPendingReply/ReplyException、HeaderCodec/FixedWidthEncoder/AuthenticationContext・PayloadTypeCatalog全472行/PayloadSemanticValidator全487行・追加DTO/enum/必要typed helperのpure経路を確認。既読PayloadCodec/FieldCodec/LayoutRegistry/FieldValueSetも当sourcecompilehashへ固定。旧2485の17ab同依存判断は歴史であり、当Source6b53の実行結果へ転用しない。新sourceの必要限定検証として元whole一回のみ。

Program対象はQuestionWireClient(P016-18)、NotificationWireClient(P016-21)、UserAdministrationWireClient(P016-17)、LogoutWireClient(P015-05)、MediaDescriptorWireClient/ProtectedReadWireClient(P005-02)の六Source/七physical（ProtectedReadのResultも含む）。元TestのownerはUNKNOWN。関連NK-WEB001/NK-MSG001/NK-PRO002/FUN009010011/AUT/UI224225226232234235236/SS311312313314321322323324352。helper/DTOを利用してもそのwholecoverage/実環境受入へ加算しない。

PT-WEB-S3WIRE001..012はwire001..012の一意対応。
1. 18requestの独立UI offset/width固定配列とactualencode比較。QSB/QSS/QSD/QDL/NTS/NTD/NTC/USR/UDT/UCR/UST/URL/UPW/ULK/LOG/AUD/VID/MED、Header256/data/record長・NFC/space/zero・context/UUIDをTest手書表で規定。
2. SUCCESS/IDEMPOTENT_SUCCESSのtyped結果と固定JST→UTC/ID/versionをliteral確認。
3. 五façade閉じたcapability以外は送信callback前拒否。
4. constructor/input/context null・timeout0/negative/2秒超境界、sent空。
5. wrongkind/context/correlation/layout/filler/header形状はINVALID_RESPONSE。
6. fixederror codes/timeout1ns/直接Error/JMSExceptionはretryなし、送信一回・pending0・bytewipe。
7. caller再呼出三回で新MessageID・同operation token。実業務再送/権限発行ではない。
8. 自己所有8thread/180有限memorycallback・Future.get10秒、reply/context分離/uniqueID/pending0/wipe。
9. QSS1/2/50record、UI234/236独立offset672byte record、Testに固定SHA三vectorと自作providerを照合、順番/typed値/NFC/日時/defensivecopy/immutable。
10. request recordsはencoding/sender前拒否、fixtureのthrowing PayloadRecordは実行されないことをassert。
11. lower/upper/expected-layout/extra-byteのresponse形状拒否。
12. malformedQuestion ID/state/date/fillerは再送なし拒否。

expectedヘルパーはJDK配列/String/MessageDigestだけでproductioncodec/catalogを呼ばない。actualだけProductionのtyped↔fixedcodec。合成context/UUID/passwordは元Testの固定fixtureで外部・通常ログへ公開せず、Reporterはcounter/case識別だけ。送信先は元FixtureのJmsRequestSender lambdaから同一wire.onReplyへのmemorycallback、実JMS connection/Artemis/DB/network/HTTP/account操作なし。semaphore/future/timeoutは自己所有値だけでRoot/VM/resource/cohort/graph9経路には入らない。SS324 SSC329のordinary JDBC最終分類を未所持JDBCの当façadeへ無条件拡張せず、owned Senderのcleanupや実session権限を試験したとしない。

PT_DEFAULT。予定command `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14312_web_business_wire_whole_twelve_pt.py`、新-only一exec/session・元12/1suite/FES/timeout/exit/重複XMLを確認し14314独立postで完全六Source閉包・CRC/四counter/自然branch0/未達をそのまま測定。実JVM環境は既tested environmental_stepから四prefix構造化、元Main/Test/期待値不変・新Test ID0。結果/実command・時刻/tool/Source/hash/coverage/障害は2634、全formal/工数null/HOLDは不変更。
