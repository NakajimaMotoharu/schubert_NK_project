# 2480 Log検索wire・二境界vectorとwhole8仕様

2026-10-29、元source a90e303fc59938d413c2d777380bdffbe3e7f9e7/save3927eab38/origin一致、PG-D806予定。主F03/元source担当費P01614の参照内数/追加費0。開始2/5/8共有pp/cap10/freshは487へ直接保存、元予測/N-T/専有費/工数null保持。結果予定2481_Log検索wire_二境界vector・whole8結果.md。

## PT_DEFAULTとscope

LogSearchWireClientTest全文539行、LogSearchWireClient/ProtectedReadWireClient/ProtectedReadWireException/JmsRequestReplyClient/ReplyCorrelationRegistry/PendingReply/JmsRequestReplyExceptionの全本文、Protocol header/typed DTOの境界を確認。全送受信は自己所有BiFunction/Callback→memory registryへ返す固定byte[]だけ。固定clock/UUID、自己所有8thread・64request、1ms synthetic timeoutと最大2秒の待機、呼出ごとbuffer zero-fillを検証し、実JMS provider/DB/HTTP/FS/native/Root/credential/署名/permitには到達しない。A/W graph9（1975）のTemporaryInfrastructureException/WebStartupExceptionを呼ばず、その9試験を再演・分割しない。ReplyRollbackSignal等のconsumer側はWebStartupException.preserveFatalへ到達する別経路として今回は保留し、method抽出しない。

## 独立期待・追加二vector

NK-WEB001/NK-ADM001/FUN008/AUT/MQ、UI232/235、SS311/312/321/322/323/352、既PT-WEB270..277。SS323 LGSREQ01は656/0/0/912でrequest recordsは0、保護responseは要求contextに一致することを要求する。元header/recordはSSの固定offsetからTest-localに組み立て、Production encoder/decodeをexpected生成に呼ばない。

1. `WEB273-AUTH-MISSING`（親JUnit web273MalformedReplies）: 正常LGSRSP01のoffset113..176をASCII spaceにする。期待INVALID_RESPONSE、固定診断/cause-null/非保存suppressed、pending0・sender buffer消去。元context不一致vectorの欠落境界を追加する。CommonHeaderの既profileが欠落を拒否するため、実装障害を推測起票しない。
2. `WEB274-REQUEST-RECORDS`（親JUnit web274CapabilitiesAndNull）: 有効LGSREQ01 dataへ正の固定SpeakerRecord一件を付加。request record0というSS323の契約からINVALID_INPUT、send0/pending0を期待する。別layout recordであってもnonempty判定で拒否する入力で、値は固定id1/名称synthetic/count1。新しい業務recordの承認ではない。

追加subvector IDは2、JUnit methodは元8不変で10件実行と誤計数しない。全元assert/入力/expected・golden bytesのoffset/値を保持し、追加二import/二snippetを除去した全非comment tokenが元sourceへ一致することを独立に確認する。入力位置/範囲/型/期待reason/配置・元assert改変等のmetadata反例を検出する。

13562原本/SHA/元方法8/元二PMD診断固定→二vector追加→13564全文逆/現二診断不変・CS0→source固定→13566当六normal/NullAway/lint/PT0→同source必要staticと全Main1843同byte/全Test1978集合・当SourceFile差/他Test byte/元担当費→元whole8一回・独立XML/一意case/FES0/exec・単一session/CRC/実counterを確認する。coverage targetはLogSearchWireClient/ProtectedReadWireClient（Result含む）/ProtectedReadWireException（Reason含む）の全三source unit・五物理class、共有protocol/JMS registryは参照。未達counterはそのまま記録し必要な独立補完へ進め、whole8成功だけでcoverage100/全criteria充足としない。

新vectorは既要求の境界補完でProduction変更を前提にしない。既実装の仕様違反が実行で確認されたら修正前BUG/YKT/必要設計台帳を起票する。新sourceへ旧成功を転用せず、正式1964/53・17/190・工数null・QA051final/全安全HOLD/保全物を維持、残10以下又は枠不明で保全、通常群/commit/PMO待ち停止なし。
