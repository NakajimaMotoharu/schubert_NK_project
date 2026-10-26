# 非共有wire helper54候補の文脈レビュー

2026-10-26、群2357/G03.01、開始.5/2/6 cap10、current878866851。PG10252のwire54site/八sourceをTest側helper/profile/byte起源へ読取照合。製品Test/DB/key/graph/native/Root/VM実行0。構文候補と呼出し数・PT件数は別である。

|source|site数|根拠/判定|
|---|---:|---|
|UserMutationReplayServiceTest|10|元Testのlayout/sourceUUID/target/versionを固定24byte配置、REQ→RSPはTest指定五layoutのJDK文字列操作。wire生成は独立、別negative fixtureのcode classifier共有一件をYKT1568へ追加。|
|UserQueryReplayServiceTest|10|原索引の不足はBUG1814。現878の14caller/七fixture条件・新固定profileと元byte全保持を10320で検証済み、当10を新発見/新PTへ加算0。|
|LogReplayServiceTest|10|LogVectorsはTest元UUID/時刻/count/pageと固定LGSRSP/48data/2088recordを明示offsetで配置し、Production request routingをexpectedに用いない。|
|MediaReplayServiceTest|6|MediaReplayFixture.wireのprefix/count/extension/modeはTest指定、header・data・recordは明示offset/長さ表/固定literal。typedでProduction decodeを使うのは入力DTO作成だけでexpected byteは手組。元request header getterはfixtureのcorrelation input、SUT semantic selectorでない。|
|QuestionMutationReplayServiceTest|2|cancel booleanによるQDL/NTC選択は独立だが、wire内部二件及びfixture六件のusesSuccessProfileで期待profileをSUTと共有。BUG1817/YKT1568として分類依存を是正する。|
|QuestionQueryReplayServiceTest|6|原索引の不足は1811で是正済み。212固定profile/4c同値定数化のsourcepostで元caller/byte保持、当6を新PTへ加算0。|
|ScenarioReplayServiceTest|9|元Test prefix・count/file flagとScenarioReplayFixtureの明示272/152/72/800/5584/4800長さ・offset。request.responseLayoutはactual側で別prefixRSPとassert、expectedをそこから生成しない。|
|ResultBoundResponseSnapshotCodecTest|1|opaque byte payloadの値7をTest配列へ固定し、lengthはQSBRSP320/NTC288/QDL280の独立Map。封筒/参照binding目的で、これを業務payload妥当性Testとはしない。今回key/crypto実行なし。|

新不足は期待側success classifier共有。全四moduleのTestで同callを検索すると12/五source（QuestionMutationReplay八/同Application一/UserMutationReplay一/UserCommand一/Web token lifecycle一）。元Test中のその他依存や全oracle独立性を認定せず、Test側明示成功enum identityへ是正する。UI232は0000と0200だけが成功profile。元Testの実PT/coverage/HOLDは変更しない。先行2046/2049のMutation非該当はrequest/layout選択に関する文脈で、今回のcode classifier依存とは別。過去の限定レビューを全oracle証明へ拡大しない。
