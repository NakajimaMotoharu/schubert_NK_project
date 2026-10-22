# 1524 PG6958 リカバリ初回五項目・当source受入matrix

2026-10-23。利用者のrecovery-next90指示を適用。sourceはe7d64fda2453e906ee6ccc5fe718e5c29841e4aa、元runはPG6930-six-v1。目標は必要再認証4＋新規P005-01だけ。本文は意味・適用性のレビュー記録であり、原証跡の機械照合と全criteriaが揃う前に受入を加点しない。

## 着手・予算・実行境界

開始fresh0/残100/reset1793306748、06:32:54 JST前後clockで同秒。event1765/1766。初回既v5参照3.59/6.25/13.29pp（再認証標準5.50、新規0.75）、**共有累計10ppで新規受入0なら保全停止**。次の全5新規は20pp目標/30pp上限、80pp新群停止/90pp保全。開始見積/原/v4/v5は遡及変更しない。実N/T・専有費・工数率null、PMO/他chatも共有枠内。既定writerの版識別はv4を維持し、承認済v5 SHA f14e43a170daa113ad184833c4e8f5f8b0f645eada9d568e12d31480ffb1d736を補助欄へ凍結する。

PT_DEFAULT：公開source/設計/原4222の公開qualification/casesと固定host archiveの読取、純粋な独立literal/parser照合、管理fixtureのみ。原全体/署名/配置の再演、新broker/DB/VM起動はしない。host job真正終了は1523で保存済みであり、実VM等の現在終了証明ではない。F03 Root11・未特定拒否・実VM/Root/cohort/native/原本DBBackup/鍵/intent/permit/配備はHOLD。

## P001-01（再認証）：contract / scope / quality

所有6fileは481/485のheader五実行型＋package-infoのみ。108の全五MQ-014～018の原文別matrixを保持する。実HeaderModelTest七method（H01～03/HDR3266-001/002）はQ/S/E、S/A/I、12 result code、64hexのnull/未知/長さ/大文字拒否、redaction、構造/profile/route/百万byte境界・overflowを固定値で検査する。MessageCodecTestの別offset 256byte goldenとFieldCodecTestのUTF8 byte literal/NFC/control/overflowを参照し、単なる同method往復をexpectedにしない。MQ-016/017は独立UI233～236/SS323→64layout/389field/69型fixtureと当PayloadTypeCatalog実caseへjoinする。他DTO/codec ownerの受入や費用を増やさない。

7fff→e7の当Main差はInteractionKind/MessageKindのprivate field名変更と定数1、ResultCodeのprivate field名だけ。wire値/例外/branch条件は不変。対象既Test全byteは7fffと同じ。当e7原XMLから各caseを一意照合し、旧PASSを新sourceへ移植しない。immutable/pure値型でIO/DB/所有資源/transactionなし、並行readはimmutable契約、再送は同値という適用範囲。package注釈に架空counterを付けない。実NullAway/Java25 lint/SpotBugs/formatと当実行family四miss0、現static適用性に未分類がないことを必要条件とする。終了依存なし。

## P001-02（再認証）：contract / scope / quality

107の20file全体（16実行family、抽象interface、package注釈3）を照合。L01～03/F01～03/T01～02、LayoutMetadata全4、LayoutFieldCatalog全3、PayloadTypeCatalog、MessageCodecのdefensive WireMessage、PayloadCodecのvaluesAreImmutableNullSafeAndRedactedを当原XMLへjoin。UI233の全64tupleと256+DATA+RECORD×max式、UI234～236の全389field/74非空領域、SS323の全64/69型をProductionを使わずfixtureへ直接照合。start1、gap/overlap、null/未知/重複/負長/百万超/immutabilityは固定negative期待値で検査済みでなければ閉鎖しない。

差はLayoutDefinition version1とLayoutFieldCatalog列数8/最小正数1の定数化だけ、既Test/fixtureは同byte。新semantic enum/exceptionの別owner Test追加を当20fileの新規製造や他leaf受入へ数えない。interface/package注釈の実行counter無しはN/A、除外追加ではない。DB/IO/transaction無し、外部資源/VM/nativeの成功を主張しない。終了依存なし。

## P002-03（再認証）：contract / scope / quality

002/003の全5fileを専有する。HeaderCodecのUI232独立256byteと各field破壊、ExpectedRoute/TransportMetadataのBYTES/persistent/TTL/ID/version/destination/ReplyTo/deliveryCount、null/空/各不一致の固定型付き拒否、MessageEncodingExceptionの送信側診断/原因保持をMessageCodecTest全7と関連固定vectorへ対応付ける。全Main/関連既Testは7fff/e7で同byte。実JMS接続の代用ではなくpure metadata/byte変換。資源/DB/再送状態なし。P001-01/02が当e7で再認証済みでなければ閉鎖しない。

## C04（再認証）：contract / scope / quality

専有broker.xml一fileは7fff/e7と原archive同byte。SS321の24global、6ANYCAST/各durable queue、各26policy、13ACLを独立固定oracleで全照合。MQ-011の非Java serialization/Bytes制約は当ArtemisTransportContractTest、MQ-012の外部templateとprovider設定は当parse/connection設定Test、MQ-013は固定loopback CORE acceptorのparser値を照合する。実host/VMの公開状態をparserから認定しない。外部runtime配備はN/G側の別gate。

ArtemisBrokerConfigurationTest原4件に加え、**当sourceで実行済み**ArtemisSecurityTestの5role×6address×3操作・未知credential拒否、ArtemisExpiryManagementAuthorizationTestの保守管理操作/他queue・app拒否/一時reply cleanup、ArtemisFileJournalTestの永続/duplicate/再起動・DLQ/Expiry保持・1/5/25秒を補助runtime証拠として区別して照合する。各fixtureは元templateから自分のTempDir/VM transportへ限定変更し、今ここで実brokerを起動しない。これは実配備済みやSS321§13の全readinessを証明しない。

旧schema canaryのcompile0/exit0/独立不正4拒否は同じvalidator/source/公式schema hashの歴史資格に限る。当sourceの動的PASSへ加算しない。現在原4parser caseと同byteXMLが当source設定の資格。非Java XMLにJaCoCo100を捏造しない。起動前後実効値取得・実公開/認証・IT/STは別工程の未完を維持。新たなruntime不足が当C04 criteriaそのものに必要ならHOLDとして受入を止める。

## P005-01（新規候補）：contract / scope / quality

専有はBrokerTopology.java一file/shared参照なし。SS321§4の六vectorは順にSYNC_REQUEST(nk.sync.request,1000000,5000)、SYNC_REPLY_WEB(nk.sync.reply.web,1000000,10000)、ASYNC_WORK(nk.async.work,1000,0)、WEB_LOG(nk.web.log,10000,0)、DEAD_LETTER(nk.dead.letter,1000000,0)、EXPIRY(nk.expiry,1000000,0)。Queueはaddress+.q、FQQNはaddress::queue、TTL>0だけexpirationRequired。原BrokerTopologyTest二method/PT-JMS-002/005を独立手書六vectorとnull/unknown/近似名拒否へ一意join。期待値はMainから生成しない。当実counterはL25/M9/C1/B6各miss0を原から照合する。pure enum/lookup、資源/close/DB/transaction/業務再送はN/A。

MQ-001～005は485が当leafを窓口として割り当てる全体要求であり、六catalogだけで要求全体を証明しない。MQ-001のArtemis経路、002のrequest/reply correlation、003の永続work/logは当ArtemisTransportContract/FileJournalの元証拠へ参照する。004はMqAuthenticationProviderTest/PT-WEB-063～067のAPI応答role/contextによる認証・独立wire sender、AuthenticationContextVerifierTestの実fixture DBにおける現actor/expired/revoked/disabled拒否、AuthorizationServiceTestのowner/ADMIN固定matrix、DatabaseMigrationTestのweb_session専用schema/minimal grants・業務table拒否を参照する。WebのDBを全否定せずWeb session DBと業務DBを区別する。005はApiSyncRequestDispatcherTest/PT-JMS-DISPATCH-026-A..Fの独立31layout→processor port一意対応/未知・欠落・不正方向/例外identity/並行分離で、このcatalog値から呼出先を解決する境界を参照する。同Testはmarker portでありreal業務assembly/native readinessの受入ではない。

以上は当sourceの該当機能・境界の元証拠への参照であり、認証/DB/dispatchの別ownerや後続P005-02/03をここで受入しない。下位全業務処理・外部compositionをcatalogの責務へ拡大せず、元要求の参照先を欠落させない。全参照Testは原XML/全file/archive/git/currentを照合し、追加費/新PT0。P002-03/C04が当e7で成立してから当leafを閉鎖する。

## 記録・非混算

元qualification728682a9、cases692fcd4d、当品質trace37c4を参照。caseNameSha256はmethod名/署名の識別hashでありbody hashではない。Test全file/fixtureのarchive/git/current同byteがbody/期待値の固定根拠となる（旧6906のbodySha256というラベルをbody証明へ流用しない）。読取診断では存在しないraw row/optional fieldを仮定したStopIteration/KeyErrorが各1あり、成果出力・source変更無し。これらをProduction失敗/新PTへ数えない。

当source個別受入は歴史481/486の17を一括書換えず、別source registerへ必要4と新規分だけ保存し、同じ既strict check_acceptanceのcriteria/hash/source/依存検査を適用する。17＋再認証4を新21と数えない。工数null・正式1964/53・QA051 final・PTALT代替完了0は維持。登録前に未達があればACCEPTEDにはしない。

親によるPG点検結論はREVIEW_COMPLETE_PENDING_MACHINE_WITNESS。上記pure catalog/header/layout/metadataの契約、独立oracle、正規XML設定と実fixtureの適用性に追加PG変更は不要。旧五Main差を逆向きにも照合し、constant値/return/例外/公開wireに変更がないことを確認した。実scopeの入力/戻り/例外/null/境界/immutabilityは既原Testへ全対応する。動的配備/Root全体/readinessは非該当を越えて成功主張しない。原4222のsource/全input/実case・counter・staticの機械照合失敗時は受入0を維持する。

初回witnessは5287896a2で正本byte照合actual1、出力前停止。SS321の本文は同一だがbranch/mainの二空行だけ異なった。BUG1636/YKT1389を修正前に登録し、本文/仕様/期待値を変更せず既承認origin/mainの二空行へ同期した。他七設計は同byteで、strict guardを維持する。これは追加発見/再認証上の文書同期であり新Production成果でもPT失敗でもない。資格source/src/元4222を変更しない。

次読取は元JaCoCo空counterにLINEがあるとの新tool誤仮定でKeyError/actual1、出力前停止。BUG1637/YKT1390を修正前登録。対象の空4classはFieldValue/LayoutPayloadの実interface（Code無し）とFieldDefinition$1/LayoutFieldCatalog$1のcompiler synthetic switch helper。元Jar物理hash/Java25 javap flagsを独立に照合し、実XMLの空辞書は空のまま保存する。helperの実source分岐はouterの実counter全miss0で照合し、生成helperへ架空line/branch100を付けない。追加除外/到達不能指定0、元JaCoCo既定の測定対象は不変。他の空や実miss/covered0は拒否する。これらのmetadata確認は既返却Jarのdisassemblyだけであり、新PT/native実行ではない。
