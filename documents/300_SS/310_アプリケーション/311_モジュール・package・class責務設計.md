# モジュール・package・class責務設計

## SSC413 初期ADMIN内encoding失敗の消去試験口（2026-11-15）

SSC412に続くBUG2993/YKT2522の内部testability補足。PG33556全28FES0/既定四100とPG33560無filterbranch-line-method-class100は保存するが、BootstrapAdminService.createのencode例外finally 6instruction未達なので全Code未資格。到達不能扱い/coverage除外/合成PASSで閉じない。

BootstrapAdminServiceのprivate final PasswordHasher fieldをprivate final Function<char[],String>境界へ変え、既public noarg descriptor()Vを明示public constructorで保持し this(new PasswordHasher()::encode)へ固定bindする。package-private BootstrapAdminService(Function<char[],String> encoder)だけをnon-null内部試験口としObjects.requireNonNullでinvariant確立。外部設定/HTTP/DB/bean/roleからencoderを選択する経路を追加しない。既Productionは全て引数0呼出を維持し、PasswordHasherの公開default pin/PBKDF2-v1/validation/SQL/認可/owner/再送/正常戻り値を不変更。create内passwords.encode(normalized)を同じ引数のFunction.applyへ結ぶだけで二段のfinally消去を維持する。

新BOOTBOUND019はメモリ内throwing FunctionのRuntime/Errorを各独立に作り、NFC前24charのcaller入力、観測NFC後12charのnormalized配列の全0、同一failure、SQLがexistsまで4文でinsert/audit0、取得済resource終了/caller非操作を確認。null Function ctorはfailfast拒否。実provider/algorithm/credentialを操作せず、成功暗号期待は旧独立JCA三Testを保持する。旧18Boundary/4Hasher本文はbyte保持＋新1、定義は新群合計20/既security9、全29/5Main6physicalを同source一exec、RootNullAway/lint-Werror/CS/SB/PMD全site、CRC-init/既定・無filter全Codeの四100（instructionもmiss0）で検証する。元27/28は未資格として保全し新29へ加算しない。

費用は元開始.9/2.7/6.0と追補.9/2.7/3.9、現群計1.8/5.4/9.9 cap10を据置き。追補の内訳をresource .6/1.8/2.4、Hasher fault .2/.6/1.0、ADMIN direct fault .1/.3/.5へ再配賦（合計同じ）、今回追加予算0・手戻り実費/token不明。追加発見と再認証を完成率へ変換しない。原費用/SV/原904.85等/正本625・元190・正式1964/53・工数null、実DB/BootstrapAdminMain/native/RootActual4/VM/aru/全PGPT/ITST/HOLDは維持。

## SSC412 初期ADMIN資源終了と暗号失敗（2026-11-15）

SSC411/BUG2983のnull境界は保持し、PG33510全27FES0/default四100に対するPG33514無filter48instruction/20branch/1line未達を解消する内部補足。原Unit23bb667e/Core29e32fb7/PG33510-33514は成功試験27件だが全Code未資格として保存し、受入/正式/工数へ加算しない。

BUG2989/YKT2518: BootstrapAdminServiceのnull検査済みStatement/ResultSetはTWRの重複close-null分岐を残さず、明示primary+finally closeへ構造化する。shared lock→membership→tablelock→exists→insert→ACTION/SECURITYのSQL文字列・getter/setter順・normal result・消去を保持。preparedとresultのtyped null guardはそのまま使用。query/read/lockとcloseStatement/closeResultのprivate helperで、取得済み資源を一回だけ逆順にclose、SQL/Runtime/Errorは元primaryを再throwし、別secondaryだけaddSuppressed、同一objectはself-suppressionせずprimary identityを維持。primaryなしのclose故障は当故障をそのままthrow。Exception graphを通常catalogへ分類する責務は既BootstrapAdminMain側に残し、そのHOLD実class/原fixtureを実行しない。caller Connection/commit/rollback/closeを所有せず、再取得/再送/rollback新発行をしない。readはprivate固定modeによりshared Boolean(true必須)、membership void単一行、exists Boolean、ID long(N12)の既wasNull/境界/余剰行検査順を維持。到達不能として除外せず実際の全条件を独立試験で測定する。

BUG2990/YKT2519: PasswordHasher公開noargは既Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8()/hex/DelegatingPasswordEncoder pbkdf2-v1の固定factoryへdelegateし、default behavior/生成・読取algorithm/ID/公開APIを変更しない。package-private PasswordHasher(PasswordEncoder)だけを内部testability境界として設け、nonnull invariantはObjects.requireNonNull。外部設定/HTTP/DB/bean/role/provider登録からencoderを選ばせず、既Production呼出は全てpublic noargを維持。新独立PasswordHasherTest追加一件(PT-AUT-HASHFAULT001)はthrowing encoderのencode/matchesで同failureとcaller入力/観測CharBufferのNFC12char消去を確認する。SDK/provider実設定や暗号期待値の変更を行わず、null port拒否も確認。旧三Hasher Test本文・他既security六本文を保持する。

BOOTBOUND016はmanual cleanupのprimary/secondary三型全組合せをStatementとResultSet各ownerで照合し、同一Errorは従来のTWR self-wrapperではなく元object直接伝播を独立期待とする（Mainの既固定failure結果/graph責務を変更しない）。他17Boundary本文/固定SQL/normal binding/JCA期待は保持。追加new1により独立定義は新19/既security9、同source全28/5Main6physical。RootNullAway/lint-Werror/CS/SB/PMD全site/CRC-init/既定と無filter全Codeのline-method-class-branch100、例外/null/資源後条件を照合する。coverage除外/抑制/旧exec合算/合成PASSなし、実DB/ADMIN作成/BootstrapAdminMain/native/原DBfixture/RootActual4/VM/aru/全PGPT/ITSTは未受入/HOLD継続。

群PGPT-WBS65-SSC411-ADMIN-BOUNDARY18-SECURITY9-HOST27-20261115の開始.9/2.7/6.0ppと5389 eventを凍結。新発見の上記二依存に.9/2.7/3.9ppを追補し、現群合計1.8/5.4/9.9pp/cap10へ改訂、初回見積りを書換えない。前提となる自動生成分岐/消去失敗の不足のためで、原P01005/P00701費/SVを重複消化せず当追補だけ追加する。共有消費/専有実費/tokenは別記、欠測null。通常小群で停止せず現接続経路を閉じる。原904.85等/正本625受入184・元190受入17/正式1964-53/工数nullを保持。

SSC411: 既BootstrapAdminServiceにtyped JDBC null guardsを追加。新Boundary18＋既security9の全27/5Main6physical、実ADMIN/DB/native/HOLD未受入。

SSC410: MigrationMasterCopyManifest constructor/canonicalBytes/sha256/mappingSha256/rowCounts/toString/invalidと既Assembler.copyManifestを追加。全990/48Main68physical予定。

SSC409: CurrentMigrationMappingVerifier.verify/frames/rows/numeric/model-validation/invalidとCurrentMigrationMappingManifest.verifySerializedを接続。既format byte不変更、期待SHAは元宣言artifactから渡す。新18/全976/47Main67class予定。

SSC408: CurrentMigrationMappingManifest ctor/canonicalBytes/sha256/rowCounts/toString/append/invalidとCurrentMigrationAssembler.mappingManifestを接続。型・既mapping bytes/orderは不変更、新10/全958・46Main66class予定。

SSC407: MigrationCleanupIdentityTest10もFinalizerの呼出元として全948再認証、他44Test同byte。Main不変更・SSC406同群手戻り。

SSC406: Finalizer.finishへ固定link constraint即時評価をMAX/setval前一回追加、親Target同経路へ接続。既Main1＋Target doc追跡更新、新Final2/Target2=全948/45Main65physical予定。caller TX commit/rollback・実DB/HOLD操作0。

SSC405: 既Column第十一metadataでV002 false/lower(body)と他64 default不存在/atthasdef整合を検査。Column026/Target036新2と全944/45Main65physical予定。DDL/DB設定変更0・実DB/HOLD未受入。

SSC404: 既MigrationMasterColumnVerifier全66行へSS331 nk_owner絶対照合第十field。Column新025/親Target新035と全942/45Main65physical同source再認証。権限操作/DDL/実DB/HOLD変更0。

SSC403: MigrationGamesVerifier.verify/rows/row/cleanupと既Target.prepare一接続でV004二行を一致確認。new22/全45Main65physical940予定、データ修復や権限発行なし。

SSC402: CurrentMigrationAssembler constructor/assembleは同map/asset/rootから既mappersを構成しSourceSnapshot＋media宣言から六table Masterを生成。new20/全44Main64physical918予定、実Current資格/DB/原本操作なし。

SSC401: CurrentMigrationProjection.read/snapshotMode/SourceSnapshot五getterは既Current五readerを同caller Connectionへ順次束縛。new12/全43Main63physical898予定、実DB/Current順資格なし。

SSC400: CurrentAudioLinkMapper/LinkOrderは宣言source triple/orderとplacement/audio対応を検証し既AudioCopyDatasetへ接続。新24/全42Main61physical886予定、実DB/Current順oracle資格なし。

SSC399: CurrentAudioLinkProjectionReader.read/rows/row/cleanupはCurrent二signedIDと保存typeを三列snapshotへ接続。新20/一Main四100予定、実DB資格・target displayorder決定なし。

SSC398: AudioMigrationMap record/constructor/lookup/canonical/copyRowsはCurrent音声のdeclared ID/asset/正確msを既AudioRowへ結合。Asset純pathをpackage共有しFileMapperは同契約保持、new24/全40Main58class842予定、実DB/asset認証なし。

SSC397: 全migrationの通常nested Fingerprint二型を含む物理56/39Main/818件を宣言、原54集合guard失敗を保全。Main/DDL/実DBHOLDは不変更、BUG2944/YKT2473。

SSC396: SS331実効audio_roleをV030後varchar11/byte11へ補正、Row/Column/Referenceと独立fixtureを横断。全39Main/56physical/新1含818JavaPTとDDL静的は実DB未実行を分け、BUG2943/YKT2472はDB再試験HOLDを残す。

SSC395: CurrentAudioProjectionReader.read/rows/row/duration/cleanupはCurrent十列をreadonly snapshotから不変rowsへ接続。signedID-size/nullablemetadata/有界decimalを保持、独立20/四100計画、実audio/DB未資格。

SSC394: CurrentScenarioFileMapperの全7Main17physicalに対しEntryMap/Placement通常各12を加え全122へ依存閉鎖。原98FES0はcoverage不足で未資格。Main不変更、BUG2940/YKT2469。

SSC393: CurrentScenarioFileMapperの現依存Asset20を含む新24＋必要74=98/7Main17physicalへ訂正。Main/業務期待値不変、原90未実行保持、BUG2938/YKT2467。

SSC392: CurrentScenarioFileMapper.copyRows/root/parseCurrentは八列と宣言game root/asset claimを既ID-order/11列Batchへ結合。metadata一致は実file資格でなく、独立24/必要122/四100を計画、実DB/HOLD未受入。

SSC391: CurrentScenarioFileProjectionReader.read/rows/row/cleanupはCurrent八列をreadonly snapshotから不変rowsへ読む。signedID/nullable sizeと保存path/hashを非修復、独立20/四100計画、実asset/DB未資格。

SSC390: CurrentScenarioEntryMapper.copyRows/parseCurrent/validTimeは十列を既三ID対応と12列Row/Batchへ結合。Current保存値と順/nullable speaker保持、独立24/必要180/四100計画、実DB/HOLD未受入。

SSC389: CurrentScenarioEntryProjectionReader.read/rows/rowはCurrent十列をborrowed snapshotから不変rowsへ接続。旧IDsignedlong/nullable speaker-label-raw保存、独立20/四coverage100を計画、実DB未実施。

SSC388: 既ColumnVerifierへ九番目identity sequence結合・N12定義booleanを追加、既NN8/66属性保持。Column024/Target mixed9-7/必要645、sequence状態値・実DB・絶対owner/全移行/HOLD未受入。

SSC387: 既ColumnVerifierへ八番目NOTNULL n制約結合・有効性booleanを追加しgetBoolean8直後wasNull/trueを要求。66既属性不変、Column023/Target mixed8-7 metadata/必要644、実DB/NN名全体・全移行/HOLD未受入。

SSC386: 既ReferenceVerifierの22query後へ六PK/13UKの保存行重複/PKnull違反件数0を六固定SELECT追加、Reference28→Content7→Finalizerの同Connection。既Ref21/Target32 matrix拡張・新JUnit定義0/必要643、index/collation/実SQL/全移行/HOLD未受入。

SSC385: 既ReferenceVerifierへ47CHECK原式違反件数0の六固定SELECTを追加、Target同TX Reference22→Content7→Finalizer、Ref021/必要643。式catalog/実SQL evaluator/DB/全移行/HOLD未受入。

SSC384: 既ContentVerifierの六表後へ生成body_searchとDB lower(body)の不一致件数0を固定第七SELECTで照合、Target同ConnectionのFinalizer前後条件とする。Content029/必要642、式定義/実DB/全移行/HOLD未受入。

SSC383: ConstraintVerifier75明示テーブル制約だけをn,t分離queryで照合する。承認済み遅延constraint trigger自体とNOTNULL catalogは別未完、無効化・全catalog資格の主張0。

SSC382: MigrationMasterConstraintVerifierの75制約構造を既TargetPublisher.prepareのColumn後staging前へ同Connection接続、PT-CONSTRAINT22＋既Target32/必要641、全31Main45physical。実DB/全constraint意味/全移行/HOLD未受入。

SSC381: 既MigrationMasterTargetPublisher.prepareは同ConnectionでColumn66属性を全成立させてから六CTASへ進む。Target025..032/必要619、実DB/catalog全体/Rootnative/HOLD未受入。

SSC380: bootstrap.migration.MigrationMasterColumnVerifierは借用TXの六表66物理カラム属性を固定catalog queryで厳密照合する。PT-MIG-COLUMN001..022/一physical・Root静的/default-raw全Code、実DB/全catalog/constraint/index/role/全移行/HOLD未受入。

SSC379: MigrationMasterTargetPublisherは既Reference後→Content65列後→Finalizerの同借用Connection経路を持つ。独立Target017..024/全589、実DB/全移行/HOLD未受入。

SSC378: bootstrap.migration.MigrationMasterContentVerifier verify/expectedRows/orderedRows/typedValue/resource cleanupは借用migration TXに対する六表65COPY列の固定SELECT型付きpost確認を担う。独立28/whole411、実DB/catalog/全移行/公開/Rootnative/HOLD未受入。

SSC377: 五既JDBC移行部品cleanupのprimary自己identity保持、BUG2925/YKT2455/独立10/必要553。認証/接続/DB/全移行を代行しない。

SSC376: bootstrap.migration.CurrentSpeakerProjectionReader read/open/row/cleanupはCurrent六列のborrowed readonly snapshotを不変六列rowsへ接続し、既Mapへ渡す。SQL NULL/semantic boolean/件数/逆順cleanupをJDKProxy独立20/whole176で確認。実CurrentDB/認証/HOLD未受入。

SSC375: bootstrap.migration.SpeakerMigrationMapとSpeakerMappingはCurrent ID→NK ID canonical対応とCurrent六選択列→SpeakerCopyBatch変換を持つ。固定redaction/全単射/null/時刻・Row invariant。PT-MIG-SPEAKERMAP001..024/全156/full10Main17physical、実Current/DB/HOLD未受入。

SSC374: bootstrap.migration.MigrationMasterCopyFingerprintはfingerprint/differenceと不変TableFingerprint、private DigestSinkを持つ。既六表writerをstream SHA/long countへ接続、PT-MIG-FINGER001..020/全403/full23Main38physical。実master/DB/署名/全移行/HOLD未受入。

SSC373: bootstrap.migration.MigrationMasterTargetPublisherは既三staging/transferと参照/最終化を同じ借用Connectionへ固定順接続、元障害伝播/後続0/自動retry0。PT-MIG-TARGET001..016/全543/full28Main42physical、実COPY/DB/Go/Root/HOLD未受入。

SSC372: bootstrap.migration.MigrationMasterReferenceVerifierは六count/九orphan-game/link order違反groupを固定read-only16SQLで照合、借用Connection/nonnull終了/元primary維持。PT-MIG-REF001..020/全403/full23Main36physical、全DB/hash/catalog/移行/HOLD未受入。

SSC371: bootstrap.migration.MigrationMasterFinalizerは借用正規Connection上の五MAX照合→五Prepared setval→六限定ANALYZEを行う。nonnull cleanup/固定診断/自動再試行0。PT-MIG-FINAL001..028/全411/full23Main36physical。実DB/原本/復旧/HOLD未受入。

SSC370: bootstrap.migration.MigrationMasterCopyDatasetはSpeaker batchと既五表datasetを不変保持、六表時刻/Entry FKと六借用stream前検証・順序を持つ。PT-MIG-MASTER001..020/必要383/full22Main35physical。実master/DB/全移行/HOLD未受入。

SSC369: bootstrap.migration.SpeakerStagingTableはspeakers七列のCTAS/3count/large INSERT/nonnull資源終了を標準JDBCで持つ。Speaker先行→Scenario二表→Asset三表を同一借用Connectionで独立Proxy検証。実DB/Current175/driver COPY/全移行/Root/HOLD未受入。PT-MIG-SPEAKERSTAGE001..024/whole96/full3Main4physical。

SSC368: bootstrap.migration.SpeakerCopyBatchは解決済みSpeakerRow集合のPK/ゲーム別normalizedUK/時刻とEntryのspeaker/game参照を検査し、宣言順の不変rowを借用writerへ渡す。名前を変換せずCurrent抽出/実175/DBを代行しない。PT-MIG-SPEAKERBATCH001..016/必要whole132/full9Main15physical、全HOLD不変更。

SSC367: bootstrap.migration.SpeakerCopyRowはUI242/SS331/V002の解決済みspeaker七列のimmutable/null/byte/date/COPY契約のみを持つ。Current抽出/正規化導出/UK-FK/全175/DB/Rootを代行しない。PT-MIG-SPEAKERROW001..016/必要codec12/full28、全HOLD不変更。

SSC366: ScenarioStagingTables/AssetStagingTablesの6資源scopeは同じSQL/borrowed transaction契約のままnonnull所有/型別closeとprimary-suppressed順を明示する。private helperのみ、PT-MIG-CLEANUP001..004/必要403、Root品質/全HOLD不変更。

SSC365: COPY四final aggregateのconstructor防御copy/deep immutable/借用streamだけの契約を標準Immutable annotationで明示する。全method/test body不変、Root品質/全物理/static0/通常399の条件は維持。

SSC364: bootstrap.migration.MigrationCopyDatasetは同じScenarioCopyDatasetからAudioCopyDatasetを構築しMediaAssetCopyBatchと五表共通created_at/借用五stream順を保持する。不変宣言値のみ、SQL/SDK/実DB/transaction/原本操作0。PT-MIG-FIVE001..020、必要whole399、全移行/Root/native/HOLD未受入。

SSC363: ScenarioFileMigrationMap/ScenarioEntryPlacementMap内部二要素キーをJDK不変List<Long>へ簡素化。公開六record/永続化/順序/重複拒否/redactionは保持。PT-MIG-SCENARIOGEN001..016と必要whole129で同source全9Main15physical/default+無filterCodeを確認、実DB/Root/native/HOLD未完。

SSC362: bootstrap.migration.AssetStagingTablesはaudio_files/media_assets/entry_audio_links三表の固定CTAS/count/large INSERTを標準JDBCで所有し、connection/transactionはcaller借用。既Scenario二表を先行、全5表の順/資源をProxyで検証。実DB/素材/認証/全ETLは上位、vendor/native依存0。PT-MIG-ASSETSTAGE001..030。

SSC361: bootstrap.migration.MusicMigrationCatalogueはMusic129宣言Entryとtarget IDsをCurrent title/group・既Pairing・MusicID・MediaRowへ結合し保存role/key/orderを固定。Video20と既MediaBatch149接続は独立メモリPT、実素材/DB/全ETLは上位、API/Web/vendor依存0。PT-MIG-MUSICCAT001..024。

SSC360: bootstrap.migration.MusicMigrationPairingは曲一groupの宣言path/titleをCurrent規則でPair/Resultへ固定。手書きimmutable値・shadowed内部照合、実素材/DB/group分割は上位、API/Web/vendor依存0。PT-MIG-MUSICPAIR001..026。

SSC359: bootstrap.migration.MediaAssetCopyBatchはMediaAssetCopyRow九typed getterを使用し、宣言集合のPK/UK/親FK/同時刻とAssetManifest一致をCOPY前に検査する。writer借用終了責務を保持、API/Web/vendor依存0、実素材/DB/全ETLは上位。PT-MIG-MEDIABATCH001..020。

SSC358: bootstrap.migration.VideoMigrationCatalogue/手書きnested VideoはUI223全20固定metadataを所有し、宣言AssetManifestとtarget IDsをMediaAssetCopyRowへ結合する。既bootstrap部品だけに依存、API/Web/vendor依存0、実素材/DB/全ETLは上位。PT-MIG-VIDEO001..024。

SSC357: bootstrap.migration.MediaAssetCopyRowはSS34310.1.4/SS331/V002+V029/SS333のmedia_assets十七列値とpair/type-MIME/MusicIDを検証し既encoderへ渡す。既MusicLogicalIdと同module、業務API/Web/PG vendor SDK依存0、実DB/全ETLは上位。PT-MIG-MEDIAROW001..020。

SSC356: bootstrap.migration.MusicLogicalIdはUI242/SS34310.1.3のNFC display path UTF8と固定prefixによるSHA256 logical ID生成だけを所有。Java標準以外の業務API/Web/PG vendor依存を追加せず、Current対応/実DB/全ETLは上位。PT-MIG-MUSICID001..012。

SSC355: bootstrap.migration.AudioCopyDatasetはSS34310.1.4/SS331/V002のaudio_files/entry_audio_linksを既EntryBatch・AudioRowへ結合しPK/UK/二FK/時刻を検証、既Writerへ二streamを渡す。業務API/Web/PG vendor SDK依存を追加せず、実DB/全ETLは上位。PT-MIG-AUDIODATA001..020。

SSC354: bootstrap.migration.AudioFileCopyRowはSS34310.1.4/SS331/V002のaudio_files十二列値を検証し既PostgresCopyTextEncoderへ渡す。既存Scenario値/業務API/Web/PG vendor SDKへの依存を追加せず、実DB/全ETLは上位。PT-MIG-AUDIOROW001..016。

SSC353: bootstrap.migration.ScenarioStagingTablesはSS34310.1.4の固定二temporary CTASとtarget空/六scalar・固定二INSERT/後条件だけを借用JDBC transactionへ発行。標準java.sql、業務API/Web/PG vendor SDK依存を追加せず、接続/transaction所有・全ETLは上位。PT-MIG-STAGE001..018/TRANSFER001..020。

SSC352: bootstrap.migration.ScenarioStagingTablesはSS34310.1.4の固定二temporary CTASだけを借用JDBC transactionへ発行。標準java.sql、業務API/Web/PG vendor SDK依存を追加せず、接続/transaction所有・全ETLは上位。PT-MIG-STAGE001..018。

SSC142（PG406、BUG402/YKT322）：SSC137のAPI/Web Rootは、SSC084で既に共用Bootstrapへ置いた固定role `api.bootstrap.ServiceDatabaseSource` をown roleの単独物理JDBC sourceとして再利用する。互換binary名はAPI artifact依存を意味しない。Batchの閉鎖import検査はこの一型と既存ApiNonSecretConfigを明示参照し、実Bootstrap source所属と既定POM依存集合を独立照合する。wildcard・API業務class・任意Source/role・BootstrapへのHTTP/JMS追加は許可しない。普通API/Web private credential reader・role契約は不変更、RootのDB/秘密/resource寿命はSS342/343・PT297で別検証する。

SSC126（PG395、正規issuer接続の内部依存）：ApiNonSecretConfig/WebNonSecretConfigの純粋scalar parser・独立PTをbootstrapへ移す。既存api/web.* binary名は互換名で、業務moduleへのartifact依存を意味しない。固定defaults/strict YAML/role別許容key/正確effective canonical SHAは保持し、Root Morningと各appが同じ実装を利用する。APIの6Queue名はSS321/343の固定default集合だけを照合しProtocol enum依存を持ち込まない。SnakeYAML3.1.1は既存API/Webと同version、sharedはStorageだけへの内部依存・HTTP/JMS/業務repositoryなし。通常API/Web/Rootへのcredential配布は変えない。新共用framework/設定fallback/業務profileを追加しない。

SSC088: 共用bootstrapへSSC086の非秘密canonical proof/固定service NSS/子自己bindingも収容し、root Batch→bootstrapを許可する。API/Web→bootstrapとbootstrap→Storageだけの内部依存、Web→業務API禁止、Storage native-only/no-JDBC、bootstrapへ業務HTTP/JMS追加禁止を維持する。root Batchのschema read-only validateにはFlyway core compile/PG plugin runtimeを使用する（従来test限定から具体化）。通常serviceへmigration/Ops credentialを配布しない。公開snapshot・native2FDだけで全root/current permit/schema/Ops readinessを代替しない。

SSC084/PG289: `src/schubert-nk-bootstrap`を共用起動libraryとしてStorageの後、API/Webの前へ追加する。固定資格情報のstrict material/保持inode読取と固定role JDBC admission/sourceだけを移動し、HTTP/JMS/業務repository/process entry/DDLは含めない。API/Webはbootstrapを参照でき、bootstrapはStorageだけを内部依存とする（JDBCはJDK、PostgreSQL driverはruntime）。Storageのnative-only/no-JDBCとWeb→業務API依存禁止は維持する。移動対象11classの既存api.* package/binary名は互換名として保持し、artifactのAPI依存を意味しない。対象と試験owner/再検証方針は473、SSC084へ追跡。RequiredColumnは業務APIに残し、bootstrap DB admissionはそのSQL NULL拒否を自身の固定08001契約で扱う。秘密/権限/外部画面仕様は変更しない。

SSC062/PG169: .batch.file.BackupManifestReaderはSS341§6.7のroot MANIFEST保持inode読取りを所有し、constructor/read・metadata/bounded IO/safe close/clockを017046・047/BAT226～241へ追跡する。callerの原本両handle/name照合、root/child/entry前後検査までを担い、任意root侵害、root生成/実3archive/DB成功/7世代/親OS寿命は保証しない。依存は既存Batch/Storage/Java標準、PG168正式12中は設計のみ先行。

SSC060/PG167: Batch .platform.InspectorUnitSnapshot（固定18property/値/必要終端条件/fresh receipt）とInspectorUnitProbe（固定show・GetUnitProcesses・同状態照合/所有stdio/固定例外）を追加予定。既存API/Web停止確認とは用途を分離し、start/stop/親callback/OS lockを所有しない。全public/private method・native helperはOPS009/UI251/SS341 §7.4・343/018021～024・PT-OPS-UNIT-001～016へ対応。依存は既存Batch/Java標準のみ、systemd設定そのものの変更は含まない。

SSC059/PG166: .batch.file.BackupArtifactVerifierは341 §6.5の信頼manifestと実4fileのread-only一致・保持inode/metadata/ACL/size/hash/byte/再binding・owned closeだけを担う。BAK/BKO/UI251/SS341・343、017038/039/BAT194～209でconstructor/verify・全内部port/snapshot/safe-close/streaming/時計のmethodを追跡する。実backup生成/DB信頼binding/世代管理やroot/OS authorityをこの結果から発明しない。

SSC058/PG165の追加責務: .batch.backup.BackupFileDigest/BackupVersions/BackupManifestは341 §6.4の申告観測値・3file/両完全handle/時刻/version/正size/hashの不変条件。.batch.file.BackupManifestCodecは固定順ASCII JSON/末尾LFとcanonical roundtrip。BAK001～008/BKO001～008/UI251/SS341・343、BAT178～193/017033～036へ全methodを追跡。実artifact I/O/worker/root/DB binding/世代管理は別未完了。module依存を追加せず既存BatchStepAttempt/BatchRunを共用する。

SSC057/PG164の追加責務: .batch.repository.CleanupKind.stepは既定step対応、CleanupStepChunk/Reasonは今回chunk・明示optional step保存累積・未完了/deferredの型契約、CleanupStepRepositoryは331 §3.14のV020固定7bind/7列/前後run identityとborrowed資源境界。.batch.cleanup.StepCleanupSummary/StepCleanupServiceは同step累積と今回呼出差分・30分/割込・chunk commit/rollback/restoration・END/deferredを扱う。OPS009/DAT009/UI251/SS331・332・341/SSC057、DB259～266・BAT154～177を追跡。親main/実unit/backup/他cleanupは別未完了。

SSC049/PG162（先行d23b1afd）: batch.repository.InspectionSummaryRepositoryは331 §3.13のborrowed read、InspectionSummaryはBatchRun/CleanupCounts/completeの非秘密不変projectionを所有する。batch.cleanup.InspectionAttempt.reconcile(expectedRun,before Optional summary,after summary,receipt int)は341 §7.3の保存END/identity/非減少/既完了不変/0・10とattempt差分を照合し、run/cumulative/attempt/Outcomeの不変値を返す。Outcome SUCCESS0/WARNING10。各constructor/factoryはnull/非負/相互不変条件を確立し、identityはtoStringでredact。API moduleのclassへ依存/複製せず、既存CleanupCountsを共用する。NULL/未知値を成功に変換しない。OPS009/DAT009/MQ008/UI212/241/251、SS331/332/341、DB251～258/BAT114～129。値だけでfresh unit起動/実子終端/OS lock/backup/親step記録を完了としない。

SSC055/PG161（先行4d534ba9→SS/PT b572baa5）: MaintenanceRunFiles.SessionへretirementCandidates/retireを追加し、固定6root・借用RunReferenceRepository照会・完全plan/marker・限定原本退役をSS343 §6.16で所有する。MaintenanceRetirementはrun/latest/prepared/count/digestの不変型、MaintenanceRecordsはNKRET1 codec、DurableRecordFilesは.plan/.retireのcanonical内容ID束縛、EnvironmentInodePolicyはdurable最大204byte（BUG171/YKT132）。private Inventory/graph/digest・全mutation前後照会は上記Session責務。Digest factoryはchecked失敗/nullを試験可能にするpackage内portで、外部設定や任意algorithm選択を提供しない。BUG172/YKT133でoriginal不在の3root barrierをplan消去前に要求。OPS009/DAT009/UI251/SS331・332・341・343、017/015・016/BAT090～113。OS flock/親終端/backup/IT/STを部品成功から推測しない。

SSC-055/PG-D-159（先行4c5dcb85）: batch.repository.RunReferenceRepositoryは親Connectionを借用し、explicit READ COMMITTED/read-write transactionと前後割込を検査、331 §3.12の固定PreparedStatementへBatchRunをbindする。queryTimeout5秒、statement/result/null4列/1行だけ、全close成功後にimmutable RunReferences（history/inbox/log/identityConsistent）を返す。全参照なしでinconsistentは不正projection。anyReferenceは3flag OR、値toStringはredacted。Connection commit/rollback/close/config変更/新接続をしない。SQLException/不正projectionは全資源close後の固定BatchRepositoryException、未知Runtime/NPEは正常化しない。null constructor/runはprogramming契約。OPS-009/DAT-009/UI251/SS331・332・343、017の013/014・PT-BAT-082～089。

SSC-055/PG-D-158（先行36b5f85b）: batch.file.MaintenanceRunFilesは固定6rootの操作scope・Session寿命・全record scan/graph・start/resume/completeを所有し、PG157のDurableRecordFilesへ限定IOを委譲する。返却のrun再開状態はimmutable activationとOptional completion。SS343 §6.15、OPS-009/UI251/SS341、NK-BAT-001/017の011・012/PT058～081。OS lock/実親/DB legacy照合/GCを本file scopeへ完了扱いで混入しない。

SSC-055/PG-D-157（先行19e22eb4）: batch.file.DurableRecordFilesは借用private永続rootの限定read/publish/remove、EnvironmentInodePolicy.durableはlocal RW/root0700・file0600検証を共有する。SS343 §6.14、NK-BAT-001/OPS-009/UI251、017の009/010・PT-BAT-046～057へ追跡。固定namespace/graph/OS lock/親終端/GCを低位IO成功で代替しない。

SSC-055/PG-D-156（先行b6b5f0f6）: batch.repository.MaintenanceActivation/MaintenanceCompletionは固定BatchRunと起動単位・完了単位のimmutable契約。batch.file.MaintenanceRecordsはSS343 §6.13の3種canonical ASCII encode/decodeだけを担う。原本からの同run照合・OS lock・private永続file・active/完了/crash/GCは親と後続file storeの責務でありparserに成功保証を混入しない。NK-BAT-001、OPS-009/UI251/SS331・341・343、PT-BAT-038～045へ追跡する。

SSC-049/PG-D-155（先行023017b2）: batch.platform.ConfigurationGroupResolverは固定OS NSS group照会のbounded process/byte検査だけを担当する。batch.file.InspectorEnvironmentFilesは固定/etc・/run祖先からrootを保持し、static reader・runtime publisherと同期callbackを全close込みで結線する。任意path/account/commandの公開入口はなく、親OS lock/実子終端/backup/run原本はcaller必須契約。OPS-009/UI251/SS343 §6.12、PT-OPS-GID-001～008/NS-001～008。

SSC-049/PG-D-154（先行aa2baa3a）: batch.file.InspectorEnvironmentPublisherはroot保持run fileの新規原子公開/同run再同期/停止確認後retireを担当する。EnvironmentInodePolicyは既存readerとpublisherが共用するpackage限定Unix/ACL/FS検査。公開factoryで任意path/UID/commandを受けず、借用capabilityのadmission/OS lock/子終端は親の責務。OPS-009/UI251/SS343 §6.11、PT-OPS-PUB-001～012。

SSC-049/PG-D-153: storageのDirectoryCalls/LinuxDirectoryCalls/OwnedTransferDirectoryへprivate0600 create・同directory単一名のno-replace publish・検証済みentry unlinkを追加する。file adapter専用で設定/DB/認証/run modelへ依存しない。通常Transfer writerとWeb readerの許可操作は変更せず、保守側のpolicyはbatch.fileへ置く。NK-OPS-001、OPS-009/UI251/SS333 §7.3/343、PT-OPS-PFILE-001～008。

SSC-049/PG-D-152: batch.file.InspectorEnvironmentReaderがstatic/runtimeの既存環境fileを保持inodeからbounded readし、属性・同名再取得・close後にplatformのCFG/ENV byte検査へ渡す。借用rootの選択/寿命とOS排他は親、読取り専用で公開/修復しない。NK-OPS-001、OPS-009/UI251/SS343 §6.9、PT-OPS-EFILE-001～008。

SSC-049/PG-D-151: batch.platform.InspectorStaticEnvironmentはSS343 §6.8の静的2行fileをMap化前に検証する非秘密byte境界。DB connectorや秘密鍵をbatchへ持込まず、子API launcherの値検証と両側で同じSSを満たす。file属性/読取/公開の責務はbatch.file、子起動と同run確認は親platformへ分離する。NK-OPS-001、OPS-009/UI251、PT-OPS-CFG-001～006。

SSC-049/PG-D-150（先行0797b369）: batch.cleanup.InspectorLockHandoffはSS341 §7.3の親Connectionのadvisory解放・同期callback・finally再取得だけを担う。借用transaction/connectionのcommit/rollback/close、実process/OS lock/backup/run原本には責務を広げない。NK-BAT-001、OPS-009、UI251、PT-BAT-030～037。JDBC scalar/資源終了の固定診断と未知programming failureの非成功を検証する。

SSC-049/PG-D-149（2026-09-09、先行17b06c0c）: batch.platform.InspectorRunEnvironmentはSS343 §6.8のrun専用EnvironmentFileのcanonical ASCII生成・期待runとの全byte照合だけを担う。BatchRunの検証契約を再利用し、時刻取得・file IO・root/lock/backup/起動・永続原本の確定を行わない。NK-OPS-001、OPS-009、UI251、PT-OPS-ENV-001～004へ追跡する。

SSC-049/PG-D-148: batch.platform.ApplicationStopGateはAPI/Webの固定2unitをread-only照会し、UnitStateParserの厳密な7property契約で停止を確認する。SystemctlStateSourceだけが固定systemctl show・制限環境・5秒/1024byte境界を所有する。停止/起動や任意unit/commandの実行入口を追加しない。親OS lock/再起動禁止/実backup/DB引渡しは別責務で、観測結果を永続的な停止leaseとして扱わない。

SSC-049/PG-D-147: batch.file.MaintenanceFileLockはroot controller内部だけの固定runtime admission adapterとする。storageの保持directory/inode/実Linux flockを借用し、固定/run配下の所有・型・mode・ACL・local tmpfs・identityを確認した保守callbackをOS lock下で実行する。公開factoryにpath/UID/commandを渡す入口を作らない。batch→storage依存を追加しAPI/Webへの逆依存は禁止。停止/backup/DB排他引渡しを低位lock取得結果だけで代替しない。

SSC-028: Shared storageの既存保持directory/inodeへ、Asset adapter向け既存child/entryのread-only能力と正サイズfile属性照合を追加する。Transfer専用UUID/date/48MB入口は維持し、API/Webのnative実装複製やProtocolからfile I/Oを行わない。詳細はSS333 §7.2、PG-D-073/PT-MED-018～020。

## 1. 目的・追跡

SSC-027具体化: `.api.application.scenario.ScenarioApplicationService`がSyncRequestProcessorとして内部段階処理を所有する。process/decode/guard→inspect（非更新認証/Inbox/query）→prepare（DB外file）→complete（再認証/通常Inbox/必要時descriptor暗号置換）→commit/close後replyの順。Private sealed Work/Preparedで新規query・確定error・既存snapshotを区別し、repository/storage実装を同classへ複製しない。JMS send/ACKは既存SyncRequestListener、root/鍵closeは起動所有者。single-instance/full root/readinessを実装するまで本番dispatcherへ登録しない。PT-SCN-009-T01～T07。

Web Java、API Java、batch、固定長共通部品のMaven module、package、主要class、責務および依存禁止を定める。

- 関連UI: 211～213、221～237、241～243、251～253、261 SS-001/007～013
- 関連RD: SYS-002、SYS-005～011、MQ-001～045、DAT-001～011、OPS-001～005
- 関連QA/RDF/UIC: QA-001～040、RDFなし、UICなし

## 2. Maven module

| Module/artifact | 実行形態 | 責務 | 依存可能 | 依存禁止 |
|---|---|---|---|---|
| `schubert-nk-protocol` | Library jar | 256 byte header、64 layout record、codec、NFC/byte検査、共通result/error、descriptor model | Java標準API、test時だけJUnit | Spring MVC、JMS、JDBC、DB entity、HTTP model |
| `schubert-nk-storage`（SSC-021） | Library jar | Linux保持directory/inode、NOFOLLOW・非上書き公開、OS属性/root配置の低位契約 | Java25標準NIO/FFM、null annotation、testだけJUnit | Protocol業務model、Spring/JMS/JDBC、HTTP/DB model、認証・Inbox・quota業務 |
| `schubert-nk-web` | Executable jar | MVC/Thymeleaf、HTTP validation、Spring Security、暗号化HTTP session、JMS request/reply、file配信、Web log outbox | protocol/storage、Spring Web/Security/JMS/JDBC | 業務schema repository、業務状態更新、API module |
| `schubert-nk-api` | Executable jar | 固定長request Consumer、認証・認可、application service、PostgreSQL業務schema、outbox/inbox、async worker | protocol/storage、Spring JMS/JDBC/Security crypto | MVC/Thymeleaf、Browser response、Web technical table更新 |
| `schubert-nk-batch` | Executable jar/oneshot | Backup検証、business/technical cleanup、transfer cleanup、Expiry保守、run記録 | Spring JDBC、PostgreSQL/Artemis管理client | HTTP公開、業務Consumer、任意table/Queue操作 |
| Root project | Aggregator | Maven Wrapper、Java 25 toolchain、dependency/version、品質plugin | 上記module | Production sourceの直置き |

Group IDは`dev.codex.schubert`、Java package rootは`dev.codex.schubert.nk`とする。Java module systemの`module-info.java`は
Spring reflectionとの運用複雑性を避け初期releaseでは使用しない。Mavenのmodule依存とArchUnitで境界を検査する。

## 3. 共通依存規則

```text
schubert-nk-web   ─┐
                   ├──> schubert-nk-protocol
schubert-nk-api   ─┘

schubert-nk-batch      （protocolへ依存しない。Expiry message本文をdecodeするDLQ整合toolだけは
                         protocolを明示dependencyとして利用可）
```

- WebとAPIは互いにcompile/runtime依存しない。
- SSC-021: Web/API/batchのfile adapterだけがstorage libraryへ依存可能。Controller、application/domain、Protocolからstorageへの依存を禁止する。API/Web間のclass複製やProtocolへfilesystem実装を移す方法は採らない。既存API `.api.storage`から純粋な低位7classを`.storage`へ移し、業務writer/record codec接続/quota/readiness wiringはAPIへ残す。Native SPIのFD整数を公開service/HTTP/DB/電文/ログへ渡さない。
- Protocolは外部frameworkから独立させ、同一jar hashをWeb/APIで使用する。
- HTTP form/view model、DB row/entity、固定長layout recordは別classとし、mapperで変換する。
- `controller -> web application facade -> messaging adapter -> protocol`の向きだけを許可する。
- APIは`messaging adapter -> application service -> domain/persistence/file adapter`の向きとし、repositoryから上位層を呼ばない。
- Batchはallowlist済みrepository/functionとOS command adapterだけを使用し、API serviceを流用して公開処理を起動しない。

SSC-021の依存補足: Web/APIはprotocolとstorageをそれぞれ参照し、両libraryは互いにも依存しない。Batchは承認済み保守file操作に限りstorageを使用できる。Executable process数、HTTP/JMS経路、業務DB権限は変更しない。

Storage package `.storage`はDirectoryCalls/LinuxDirectoryCalls、OwnedTransferDirectory、StorageIoException、StorageIdentity、StorageAttributeGuard、StorageRootLayoutを持つ。Class/operationはfile adapterから使える公開契約へ限定して可視化し、native symbol binding・entry FD実装・状態lockをprivateに保つ。必要なnative accessは利用processへ明示設定し、起動時にfail closedで検証する。

## 4. `schubert-nk-protocol`

SSC-049/PG-D-133: storageへ低位InodeSecurityCalls/LinuxInodeSecurityを追加し、保持inode callback内のaccess ACL/readonly filesystem flag/effective UIDだけを公開する。業務認証やkey内容を扱わず、APIのcredential file adapterがSS343 §6.2のpolicyと組み合わせる。任意path・symbol・attribute名を受けず、native実装をAPIへ複製しない。検査processも明示native-accessを必須とする。PT-DB-INBOX-121～128。

SSC-049/PG-D-146: storageのLinuxFileLockは保持済みregular inodeへの低位scoped flockだけを担当し、batch file adapterから利用する。呼出しは保持callback中の固定/proc/self/fd能力と閉じた業務callbackに限定。任意pathや生FDをserviceへ公開せず、OS user/ACL/root/実backup/DB transactionはbatch側の別責務。FFM bindingはshared storageへ集約、FileChannel.lock/fcntlをflockの代用にしない。PT-OPS-FLOCK-001～008。

### 4.1 Package

| Package | 主要class | 責務 |
|---|---|---|
| `.protocol.header` | `CommonHeader`, `MessageKind`, `InteractionKind`, `ResultCode` | 共通headerの型安全な表現 |
| `.protocol.layout` | `LayoutId`, `LayoutDefinition`, `LayoutRegistry`, `LayoutPayload` | Layout ID/version、data/record長、最大件数、Q/S/E制約 |
| `.protocol.layout.auth` | `LoginRequest/Response`, `LogoutRequest/Response` | IF-001/002のlayout record |
| `.protocol.layout.scenario` | `Game*`, `Speaker*`, `Scenario*`, `Route*`, `ScenarioFile*` | IF-003～008 |
| `.protocol.layout.media` | `Audio*`, `Animation*`, `Music*`, `MediaDescriptor` | IF-009～016 |
| `.protocol.layout.log` | `LogSearch*`, `WebLogEvent` | IF-017、IF-I02 |
| `.protocol.layout.admin` | `User*` | IF-018～024 |
| `.protocol.layout.question` | `Question*`, `Notification*`, `QuestionWork` | IF-025～031、IF-I01 |
| `.protocol.codec` | `FixedWidthEncoder`, `FixedWidthDecoder`, `HeaderCodec`, `PayloadCodec`, `FieldCodec` | byte列との相互変換 |
| `.protocol.validation` | `ProtocolValidator`, `FieldValidator`, `Utf8Validator`, `LayoutValidationException` | 構造・型・必須・許容値の受信前検査 |
| `.protocol.file` | `LargeResultDescriptor`, `LargeResultRecordCodec`, `MediaDescriptorValidator` | Transfer/media descriptorの構造検査 |
| `.protocol.time` | `JstWireTimestamp` | 17桁JST日時のparse/format |

`LayoutPayload`はsealed interfaceとし、各data/recordをJava `record`で定義する。Record constructorはnull、range、enumを検査するが、
encode後byte長は`FieldCodec`を正とする。`LayoutRegistry`は64 layoutを起動時に登録し、ID重複、長さ式、最大body 1,000,000 byteを
検査する。

### 4.2 Codec class

| Class.method | 引数 | 戻り値 | 例外 |
|---|---|---|---|
| `FixedWidthEncoder.encode` | `WireMessage<? extends LayoutPayload>` | `byte[]` | `MessageEncodingException` |
| `FixedWidthDecoder.decode` | `byte[]`, `TransportMetadata`, `ExpectedRoute` | `WireMessage<?>` | `PermanentProtocolException` |
| `HeaderCodec.peek` | 256 byte以上のbody | `CommonHeader` | `PermanentProtocolException` |
| `FieldCodec.encodeText` | value、field definition | 規定長`byte[]` | `FieldEncodingException` |
| `FieldCodec.decodeText` | field slice、definition | `String`/empty | `PermanentProtocolException` |
| `ProtocolValidator.validateTransport` | decoded message、JMS property snapshot | `void` | `PermanentProtocolException` |

JMS classはprotocol moduleへ渡さず、Web/API adapterが必要propertyを`TransportMetadata`へ写して検証する。

## 5. `schubert-nk-web`

### 5.1 Package

| Package | 主要class | 責務 |
|---|---|---|
| `.web.bootstrap` | `WebApplication`, `StartupInvariantValidator` | 起動、layout/root/Queue/session設定検査 |
| `.web.config` | `WebMvcConfig`, `SecurityConfig`, `JmsClientConfig`, `WebProperties` | Framework wiringと外部設定束縛 |
| `.web.controller` | `LoginController`, `MenuController`, `ScenarioController`, `MediaController`, `AnimationController`, `MusicController`, `LogController`, `UserAdminController`, `QuestionController`, `NotificationController`, `ErrorController` | HTTP endpoint、form binding、view選択 |
| `.web.form` | 画面別`*Form`、`*SearchForm` | HTTP入力とfield error。MQ recordを保持しない |
| `.web.view` | 画面別`*ViewModel`、`PageViewModel`, `FlashMessage` | Template表示専用model |
| `.web.mapper` | `ScenarioWebMapper`, `AdminWebMapper`, `QuestionWebMapper` | Form/viewとprotocol recordの変換 |
| `.web.messaging` | `JmsRequestReplyClient`, `ReplyCorrelationRegistry`, `WireMessageFactory`, `ResponseMapper` | Persistent送信、2秒待機、相関、response検証 |
| `.web.security` | `MqAuthenticationProvider`, `AuthenticationContext`, `ApiAuthorizationFailureHandler`, `TrustedClientAddressResolver` | Login MQ認証、context保持、Web側role/owner gate |
| `.web.session` | `EncryptedWebSessionRepository`, `SessionAttributeCodec`, `PendingRevocationRepository`, `ContextRevocationRetrier` | Technical schemaだけを使う暗号化session/Logout再試行 |
| `.web.operation` | `OperationTokenService`, `OperationTokenStore` | UUID発行、session全用途pending＋consumed合計10件、初回完成印・consumed退役・PRG/timeout時の保持（QA049/SS314・324） |
| `.web.media` | `DescriptorFileResolver`, `MediaRangeService`, `LargeResultReader`, `ContentDispositionFactory` | Root/path/hash/Range/file配信 |
| `.web.logging` | `HttpRequestLoggingFilter`, `WebLogOutboxRepository`, `WebLogDispatcher`, `RedactionPolicy` | Local JSON＋WLGEVT01 outbox |
| `.web.error` | `GlobalWebExceptionHandler`, `ProblemViewFactory` | 400/401/403/404/409/416/503の共通表示 |

### 5.2 Controller依存禁止

ControllerはJDBC、JMS template、filesystem APIを直接呼ばない。Controllerからは画面単位facadeを呼び、facadeがmapperと
`JmsRequestReplyClient`を組み合わせる。Media endpointもdescriptor取得をAPIへ要求後、`MediaRangeService`へ委譲する。

## 6. `schubert-nk-api`

### 6.1 Package

| Package | 主要class | 責務 |
|---|---|---|
| `.api.bootstrap` | `ApiApplication`, `StartupInvariantValidator` | 起動、migration/version/root/codec整合検査 |
| `.api.config` | `ApiJmsConfig`, `DataSourceConfig`, `SecurityCryptoConfig`, `ApiProperties` | Consumer、pool、credential、設定 |
| `.api.messaging.inbound` | `SyncRequestListener`, `QuestionWorkListener`, `WebLogListener`, `InboundMessageGuard` | Queue受信、property/body検査、delivery count分類 |
| `.api.messaging.outbound` | `ReplySender`, `DlqSender`, `OutboxDispatcher`, `JmsMessageFactory` | Reply/internal work/DLQ送信 |
| `.api.dispatch` | `RequestDispatcher`, `LayoutHandlerRegistry`, `LayoutHandler<Q,S>` | Request layoutからhandlerへ型安全にdispatch |
| `.api.security` | `AuthenticationService`, `AuthenticationContextVerifier`, `AuthorizationService`, `LoginAttemptRepository` | Password、session、role/owner、lock |
| `.api.application.scenario` | `ScenarioQueryService`, `MediaQueryService` | 現行検索・階層・descriptor query |
| `.api.application.admin` | `UserQueryService`, `UserCommandService` | User管理と自己保護 |
| `.api.application.question` | `QuestionCommandService`, `NotificationQueryService`, `QuestionQueryService`, `QuestionWorkerService`, `AnswerProvider` | 質問、通知、取消、回答、STUB |
| `.api.application.log` | `LogQueryService`, `WebLogIngestService`, `AuditLogService` | Log検索、WLGEVT01投影、critical audit |
| `.api.idempotency` | `InboxCoordinator`, `OperationFingerprintService`, `ReplayResponseFactory` | Message/token重複、HMAC、結果再構成 |
| `.api.domain` | `AsyncJobState`, `Role`, `AccountStatus`, `NotificationType`, domain result | 業務状態・遷移。Framework annotationを含めない |
| `.api.persistence` | 画面/aggregate別`*Repository`、`*RowMapper` | Parameterized SQL、row mapping、lock |
| `.api.file` | `AssetResolver`, `MediaDescriptorFactory`, `LargeResultWriter`, `FileIntegrityVerifier` | Logical IDから許可root内fileを解決 |
| `.api.storage` | `LinuxDirectoryCalls`, `OwnedTransferDirectory`, `StorageAttributeGuard`, `TransferCapacity` | SSC-019のAPI内部filesystem capability/属性/予約会計。`.api.file`の下位技術部品で、Controller/DB/JMS/HTTPへ依存しない |
| `.api.error` | `ApiExceptionMapper`, `RetryClassifier`, `FatalProtocolHandler` | Result code、一時/恒久分類、DLQ後exit |

### 6.2 Handler規約

`LayoutHandler<Q,S>`は`LayoutId requestLayout()`、`Class<Q> requestType()`、`S handle(RequestContext,Q)`だけを公開する。
Dispatcherは認証・inbox処理後にhandlerを呼ぶ。HandlerはJMS ACK/send、HTTP、templateを扱わない。

`RequestContext`はmessage/correlation/request ID、actor user ID/username/role、受信日時、delivery countを保持するが、raw認証context、
password、全bodyを保持・`toString`出力しない。

## 7. `schubert-nk-batch`

SSC055/PG163: .batch.repository.BatchStepは既定10stepとbackup例外、BatchStepAttemptは原本BatchRun/日別attempt/開始時刻・skipのimmutable handle、BatchStepResultはterminal状態/件数/固定診断、BatchRunRepositoryは331 §8.3の借用transaction・全履歴検査・明示回復・CAS/replay。内部History rowは非秘密12列だけで原本cutoffを推測せず、全helperをBAT130～153へ追跡する。親bootstrap/OS/unit/実backupは別の未完了責務。

| Package | 主要class | 責務 |
|---|---|---|
| `.batch.bootstrap` | `BatchApplication`, `BatchCommandRouter` | `backup`、`cleanup`、`morning-run`等のcommand選択 |
| `.batch.lock` | `MaintenanceLock`, `BatchRunLeaseRepository` | OS lock＋DB run一意性 |
| `.batch.backup` | `PostgresBackupService`, `ConfigBackupService`, `BackupManifestService`, `BackupVerifier`, `GenerationPruner` | `.part`生成、検証、7世代 |
| `.batch.cleanup` | `BusinessDataCleanupService`, `TechnicalDataCleanupService`, `TransferCleanupService` | Backup gate付きDELETE、root安全検査 |
| `.batch.mq` | `ArtemisReadinessClient`, `ExpiryCleanupService` | 限定credentialによる7日超Expiry削除 |
| `.batch.repository` | `BatchRunRepository`, `CleanupRepository` | Allowlist SQL/function、件数証跡 |
| `.batch.logging` | `BatchEventLogger`, `CommandRedactor` | BATCH JSON/DB log、secret除外 |

`ProcessBuilder`へ渡すcommand/argumentは固定allowlistで組み立て、shell文字列連結を行わない。削除serviceは設定root自体を削除せず、
`SecureDirectoryStream`または同等のsymlink非追従検査を使用する。

## 8. Application共通例外

例外classは各moduleの`.error`へ置き、protocol moduleがWeb/API例外へ依存しない。

| 分類 | 例外 | 処理 |
|---|---|---|
| HTTP validation | `WebValidationException` | 同一画面field error |
| 業務 | `BusinessRuleException(resultCode)` | Transaction rollback要否を個別指定し、固定長error response |
| 認証・認可 | `AuthenticationContextException` / `AccessDeniedException` | `0102`/`0103`、deny closed |
| 対象なし・競合 | `NotFoundException` / `ConflictException` | `0104`/`0105` |
| 一時基盤 | `TemporaryInfrastructureException` | rollback、最大3回再配送 |
| 容量 | `CapacityExceededException` | `9001`、受付/生成停止 |
| 恒久protocol | `PermanentProtocolException` | 業務未実行、DLQ、非zero終了 |
| 起動不変条件 | `StartupInvariantException` | readiness false、process起動失敗 |

## 9. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-001 | Web/API/batch/protocolの4 moduleとする | UI 211/251、RD SYS-011。朝batchをAPI停止中に安全に実行し、protocolをframework非依存にする | PGでMaven reactor/ArchUnit、PTで禁止依存test |
| SS-D-002 | Package rootを`dev.codex.schubert.nk`とする | 現行`dev.codex.schubert`との由来を保ち、NKをnamespace分離 | Artifact/class名、log service名へ反映 |
| SS-D-003 | HTTP model、wire record、DB row/domainを分離する | UI 211 §5、RDの境界分離。秘密値の意図しないserialize/logを防止 | Mapper PTと全layout対応表323を必須化 |

## 10. 実装禁止事項

- Web moduleへの`schubert`業務schema権限または業務repository追加。
- Protocol moduleへのSpring/JMS/JDBC/Java serialization依存。
- Controller/Listener内へのSQL、path連結、業務transaction実装。
- API moduleからBrowserへ直接HTTP待受・HTML応答。
- Batch credentialによる任意SQL、任意Queue purge、DLQ自動削除。
- DTO/entityの`toString`へpassword、context、question/answer本文を含めること。

## 11. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Module、package、主要class、依存規則を初版作成。 |
| 2026-09-01 | SSC-002により`FixedWidthDecoder.decode`を322 §5の完全なtransport/route検査署名へ統一。 |
SSC061/PG168: .batch.repository.BackupStepRepositoryと.backup.BackupCommitServiceは341 §6.6/331 §8.3の同一真正manifest両完全stepのread/transaction確定・不明commit再読を担当する。BAK/BKO/OPS009/UI251、017041～044/BAT210～225へconstructor/inspect/complete/helperを追跡。manifest生成/信頼reader/実artifact/root/OS/最新選択/7世代は別必須。DDLやmodule依存は変更しない。
