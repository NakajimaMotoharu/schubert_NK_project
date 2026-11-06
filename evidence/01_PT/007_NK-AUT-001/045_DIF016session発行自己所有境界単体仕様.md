# AuthSessionService：DIF016 session発行の自己所有JDBC単体仕様

NK-AUT-001/WBS-P007-02、AUT001..004・DIF016、UI226、SS312§4/314§6/332§5/352§5・11.2、関連PG-D160/SSC056。対象AuthSessionServiceのpublic二引数constructor/package四引数constructor/issue、全source・physical1。元seed未登録/20458 strict pin無しを照合。元実PostgreSQL Login/session試験は未抽出・未再演。fake JDBCの成功は実sessionの発行・失効、実lock、Inbox commit、実Login/CHR受入を示さない。

正常fixtureはPUBLIC 32byte AA→64ASCIIa、既公開SHA256ffe054...68eb、PUBLIC zero32 AES256 key/nonce11×12・固定synthetic UUIDを使う。これらは運用credential・利用者情報・実raw sessionではなく固定暗号vectorだけ。成功系ではpublic CSPRNG生成を使わず注入したFixedRandomとSupplier、各fixtureがcodecをTWR所有しcloseする。public constructorの既定JDK SecureRandom/UUID supplierは組立だけを通し、不正transactionでrandom.nextBytes/UUID発行前に拒否する。Fixtureの数値IPv4はgetByAddressのみ、DNS/connect無し。JDK/JCA/entropy/classpath/IP metadataの全syscall0は主張しない。保留4class/Root/VM/実DB/外部service/配備/鍵/permit/CHRへ接続しない。

|Test ID|method|入力・独立期待値|
|---|---|---|
|PT-AUT-ISS001|insertsIndependentEnvelopeHashUtcAndEightHourExpiry|user1/7/N12最大、User lock→INSERT→active列のSQL/bind10値、now .123456789→micro .123456/8h、JDBC4.2 UTC、1582暦境界、公開AES envelope3vector、caller buffer消去|
|PT-AUT-ISS002|dif016RetainsTwoAndReplacesOldestWithAtomicAuditStaging|active1/2は失効0、3で最古1/4で古い2を返却順に失効。ORDER BY last_accessed_at,id固定、同borrowed TXにREPLACED/0000監査を各一回stageし、caller commit/rollbackは発行しない|
|PT-AUT-ISS003|publicAndInjectedConstructorsAndApiNullBoundsAreExplicit|二constructor各null・四引数random/ids null、API connection/client/message/correlation/time null、ID -1/0/最大+1をSQL前拒否、public constructorはexplicit TX前提、無限日時は未成功|
|PT-AUT-ISS004|absentDisabledAndMissingColumnsFailBeforeIssuanceOrReplacement|User無し/非ACTIVEはcontext拒否、status null/active id nullは固定Infrastructure。生session生成・置換へ進まない該当範囲、既取得全close|
|PT-AUT-ISS005|insertReplacementAndAuditRequireExactlyOneAffectedRow|INSERT/REPLACE/critical audit各affected0/2で固定Infrastructure、後続SQL未発行、Caller rollback責任は成功化しない|
|PT-AUT-ISS006|ordinaryJdbcAndEveryOwnedCloseFailWithFixedRedaction|五prepare/query-updateと関連driver getter/setter/next、全七資源各close、context primary+cleanup SQL。原因/suppressed/marker露出無し、全取得一回close、Connection commit/rollback/close/config変更0|
|PT-AUT-ISS007|randomCodecAndUnknownRuntimeFailuresKeepBuffersAndIdentity|注入raw RNG/nonce RNGの普通Runtime、closed codec、未知JDBC runtime同一性、各取得byte[]はfinally zero-fill。新key/credentialを発行・参照しない|
|PT-AUT-ISS008|parallelPrivateFixturesDoNotShareContextBuffersOrAuditState|二worker16個の独立codec/random/JDBC/context buffer、2/3 active混在、失効と監査SQLは各fixture3/5回だけ、全Future/TWR完了|

暗号期待値はPG20902のPython cryptography AESGCM（versionはmanifest）と手書きASCII4byte big-endian length-prefix AAD/purpose/table/synthetic UUID/owner/format/key-version、SS352のNKENC1 fieldから作成。Productionのencrypt/decrypt/aadはexpected生成に呼ばない。3envelope/hash/commandと説明を保全し、Testには独立計算済みpublic固定値だけを埋込む。暗号raw/nonce/ciphertextの作業buffer参照をfixtureが観測して0化を検査するが、実keyのログ/ファイル/DB dumpを読まない。返却tokenをlog/artifactへ保存せず、JUnit stdoutはcase名と集計だけ、guardで秘密patternを確認する。

Java25.0.4/JUnit1.13.4/JaCoCo0.8.15、normal20704 sourcefb189、全1844class/全Java-POM同byteを照合した静的20114 D8だけ参照。profile092 prepare/static→source freeze/push→一回8Unit→SDK静的根拠と元CP/init/XML/Gitを固定→strict/独立post。全physical1・四countermiss0/single CRC session/全@Test FESaborted0、旧exec合成/手動除外/無意味なassertion無し。AuthContextCodec/SessionAuditWriter等の依存coverageをsource全体100へ混算しない。未実施・失敗・静的代替はPASSにしない。QA055/実DB・native/CHR/451正式等HOLDは維持。event4059/原1.5/4/7cap10/主P00702・S/V別、結果046へsource/run/日時OScommand終了/coverage/BUG/証跡hashを追記する。

BUG2362/YKT2107は元20904 compile0/20906 raw6/Unit未起動を保全後、定数INFRA_MESSAGEへ変更。getter/setter/next十四故障点とInstant.MAX非成功を最初のUnit前に補完、現20908 compile0/20910 raw5・個別用途非該当5/適用0/処理0/CS0を保存。既sourceケース再演0、8method/物理1/原見積不変更。public constructorのUUID supplier callsite一つのlambdaは静的呼出順を確認し、profile092だけinitializer最大1を許容する。実Supplier発行の成功化ではなく、当public constructorはtransaction拒否で次処理未到達。
