# 直接expected helper70siteの起源レビュー

2026-10-26、群2351/G03.01、開始.5/2/6 cap10、current4c975c3eb。PG10252の非共有expected selector70site/五sourceを、helperとcaller/fixtureへ読取で対応付けた。製品Test/元fixture/DB/key/JMS/Root/native実行0、全G03の受入ではない。

|source|site数|根拠/判定|
|---|---:|---|
|UserQueryApplicationServiceTest|15|expected→UserQueryRequest.decode→ReplayTest.wireのdetailRequestに期待profileを依存。BUG1814/YKT1565起票、原wire13caller/保存error判定を含む横展開へ。|
|LogQueryApplicationServiceTest|18|expectedはTest元message ID/context、count、明示clockをLogVectors.wireへ渡す。固定LGSRSP/header/48data/2088record、Test指定countとSQL降順id/messageを独立offsetで配置、SUT response/layout/decodeからexpectedを生成しない。|
|QuestionMutationApplicationServiceTest|13|expectedは元Test cancel boolean/source UUID/response ID/時刻/code/operationをTest wireへ委譲。fixedQDL/NTC profile/offsetで、Production request判定で期待profileを選ばない。|
|QuestionQueryApplicationServiceTest|14|旧PG10252/source当時はBUG1811。現4cは212独立helper化＋19同値定数化を10287/10304で元全token/byte/assertion108へ結合済み、当subsetだけ14を再加算/再実行しない。|
|LoginInboxServiceTest|10|Test goldenは固定688byte/LGNRSP01/explicit offset/JST文字列/公開合成context、Test指定RoleへADMIN/USER literalを選ぶ。9000は独立日本語messageへ固定置換。Product serializerやrole resolverから期待値を生成しない。|

今回新規不足は15siteに波及する一共通helper。既是正Query14を新発見や新PTへ数えず、残41siteで当文脈に欠陥を認定しない（15＋14＋41=70、Test件数でない）。入力のimmutable header getterはfixtureのID/context取得であり、SUTのdecode/routing/response生成とは区別する。新sourceの元製品実行資格・coverageは未成立、旧sourceの成功を当sourceへ転用しない。
