# モジュール・package・class責務設計

SSC417: PostgresMigrationCopyPort implements MigrationCopyPort。固定六staging/列順・同借用ConnectionのPG unwrap→COPY binarywrite→endCopy/count/inactive確認。新1MainとPT source24を作るが全Test NOT_RUN_HOLD、source静的のみと区別。

SSC416: MigrationMasterCopyVerifier.verify/toString/invalid/default ctor。取得済み保持byteを防御copyしtrusted expected SHA→既宣言再構成→canonical byte完全一致。実永続化・認証なし。全1050/52Main73physical予定（自然NoCode1）。

SSC415: CurrentMigrationTransfer.transfer/SourceCounts/invalid/toString/default constructor。二借用接続の所有を変更せずread→assemble→same-target-copyへ接続。新20/whole1030/51Main72physical（自然NoCode1）予定。

SSC414: MigrationMasterCopyCoordinator.transfer/rows/toString/input/stateとMigrationCopyPort.copyを追加。caller認証/CopyIn正常終了とTX所有は別、固定六表のみ。全1010/50Main70physical（自然NoCode1）予定。

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

## SSC-418 保護読取の一時context buffer所有・例外消去（2026-11-15）

ProtectedReadWireClientの既6引数package-private構築口と全public facade APIを維持し、defaultはprivate stateless JDK操作実装に固定する。ASCII変換はAuthenticationContext.wireValueからUS_ASCIIの新規64byte、比較は既MessageDigest.isEqualでありalgorithm/認証/権限/電文/画面/再送/期限/queueを変更しない。外部設定・HTTP選択・動的loadingで切替えない。新しい7引数package-private口は内部ContextOperations（encodeとsameの二操作）を受け、operations nullをconstructorの明示nonnull preconditionで拒否する。標準実装は状態/credentialを保持しないprivate static final class、操作interfaceはpackage-privateでbinary Code0を実証し除外としない。

encodeの戻りはnullable boundaryとして宣言し、contextBytesがnull又は64以外を固定IllegalStateExceptionで拒否する。nullは未取得、非null返却時にownedとなる。長さ不正の返却bufferはhelper自身が消去してから失敗し、呼出側へ返した正規bufferだけが次の所有へ移る。第一bufferを取得した直後に外側try/finallyへ入り、その中で第二を取得して内側try/finallyへ入る。第二の取得/検査に失敗すれば取得済み第一だけを消去、比較失敗なら第二→第一をそれぞれ一回消去する。JDK内部の返却前の未到達allocationまでを消去保証したと主張しない。実OOM/Thread操作/JDK差替えで故障を誘発しない。

decodeはinstance内でこの既owned比較を使う。既catalog catchの固定INVALID_RESPONSEは保持し、変換前に既JmsRequestReplyException.preserveFatalでcause/suppressed/SQLnext/JMSlinkedのError identityを保存する。新package-private口の非fatal/不正結果だけが従来の閉分類へ落ち、Errorを通常結果へ変換しない。Root/VM/DB/SDKbackend/actual4/Root2/拒否fixtureへの代替口ではなく、元から許可された同memory-only componentの例外消去を検証する。public synthetic contextだけを用い、実token・session・鍵・原本にアクセスしない。

PTは既58全本文/独立wire/golden/timeout/並行/secret-wipeを保持し、新whole ProtectedReadContextOwnershipTestの6methodを追加する。CONTEXT001 first/second/compareの合成Errorで取得済み全buffer消去とError同一、002比較RTE内Errorの同一伝播、003通常RTEの固定INVALID_RESPONSE/消去/秘匿、004null operationsの構築前拒否、005null encode第一/第二で既取得分消去と固定分類、006不正幅0/63/65を第一/第二で与え返却済み全bufferの消去と後続comparison0。正常/不一致のdefault JDK動作・全8旧クラスは既58で再資格し、必要な同source whole64・全physical数等を推測せず新compile実物から確定する。new6と旧58を区別し、old58成功を新sourceへ流用しない。

原58群の未達carry.2/.6/1.8ppを保持し、新Source製造/SS補足/六PT分だけ.4/1.2/2.4pp追加、当群合計.6/1.8/4.2pp cap6。元群.8/2.4/7.2/cap8・元P005費・元904.85/SV各上限は不変更、carryを二重追加しない。新13Mainは変更sourceなのでRoot compiler/NullAwayでfresh compile、全9wholeTestと静的、同一64execのdefault及びunfiltered全命令/行/メソッド/クラス/分岐、CRC/init/sourceを確認する。各naturalB0/Code0は明示、全Protocol依存を含む全物理scopeの未達を保存しown/source/全194等を混同しない。global451/正式/工数/CHR/native/ITSTを受入にしない。

## SSC-419 Release署名検証の取得直後clone所有（2026-11-15）

ReleaseSignatureVerifier.verifyは既null/長さ検査とpublicDER/元manifest/signatureの同byte clone・既Crypto/JDK Ed25519を維持する。key clone直後に外try、その内でmessage clone直後に中try、signature clone直後に既Crypto try/catch/finallyを置く。finallyはsignature→message→keyの逆取得順で一回ずつ消去、既GeneralSecurityExceptionのfatal graph/Error identityと固定IOExceptionを維持する。返却前のJDK未取得allocationの消去は保証せず、実OOMを起こさない。原public API/constructor/認可/署名format/鍵の固定根/結果/期限/電文は不変更、新operation portやprivate key/実署名/配備を追加0。既9Test全文は保持、新SIGN010だけ合成RuntimeException後に同instanceを正常再利用し、三copy消去/caller不変/pinned再利用/次回独立copy/call数2を固定publicRFC vectorで確認する。同source全10、RootNullAway/静的、sameexec default/raw target全命令行methodclassbranchを照合し、StorageIoException依存の未網羅を隠さずglobal451/正式へ算入0。

BUG3015/YKT2542、状態:設計確定・main反映前、PG/通常PT未完、globalHOLD保持。

## SSC-420 Web暗号化二codecの機密取得保護（2026-11-15）

WebLogPayloadCodec.encryptとRevocationPayloadCodec.encryptで取得済みplaintext/candidateの後にnonce/AAD/emptybuffer初期化がtry前にある取得漏れを是正する。placeholderの非秘密空配列だけをowned機密取得前に準備し、既try内でplaintext copy→nonce→AADを順に取得する。従来finallyで返却済みowned全配列を消去し、返却前のJDK内部allocationは保証せず実OOMを誘発しない。既lock/ensureOpen/null/鍵version/固定AES256GCM128/nonce12/AAD/format/過去鍵/再送結果/例外catalog/既fatal guard/外部APIを保持、新provider/新crypto切替口/権限/実鍵/DB/実nonceを追加0。既Revocation7＋FailureGraph1＋JdbcGraph3＋Fatal5＋WebLog9=25Test本文と独立DataOutput/JCA goldenを保持し、新各1Testだけpublic固定鍵/nonceで初回乱数故障→別worker正常と元caller/nonce消去/既独立golden/call2を検証する。workerはFutureget5s、finallyshutdownNow/await10s確認後codecclose、process隔離内の旧JCA provider復元fixture以外のsystem操作なし。新27は当source一singleexecでfreshMain13 RootNullAway/静的/CRC/init/default及びrawを確認、対象二codecの全Codeと全191等依存scopeの未達を区別し数を実compileから確定する。旧成功/Protocol130は確認再演せず当sourceへ合算しない。

BUG3018/YKT2542、状態:設計確定・main反映前、PG/PT/全451未受入。

## SSC-421 API認証context取得保護と有限単体fixture（2026-11-15）

AuthContextCodec.encryptでplaintext取得後のnonce生成、decryptでnonce取得後のencrypted生成が既try前にある所有保護漏れを是正する。機密取得前に非秘密の空placeholderだけを準備し、実plaintext/nonce又はnonce/encryptedを既try内で順に取得する。取得済みownedだけが既finallyへ必ず届くようにし、JDK内部返却前allocationや実OOMの消去を保証したとしない。既stateLock/close/nonnull/鍵version/前鍵/固定AES256GCM128/nonce12/NKENC1/identityAAD/例外分類/public APIを保持し新crypto/provider/権限/secret口0。全MainはAuthCodec/Identity/Encrypted/CryptoException/package-infoの5sourceと現在Protocol同byteだけ、Actual4/Root2/実DB/実鍵/SDKbackendの代替口を作らない。原whole7の独立DataOutput/JCA expectedと業務assertを維持し、caller-monitorと100nonce並行TestのExecutorService.close/Future.get無期限だけをstop→Futureget5s又は元10s/await10s明示assert→worker確認後codec.closeへ直す。元nonce数100/identity/mutation/null/provider復元契約を弱めない。新AUTHCTX-OWN001はpublic deterministic nonceの初回直接Error同一/nonce消去、別workerで同codec正常と独立envelope一致/元context不変/call2を検証。変更後whole8一singleexec、freshRootNullAway/静的、CRC/init/default及び無filter必須LINE/METHOD/CLASS/BRANCH整数100を対象Codecで確認する。補助Instruction/Complexityも全保存し未実行を隠さず、全物理依存scope/他Main/全例外/全命令のPASSへ拡張0。原7成功は確認再演せず当変更の必要再資格だけ行う。

BUG3021/3022・YKT2542/2546、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-422 API認証暗号化値の内部構築境界とfinally試験（2026-11-15）

AuthContextCodecのpublic4引数/既package-private5引数を維持し、新package-private6引数へ内部EnvelopeFactoryを受ける。旧5はprivate static finalのEncryptedAuthContext::newへ固定委譲し、全通常Production組立は既record構築/防御clone/同byte/同例外を維持する。外部設定・HTTP・service loader・反射でfactoryを選択しない。追加interfaceはpackage-privateのcreate(version,storedCiphertext)一操作だけ、鍵/平文/nonce/Cipher/JCAprovider/認証/権限/DBには触れない。factory引数nonnullは既鍵/version/random検査後・機密copy前にconstructorで確立する。createの戻りはnullable境界として明示し、nullなら既CRYPTO_UNAVAILABLE固定例外へ拒否する。factory呼出しは既stored及びencryptedの二finally内に置き、Error/RTEがそのまま伝播してもowned二配列とplaintext/nonceが消去されprivate lockが解放される。実OOMやprivate reflection/JCAprovider差替え/拒否試験の代替を行わない。default record生成の内容/size/暗号/version/AAD/保持/再送/publicAPI/承認済DIFを変更0。

既whole8の全本文/期待値と有限workerを保持し、新AUTHCTX-FACT001..003の3methodを同wholeTestへ追加する。001はpublic組立ciphertextを受け取った直後の直接AssertionErrorとIllegalArgumentExceptionの二caseで元throwable同一、stored全zero、次の別worker正常・独立DataOutput/JCA envelope一致・copy別identity/call2を確認する。002nullfactoryの構築前提拒否とnonce呼出0/元public key不変。003nullable factory結果nullを固定CRYPTO_UNAVAILABLE/原因抑制初期0へ拒否しstored消去後に同codecの別worker正常と独立goldenを確認する。全worker Future5/stop-await10assert後close、入力は既公開a64/keysequence/nonce2Aだけ、expectedにProduction生成を使わない。新sourceはMain5をRootNullAwayでfreshcompileし、増えたinterface含む物理数/Code数を実測、自然Code0を除外扱いしない。必要同source whole11を一singleexec、静的/CRC/init/XML/defaultと無filter必須LINE/METHOD/CLASS/BRANCH整数100を照合し、補助Instruction/Complexity/close例外未実行は全数保持し全命令/全例外をPASSにしない。旧8成功を足して11とせず旧8は新source必要再資格で新規0、新3だけ別計上する。全依存scope/正式451/CHR/native/ITST/HOLDは未受入。

BUG3023/3021・YKT2541/2542。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-423 API context hashの内部計算境界と機密消去試験（2026-11-15）

ContextHashのpublic noargs/checked NoSuchAlgorithmException/calculate(AuthenticationContext)と既private stateLockを維持する。package-private DigestOperations（digest(rawASCII)、format(hashed)の二操作）とpackage-private constructorを追加し、public constructorはprivate JdkOperationsの既SHA-256 MessageDigestとHexFormat.of().formatHexだけへ固定委譲する。外部設定/HTTP/ServiceLoader/反射/DBからOperationsを選ばず、通常production組立の認証判定・rawASCII64→SHA256→lowercase hex64・借用context・例外identity・provider選択・共有digestの排他を変更0。Operationsのnonnullを機密取得前constructorで確立、二戻りは内部nonnull契約、所有raw/hashedの各既finallyを維持し、digest/formatから直接Error/RTEが伝播しても取得済owned配列を消去しprivate lockを解放する。private stateへの反射/実OOM/独自provider/権限操作/拒否試験の迂回を行わない。

原ContextHashTest全三の有限worker/固定Python hashlib vector/100並行/null/未知/元provider unavailable復元の全本文と期待値をexact保持、新HASH-OWN001/002/003を同wholeTestへ追加する。001はdigestとformatの各段階で直接AssertionError/IllegalArgumentExceptionを一回だけ発生させ、原throwable同一、captureしたowned raw及び生成済hashed全zero、次の別workerによる同hashの固定既vector成功/call2/borrowed context不変を確認する。002はnulloperationsの構築前提拒否（機密入力なし）。003は通常委譲のrawASCII長64/byte a、32byte公開固定SHA値、独立lowerhex string/copy所有/zero/otherworker及びprivate lockのcaller-monitor非干渉を確認する。期待値をContextHash.calculateから作らず元固定二vectorとJDK明示SHA-256のactual処理だけ使用。新sourceMain/内部adapter/抽象interface実Code0をRoot25/NullAway/staticでfresh構築し、必要同source全六一singleexecの真正XML/source/CRC/initと無filter実Code必須四を照合、自然Branch0/Code0を人工100/除外にしない。元三を新規定義へ加算0、補助Instruction/Complexityや全178/451/leaf/CHR/nativeは未受入を保持する。

BUG3027・YKT2541/2550。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-424 JDBC資源nonnullと発行・監査の明示終了（2026-11-15）

AuthSessionService.issue及びSessionAuditWriter.writeの全owned PreparedStatement/ResultSetは取得直後に既RequiredColumn.requireValueを通しnonnullを確立する。provider返却nullは既22004 SQLDataExceptionとして拒否し、発行側は既9000固定AuthenticationInfrastructureExceptionへ変換する。正常SQL/順序/binding/lock/rowcount/時刻8時間/microsecond/DIF016/監査JSON/role/owner/暗号/format/public API/呼出元TX所有を変更しない。Connectionは借用でcommit/rollback/close/setAutoCommitを行わず、取得できたstatement/rowだけを一回逆順にcloseする。各nonnull資源の本体を明示try-catch(SQLException|RuntimeException|Error)-finallyで保護、catchはnullable primaryへ同一failureを保存して再throwし、finallyはAPI database内の小さいstateless JdbcResourceCleanup.close(primary,SqlClose)でcloseする。SqlCloseはthrowsSQLExceptionに限定したfunctional interface、cleanupはstatic操作だけを持つ非生成可能interfaceで余分なconstructor/instance状態を持たない。action nonnullは呼出前提。close成功はprimary graphへ変更0、primary無しclose失敗は同一SQL/RTE/Errorを伝播、primary有りclose失敗は元primary.addSuppressedで元graphを保持、同一instance self-suppressionはJDK IllegalArgumentException/causeをTWR同様に維持する。Batchの別failure precedence helperを流用せずAPI→Batch依存0、fatal分類の追加/変更も0。INSERT ciphertextはprepare/nonnull検査まで含む最外側の既finallyで必ずzeroにし、取得失敗を保護域の外へ出さない。resource nullは取得無しでrelease0、row nullでも既statementは一回closeする。外部設定/provider/driver接続/資格/権限/秘密/DDL/電文/承認済DIFを追加変更0。

原issue8/audit9の全Test本文・独立三AESgolden/固定hash/完全SQL/UTC/JSON/alias/error/所有/finite workerを保持し、Issueの既純粋Proxy FixtureへnullStatementAt/nullRowAtのdefault空値controlだけを追加する。新AUT-ISS-RESOURCE001/002はstatement五箇所(USER/INSERT/ACTIVE/REPLACE/AUDIT)とrow二箇所(USER/ACTIVE)のnull返却を独立に与え、9000固定/cause-suppression初期0/owned row-statement一回close/借用TX変更0/entropy-nonce-ciphertext全zeroを確認する。新JdbcResourceCleanupTest全五はaction null前提、通常closeの呼出一回/primary不変、primary無しSQL-RTE-Error同一、primary有り各closefailureの正確なsuppressed identity、selfaliasの元IllegalArgumentException causeを固定graph期待で検証。期待をproduction cleanup/hash/codecで作らず元literalと独立公開objects/countersだけを使う。新七だけ新定義、旧十七は新Main必要再資格で新規加算0、全二十四を当source一singleexecにしてfreshRootNullAway/static/Code物理実測/CRC-init/XML/default+raw必須四を照合する。新interface/SqlClose/package Code0は自然値、未実行をcompiler除外/到達不能/旧exec合算へしない。実DB/生session/Root/cohort/VM/native/aru/actual4/Root2/SDKbackend/HOLDは未受入を維持する。

BUG3033・YKT2553/2546。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-425 JDBC型付き終了所有契約（2026-11-15）

SSC424のcallback越しclose所有がSpotBugs OBL一件として未確定となったため、JdbcResourceCleanupへStatement専用closeStatement(primary,statement)とResultSet専用closeRows(primary,rows)を追加する。両者はnonnullを明示検査し、直接resource.closeを一回呼び、SQL/RTE/Error失敗はprimary無しで同一throw、有りで元primary.addSuppressed、自分自身の場合も元JDK IllegalArgumentException/causeを維持する。既close(primary,SqlClose)及び原五testは保持する。親Issue/Auditは型付きadapterへ変更するだけで、SQL/binding/8h/DIF016/暗号/borrowed Connection/TX/INSERT最外側消去/既例外graphを変更しない。実漏れは未確認で、抑制/除外による静的合格にはしない。既取得SDK com.google.code.findbugs:jsr305:3.0.2 の実在javax.annotation.WillClose（RUNTIME retention、通常parameter所有契約）をAPI provided依存として宣言し、各typed parameterへ付与する。注釈はclose責任の宣言でありSuppressFBWarnings等の抑制ではない。SDK変更/ダウンロード/実DB/driver/権限/外部経路追加0。原SpotBugsannotations4.10.4に同annotationがあるとのBUG3034初記述は誤認であり、実SDKメタデータの照合で訂正する。新二testは両adapterごとにnull前提/正常/SQL-RTE-Error/primary/alias/一回closeをJDK純粋Proxyと独立identityで検証し、新合計九＋既十七の必要全二十六をfresh同source compile/NullAway/static/CRC/XML/必須四rawで測定する。原二十四未実行をPASSへ加算0、旧compile/static一件は歴史証拠として保持する。

関連BUG3033/3034・YKT2553・SSC424。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-426 API取消JDBC資源nonnullと明示終了（2026-11-15）

AuthSessionRevocationServiceのlogoutCurrent/revokeAll/updateにおけるowned statement五取得/row四取得を取得直後RequiredColumn.requireValueでnonnullに確立し、既SSC425 JdbcResourceCleanup.closeStatement/closeRowsと明示primary(SQL/RTE/Error同一再throw)-finallyで一回終了する。SQL文字列/binding/order、User/session lock後clock採取/microsecond、期限境界、既取消済idempotent/監査理由/ADMIN認可/N12/allowed-reason/rowcount/例外分類/元graph/selfalias/borrowed Connection/TX所有を変更しない。悪いnull providerは既22004に統一、resource無しをcloseしない。Audit/Hash/helperは既同byte、実DB/driver/Root/サービス/VM/鍵/権限/HOLD変更0。原SessionRevocationJdbcPortTest8の完全SQL/固定SHA/JSON/UTC/lock後時刻/全null/role/owner/理由/再送/rowcount/cleanup/並行期待を保持し、無期限pool closeだけshutdownNow→await10assert/classTimeout30に是正する。既fixtureへnullStatementAt/nullRowAtのdefault空controlを追加、新二件はLogout U/S/X/LとADMIN T/A/X/L statement及びU/S/T/A rowのnullを独立入力して固定9000/owned一回/borrowedTX0/後続処理非発行を検証。原八＋新二全十をfresh閉じたMain/RootNullAway/static/CRC-init/XML/実Code必須四で測る。旧DBfixture/旧012全APIjarを流用しない。

BUG3035/3036、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-427 認証検証のnonnull終了とprivate carrier（2026-11-15）

AuthenticationContextVerifier.verify/readSessionの三owned statement/二row取得へ既RequiredColumn.requireValueを置きnonnull・22004を確立し、既typed JdbcResourceCleanupとprimary SQL/RTE/Error同一再throw/finally一回終了を使う。verify/inspectReadOnlyの公開signature、SQL literal/順序/User→session lock/currentActor/role/期限/readonly非lock非touch/UTC/8h greatest touch/rowcount/固定失敗分類/borrowedTX/秘密/電文は不変。private VerifiedSessionは二fieldを当class内のreadSession→verify/inspectだけへ運ぶ非公開carrierであり、参照するのはid()/actor()だけ。recordの値同一性・自動表示・hashを業務契約として使わないため、private static final classへ整理しfinal UUID sessionId/final AuthenticatedActor authenticatedActor、constructorでObjects.requireNonNull二つ、同名二accessorだけを持たせる。外部型/serialization/wire/public値契約の変更0、不要なprivate値操作やテスト専用口を追加せず、全残Codeを通常公開業務経路で意味ある期待により検証できる形にする。測定から既Codeを除外/到達不能認定せず、旧record形状は歴史として保持し新形状を独立測る。原AuthenticationVerifierJdbcPortTest6のSQL/hash/currentDB actor/readOnly/拒否/nullcolumn/rowcount/cleanup/未知RTE/並行全期待を保持、workerのみshutdownNow/await10assert/Timeout30へ有限化する。既FixtureのnullStatementAt/nullRowAt default空controlとacquired記録を追加、Mapのnullable要素とruntimeFailure nullableをJSpecifyで明記する。新資源null二はverify User/Session/Touch及びinspect READ statement、verify User/Session及びinspect Session rowのnullで固定9000/取得済一回close/borrowedTX0/最後SQL一致を独立検証。原六＋新二の全八、Main閉包11（SDKjsr305だけ追加で既取得/全Protocolは同byte）/freshRootNullAway/static/全物理CRC/XML/default及びraw必須四を照合。実DB/driver/旧全APIjar/Root2/Actual4/VM/native/aru/HOLD操作0。

BUG3039/3040、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

2026-11-15 SSC427継続補足（BUG3041）: private field名のみsessionId/authenticatedActor、既id()/actor()/nonnull invariant/SQL/public結果は不変、新fixture user labelは新側constant化・元6期待除去inverse保持。初回static32/未実行8を保存しfresh必要資格へ。

## SSC-428 ADMIN前処理資源nonnullと明示終了（2026-11-15）

AdminCommandAuthenticator.verifyIdentity/owner/lockUsersの三owned statement/三row取得へ既RequiredColumn.requireValueを置きnonnull・22004を確立し、既typed JdbcResourceCleanupとSQL/RTE/Error primary同一再throw/finallyで一回逆順終了する。advisoryの二資源TWR headerは同じ取得順/逆順終了のnested単一資源へ正規化してから明示終了にする。SQL全文/7mutation集合/target presence-N12/候補owner単一行と範囲/減少系だけadvisory一行/候補target現ACTIVE ADMINの昇順lock/locked owner再照合/最新Verifier/currentADMIN/Inbox前段/rowcount/UTC8h/既失敗分類/primary-suppression-selfalias/borrowedTX所有を変更しない。実advisory lockや利用者更新は発行せず、元091 PT_DEFAULTの既hardcoded JDBC-interface fixtureだけを使う。原AdminPreludeJdbcPortTest8の完全SQL/固定hash/UTC/Mapbindings/全7Mutation lock有無順序/cardinality/owner非権限/拒否/rowcount/資源/並行全期待を保持し、poolだけfinally shutdownNow/await10assert/Timeout30へ有限化する。fixture runtimeFailureのnullable契約とdefault空nullStatementAt/nullRowAtを明記、新null二はstatement全7label(candidate/advisory/users/locked/auth-user/auth-session/touch)及び非touch row全6labelを固定DISABLE入力で試し、固定9000/cause-supp0/最後label/owned一回/borrowedTX0を検証する。下位Verifierは同byte既qualified12を依存としてfresh Root閉包へ含めるが成功件数へ加算しない。新Mutation閉集合一は固定CREATE/ENABLE/DISABLE/PROMOTE/DEMOTE/RESET_PASSWORD/UNLOCK順序とidentity/valueOf/防御values/unknown-empty-case-space-null、membership減少はDISABLE/DEMOTEだけと明示期待で検証する。元八＋新三全十一、Main14/全195physical/RootNullAway/static/CRC-init/XML/default及びraw対象Admin本体とMutation全Codeを照合する。旧012全APIjar/realDBfixture/Root/VM/native/SDKbackend/aru/四held/HOLDへ拡張しない。

BUG3044/3045、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-429 Login JDBC資源nonnullと有限worker寿命（2026-11-16）

LoginAttemptRepositoryの五statement二row、LoginAuditWriterの一statement取得へ既RequiredColumn.requireValueを置きnullをSQLSTATE22004とし、既JdbcResourceCleanup.closeStatement/closeRowsとnullable primary、SQLException/RuntimeException/Error同一再throw/finallyでTWRと同じ一回逆順終了を保持する。SQL文字列/取得lock User→IP/username NFCと長さ/role-status/count/USER5-IP10/15分/window境界/成功失敗更新/rowcount/UTC/borrowed connection所有/監査列-action-details値/秘密非保存/固定9000-fatal-preserveを変更しない。AuthenticationService本体に仕様変更を加えず、その通常全体を既API Memory16で検証する。既in-memory JDK Connection/Statement/ResultSet proxyと自身の未発行zero-key AuthContextCodecだけを使い、実DB/driver/サーバLogin/VM/Root/Actual4/HOLDへ拡張しない。元16全入力・独立固定期待をinverse exact保持し、Memory016はpool明示stop/await10assert後だけ二fixture close、await失敗時codecを稼働workerへ残し成功扱いしない。classTimeout30。新null二はUSER/CREATE_IP/IP/UPDATE_USER/UPDATE_IP/LOGIN_AUDITの六statement、USER/IP二rowの固定9000/cause-supp0/最後取得位置/取得済owned close一回/未取得資源無し/秘密配列消去/borrowedTX0を検証する。元16＋新2全18、freshMain閉包/RootNullAway/静的指摘適用性全件/物理CRC-init/XML/raw四counterを三target AuthenticationService/LoginAttemptRepository/LoginAuditWriterについて確認し、未達を明示する。旧全APIjar/原realDBfixtureのcopyや抽出は行わない。

BUG3047/3048、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-430 Web form分類のfatal保全と有限単体試験（2026-11-16）

LoginFormAuthenticationConverter.convertの既catch(IllegalArgumentException|IllegalStateException|NoSuchElementException)では、固定LoginFormRejectedExceptionへ変換する前に既SessionStoreException.preserveFatal(failure)を呼ぶ。元Error/cause/suppressed/SQLnextをidentity seenで有限走査する既helperを再実装せず、Error無しの例外は原因/診断を保持しない同じ固定input rejectionを返す。通常POST/login/UTF8/contenttype/charset/query予約名/parameters多重-null/数値proxy信頼/非認証token/char[]受渡し/CSRF前提/公開API/400入力拒否と403proxy拒否/ログ秘匿/上位503分類/承認DIFを変更しない。外部設定/provider/資格/権限/実認証/DB/MQ/鍵/Root2Actual4/VM/native/aru/HOLDを追加しない。元LoginFormConverterPortTest全13の全入力/独立HTTP・token・配列消去期待はinverse exact保持、八task/二worker/既Futureget10を保ちfinally shutdownNow/await10assert/classTimeout30へ有限化する。新FORM014は三分類例外それぞれcause/suppressed内の公開合成AssertionErrorをgetMethod/getParameterValuesから与え元Error同一/固定正常結果0を検証、新FORM015はError無しcause循環/共有suppressedの固定秘匿分類と未分類RTE同一を確認する。既JDK Servlet-interface proxyだけを使いMockserver/actualcontext/key/native/JDBCを起動0。safe MainはConverter/CaddyResolver/LoginClientAddress/FormRejected/CaddyRejected/SessionStoreException/InvalidSessionRowExceptionの七source、SDKは既qualifiedServlet6.1/Spring7標準libの明示hashだけ、旧全Web/APIjarを読取・hash・抽出・定義しない。原13＋新2全15、一source/runのfreshRootNullAway/静的全site/物理CRC-init/XML/default及び無filterConverter必須四整数100、依存七全体の未達を隠さない。

BUG3063/3064、YKT2546/2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-431 Login現在context probeのfatal保全（2026-11-16）

MqLoginContextProbe.isActiveの既七catch(JMSException/JMSRuntimeException/JmsRequestReplyException/PermanentProtocolException/IllegalArgumentException/IllegalStateException/DateTimeException)は固定UNAVAILABLEへ変換する前に既JmsRequestReplyException.preserveFatal(failure)を呼び、cause/suppressed/SQLnext/JMSlinkedの元Error identityを有限に保存する。header/IF003現在context再確認/UUID freshness/256byte request/全reply検査/0102 false/他非success固定例外/timeout1ns..2s/12wait/再Login禁止/所有request-sendercopy-reply-data-records全消去/正常認証ロール/公開API/秘密非保持を変えない。Provider本体は変更しない。catch唯一のfinal MqLoginExchangeExceptionはsuper(message,null,false,true)によりcause/suppressedを保持できず今回のmissing-guard条件に非該当、固定reason INVALID_INPUT/UNAVAILABLEと例外秘匿を独立回帰契約にする。新PROBEGRAPH001は各七catch族の公開合成Error graph（JMSlinked→SQLcause含む）を既memory senderから与え元Error/256ownedcopy全zero/pending0と同one-slot clientで別freshID正常復帰を検証する。新LOGINFAILVALUE001は二reasonの固定message/nullcause/disabledsuppression/initCause拒否/null constructor/enum閉集合lookup/values防御を独立literalで確認する。元MqLoginClientTest8/ProbeTest3/ProviderTest5の全16本文・独立wire・100並行/get10/stop-await5及び既固有例外/消去期待は保持、compile依存するfixture helperは抽出せず元whole class全実行する。新2＋旧16全18を一source/run、既明示safeWeb18sourceと現在Protocol176だけfreshRootNullAway/static/物理CRC-init/XML/default/raw対象Probe/Provider/ExchangeException全sourceで照合する。旧162/166/Protocol130は確認再演0、実JMS broker/socket/DB/auth session/鍵/Root2Actual4/VM/native/aru/HOLDや旧全WebAPIjar読取抽出を行わない。

BUG3065/YKT2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-432 認証Providerの資格消費契約を一箇所へ集約（2026-11-16）

MqAuthenticationProvider.authenticateの既finally二guard（captured credentialsがchar[]ならzero、その後authenticationがUsernamePasswordAuthenticationTokenならeraseCredentials）を、同じclassの一つのprivate static consumeCredentials(Authentication,@Nullable Object)へ同順・同条件で集約する。finallyはこのhelperを一回呼ぶだけとし、正常/拒否/例外で資格消費の実装を一箇所へ統一する。authenticationの既nonnull前提/getCredentials一回をtry前に採る順序、nullable credentialsを含む不正型/unsupported subclassの拒否、公開API/認証成功条件/closedprincipal/Role/Probe/再送/014/0101/0106/9000分類/char配列zero後tokeneraseの順序・回数/cleanup例外の既優先を変えない。helperを公開・port・外部設定化せず、private reflection/SDK型偽装/到達不能扱い/除外/閾値緩和で分岐を隠さない。PG34545の通常return/例外の二重生成cleanupに対し、既通常API試験が持つ成功・不正token型・null/非char資格・派生型・transport失敗の実入力で単一helperの両guardを検証する。元Client8/Probe4/Provider5/closedfailure1全18の全source/期待/fixtureはbyte exact保持、新Test定義0。fresh safeMain18/RootNullAway/静的/現在SDK-JDK/protocol/物理CRC-init/XML/default及び無filter対象Probe/Provider/ExchangeException全Codeの必須四100を同一source/runで確認、旧18成功/defaultを新sourceへ転用0。外部権限/認証経路/実JMS-DB-session-key/Root2Actual4/VM/native/aru/HOLDを変更0。

BUG3067/YKT2431/2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-433 Web failure分類のfatal保全と有限単体試験（2026-11-16）

MqLoginFailureHandler.onAuthenticationFailureは既request/response/failure非null及びWebRequestContext.requireの順を保持し、その直後・HTTP分類と監査前に既JmsRequestReplyException.preserveFatal(failure)を呼ぶ。Error/cause/suppressed/SQLnext/JMSlinkedは既identity graphで有限走査、元Error同一を伝播しresponse/auditへ副作用を出さない。Error無しの通常五分類、302/400/403/503、Retry-After/Location、監査回数と呼出順、秘匿、公開API、QA055固定文を変更しない。例外診断をログ又は保存せず一時走査するだけ、DB/実JMS/実HTTP/Root2Actual4/VM/鍵/aru/native/HOLDへアクセス0。元MqLoginFailurePortTest6は全期待をinverse exact保持、16task二worker/get10維持でfinallyshutdownNow/await10assert/Timeout30を追加。新FAIL007は五AuthenticationException families×cause/suppressed/JMSlinked-SQL graph三の15条件でError同一/HTTP0/headers空/audit0/context読取一回を検証。新FAIL008は五familiesの非fatalcause循環/共有suppressedを有限分類し独立status302302400403503/audit11010/headers固定表で検証。safeMainはHandler/Locked/FormRejected/CaddyRejected/Context/Address/SessionStoreException/InvalidSessionRow/SessionPrincipal/WebSecurityAudit/JmsRequestReplyExceptionの11、SDKは既許可Servlet/Spring/JMSAPI/Gson/annotationsの明示hash。旧全WebAPIjar読取hash抽出定義0。原6＋新2全8、一source/runのfreshRootNullAway/静的全site/物理CRC-init/XML/default/rawHandler必須四整数100、依存全体の不足を隠さない。

BUG3068/3069、YKT2546/2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-434 Revocation AAD所有fieldの消去を一箇所へ集約（2026-11-16）

RevocationPayloadIdentity.aadで作成したowned六field byte配列の既finally消去loop（元順Arrays.fill(field,0)）を同classのprivate static eraseFields(byte[][])へ同bodyで一箇所集約し、finallyはこのhelperを一回呼ぶ。六field内容/32bitBE長/UUID全bit/epoch秒signed64+nanos32bit/返却配列/取得前検証/消去順・回数・例外優先/公開API/QA050再送間隔/暗号仕様を変更しない。PG34695で通常return/例外finallyの同一消去loop二重生成を確認、正常aad公開package口からhelper全条件を検証する。正常・異常を架空に増やさず、実OOM/ThreadDeath/非公開反射/SDK代替/到達不能/coverage除外で穴を隠さない。原RevocationValueContractTest4とExceptionValueContractTest1の全source/独立113byteAAD期待/境界/null/clone/value/列挙期待はbyte exact保持、新Test定義0。freshMain5RootNullAway/静的/currentProtocol176/物理182CRC-init/XML、一source/runの必要whole5とraw対象六classのLINE/METHOD/CLASS/BRANCH100を確認し、補足INSTRUCTION/COMPLEXITY不足はそのまま明記する。旧5成功/default/rawを新sourceへ流用又はexec合算0。Claimed/PendingRepository/Root2Actual4/実鍵-DB-JMS-取消再送/VM/native/aru/HOLDは操作せず、helperを公開・外部設定・新portへしない。

BUG3074/YKT2431、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-435 Revocation AAD所有fieldの取得を終了保護領域内へ移す（2026-11-16）

RevocationPayloadIdentity.aadのowned六field取得をcleanup領域内へ移す。try前では要素が全てnew byte[0]である六slot配列の形だけを確立し、元literalの六expr（purpose/table/UUID/time/format/version）を元順でtry内のfields[0]..[5]へ代入、その後の長計算/ByteBuffer/返却値はそのまま保持する。既finallyのprivateeraseFields(fields)一回で、version.getBytes(null)等の部分取得中断も取得済み全slotを元順zeroする。空slotをnullにせずconstructor/factory内部invariantとNullAwayで担保、未取得slotのemptyzeroは無害。元null版の例外型/NPE診断・正常113byteAAD・元expr順/UUID秒nanosBE/版byte/返却配列/公開API/QA050再送/暗号仕様を変更しない。SSC434時点は原全5成功だがrawLINE1未完、PG34724の5I/1LINE未達とBUG3074/3075を保持して品質完了へ算入0。元二Testclass/全5本文と独立AAD/境界/null/clone/列挙期待はbyte exact、新定義0。新source必要whole5/freshMain5RootNullAway/全静的/182physicalCRC-init/XML/raw六classの必須四100を検証、補足I/complexityも値を明記。実OOM/ThreadDeath/偽例外port/私有反射/除外/到達不能/旧exec合算で穴を隠さない。実鍵/DB/JMS/再送/Root2Actual4/Claimed-Pending/VM/native/aru/HOLDを追加しない。

BUG3074/3075/YKT2431、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-436 閉認証投影の非instance責務とstatic namespace（2026-11-16）

ClosedWebAuthenticationは認証主体を保持しないpackage-privateの閉じたstatic factory/projection責務をstatic-only package-private interfaceで表す。元final classの宣言とprivate空constructorだけを置き換え、authenticated/principalの二static method名・descriptor・注釈・全body・null/匿名空Optional・token exacttype/認証済/credentials-null/details-null/authority一件/role一致の全判定と固定SessionStoreExceptionをbyte逆展開保持する。interfaceはinstance API/abstract method/fields/新port/設定/権限経路を持たず、型自体はpackage-privateのまま。Java interface static methodのpublic modifierは型のpackage可視性の内側だけ、外部Web/認証/セッション/HTTP/UI/RD/DIFを変更0。private反射・意味のないinstance生成・coverage除外・到達不能宣言で空ctorを埋めない。型kind変更により旧class Methodrefを含むbinaryは混用不可、全module/八source呼出元をfresh再compileしたreleaseだけが将来配備対象。八callersのpath/hash/ownerとstatic呼出構文を記録する。今回の許可済みsafeMain19は元Login18＋TopBar1、callerはProviderのみ実接続、元Client8/Probe4/Provider5/閉例外1/ClosedValue4/PrincipalTopBar2の全六Testclass24をbyte exact保持して新sourceで一回再資格。元二method/PrincipalTopBar/ProbeProvider/閉例外とReasonの七targetを同一source/runのfreshRootNullAway/全静的/current198physicalCRC-init/XML/raw必須四100で確認、他依存missは保持。残七callerや正式Webassembly/全回帰はHOLD依存があるため未実行のまま、本文source互換だけで成功へ変換しない。実Root2Actual4/鍵DB-JMS-認証service/session/VM/native/aru/HOLDをcompile/代替/操作0、旧source全体/exec成功移植0。

BUG3078/YKT2431、状態:設計確定・main反映前、PG/PT/全caller/正式未完。


## SSC-449 PostgreSQL JDBC注釈の正規compile依存（2026-11-17）

BUG3129/YKT2600、RD/UI変更なし。pgjdbc42.7.13の公式POMはchecker-qual3.55.1をruntime依存にしているが、PostgresMigrationCopyPort及びQuestionSubmissionServiceのPGConnection/CopyManager等をjavac -Xlint:all -Werrorで型検査するとorg.postgresql package-infoのDefaultQualifier/TypeUseLocationがcompile classpathへ無く10警告→終了1になる。PG36830元Maven/36834診断/36836元flagsの直接javacで同じ失敗を保全。これは製品業務処理や原本/権限の失敗ではなく、SDK注釈の依存scope不足。

Bootstrap POMへorg.checkerframework:checker-qual:3.55.1を明示compile依存として追加する。版は既pgjdbc POMのruntime版と完全一致、既toolchain cacheから使用し新規version選定/更新をしない。Bootstrapをcompile依存とするAPI/Web/Batchへも型情報を正規推移し、既runtimeに存在する同一artifactを別版へ置換/増幅しない。Root flags、NullAway/JSpecify/Werror、PMD/CS/SB、既業務Main/Test/SQL/電文/既goldenは不変。注釈classをstub/削除したり-Xlint:-classfile/-nowarn/-Werror解除で回避しない。実SDKの注釈解決だけであり、秘密・鍵・許可・署名・native/DBの実操作を追加しない。

独立資格: 原失敗のwarnings10/exit1と新compileのwarnings0/exit0を同じRoot flags/版/業務Main byte/sourceで対照し、実効compile classpathへ3.55.1の同JARが入ること、六module依存境界/収束を照合する。生成Mainは旧sourceの公開APIと必要byteを比較し、失敗元の未生成classは旧成功と同一扱いしない。四module全477Mainの通常compile・該当静的を先行し、API/WebのQA056該当classfile操作は回答まで保留、全六/F02/F03/451を宣言しない。PTを暗黙に起動せず、実PT/coverage/CHRと分離する。同source通常PTが必要な変更なら対象triggerと独立oracleを先に確定する。

状態:設計確定・main反映前・POM未変更・是正後compile/静的未実施。関連元F02/F03・P01808/00403/00405終了依存。元F03/2-2残2.4ppとcap5は据置き、診断/手戻りを原成果とは分離記録し、追加予算消化/工数率へ変換しない。BUG3129/YKT2600は再試験と全横展開判定までOPEN。


## SSC-450 閉SQLの実行位置をliteral操作として保持（2026-11-17）

BUG3132/YKT2603、上位RD/UI変更なし、canonical主担当/費用WBS-P019-03、F03受領。AssetStagingTables、MigrationMasterColumnVerifier、MigrationMasterConstraintVerifier、MigrationMasterContentVerifier、MigrationMasterFinalizer、MigrationMasterReferenceVerifierのprivate閉SQL表現を補足する。全SQL文字列・固定表/列/順序・実行順・timeout/fetch/setval bind・借用transaction・null/一次例外/cleanup規則・public APIは変更しない。

private stateless関数型の実装をclass初期化時に固定Listへ登録し、各executeQuery/executeUpdate/executeLargeUpdate/prepareStatement呼出位置の引数をcompile-time constantのSQL式にする。callbackはStatement/Connectionを保持せず呼出引数として借用し、一SQLごとのcallback割当や可変registry/外部SQL選択口を作らない。Assetのprivate Tableはname/columns/order文字列からprepare/targetCount/stagedCount/insertの四操作を持つ閉じた計画へ変更する。Column/Constraint各六query、Content七query、Reference六count及び全inspectionは同順の固定query操作、Finalizerは五MAX/五setval prepare/六ANALYZEの固定操作へ変更する。setvalの五事前MAX検査→全setval→全ANALYZE・constraint phase、known zero/nonnull/wasNull/row数とmetadata期待を維持する。NoCode private interfaceも物理集合に含め、除外/架空到達/SQL難読化/新suppression/flag緩和をしない。

旧承認SQL全byteと順序を一対一で照合するSource equivalenceは補助証拠とする。PT期待はproductionを呼んで生成せず、既独立Testのliteral SQL/metadata/rows/固定hash/JDBC後条件と承認SS/DDLから保持する。元Asset32・Column26・Constraint22・Content29・Finalizer30・Reference21のwhole160 Test本文/独立期待値を不変とし、必要なwhole helperをscope確定してから新sourceで一exec、Root NullAway/Werror/全静的/物理CRC-init/XML/当六sourceの未filter四counter/公開API及び不変byteを確認する。private関数型の真のNoCodeを隠さず、共通DTO等の残coverageも全componentに残す。実DB/master/原本/鍵/Backup/Root/VM/native/QA056四型/QA051 finalの保留は解除しない。

既instanceのtoString/redactionと例外診断を維持する。literal化は所有開始後のString組立を除去するが、性能やheap OOME挙動の実測合格を主張しない。追加A .4/1.2/3.6pp cap4を一回だけ計上、元F03 C2.4/SV/原見積りを保持する。元P01903/全F03/正式/ITSTの受入は別。状態:設計確定・main反映前・製造/PT未実施。
