# 管理値・固定例外catalog 独立単体テスト仕様

PG18010/event3708、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEADd5890567111b51051268b2133b21d017342a80bc/dev-foundation。主F03、主責任P01003/P01002/P01202は参照/追加費0、固定1.5/4/8pp cap10/fresh82-18/reset1793774153。UserCommandMetadata/UserMutationResultの後続索引0、AnswerBusinessExceptionは1441のDB/provider Graph適用とは別の既存定義を読む。元DB/Graph/provider Test wholeを抽出/改作/実行せず、独立の値/catalog契約だけを新六件で検証する。

NK-ADM001/NK-ASY001・UI236 USRMUT24（User ID N12/更新後version N9）/UI232結果code、SS312§9/323/332/351、PT-ADM019021023/AWORK005/新PG-D1115。三Main全bodyとResultCode/ResponseData/UserId/IdValue/TypedFieldValues.requireUnsignedRangeを確認。UserCommandMetadataはnonnull traceとUTCµs切詰めだけが当内部契約で、QuestionCommandMetadataのcivil年range checkを無断で追加しない。外側wire/JDBCの年範囲/transactionは別責務、当値の成功を業務実行へ換算しない。

|Test ID|program/class/method・入力|独立期待値|
|---|---|---|
|ADMIN-VALUES001|UserCommandMetadata ctor/at/messageId/correlationId/toString、公開固定UUID二つ、現代123456789ns・preepoch999999999ns|手書ISOの123456µs/999999µs、元UUID保持・固定UserCommandMetadata[REDACTED]|
|ADMIN-VALUES002|同ctor各field null|API契約違反NPE、catch正常化0|
|ADMIN-VALUES003|UserMutationResult ctor/accepted、UserId7/version1・999999999/code0000・0200|同指定code、OptionalのUserId/version literal保持、固定REDACTED|
|ADMIN-VALUES004|同ctor/rejected、許可0100/0104/0105/9001、他の非成功code、成功payloadなし/失敗payloadあり|許可四つだけempty、他は固定invalid code、profile矛盾は固定inconsistent例外。dataを黙って削除して受入しない|
|ADMIN-VALUES005|同ctor/accepted null code/container/id・redaction/input所有|nonnull invariant NPE、既Optional/typed payloadを保持、fixed redaction。Optional自体が要素nullを表現しないためnull要素の偽fixtureを作らない|
|ADMIN-VALUES006|AnswerBusinessException ctor|固定answer could not be produced/cause null/suppressed0。providerを呼ばず、Throwable graphを探索しない|

expectedは手書時刻/UUID/数値/code列/固定診断、Productionのtimestamp/分類methodで生成しない。成功二種/許可失敗四種/その他六種を独立UI期待から列挙する。unknown enumはこの型で表せずwire文字列unknown試験は既Protocol正本へ参照、除外やskippedを捏造しない。並行/再送/SQL/業務権限は当immutable DTO/catalog範囲外で未実施。

PT_DEFAULT：UUID.fromString/Instant.parse/Optional/Set/不変typed dataと固定exceptionだけ、実User更新/権限付与/DB/JMS/provider/認証/session/鍵/crypto/IO/clock/Root/native/VM/Thread/乱数0。既held Graphで同例外型が使用されることを、新しいprovider実行許可にしない。各Source全physical/Codeと正常Jar/現source/snapshot/一session exec/CRCを照合、公式filter不変更/手動除外/execunion0。分母自然0のSourceはbranchN/A、実branchのSourceだけ四100として区別する。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg18010_admin_values_catalog_six_pt.py。Java25.0.4/normal14216/Spot14224固定/親180秒、新quality六/普通5786別。3451とmanifestへ環境OS-JDK/branch/HEAD/日時・command/終了・全input/Main/Test/class/exec hash/XML/coverage/独立oracle/関連BUGを保存。新Main測定は既Productionの資格補完で新規製造file0。正式1964/53/歴史17/190/新個別受入0/工数null/QA051final/451/全HOLD維持。
