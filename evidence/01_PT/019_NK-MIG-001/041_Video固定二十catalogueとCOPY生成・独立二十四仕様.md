# Video固定20catalogueとCOPY生成・独立24仕様

NK-MIG-001/MIG-DAT-003/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI254、SS311/331/34310.1.4 SSC358、WBS-P01903.02。

UI223§6の固定動画20件とSS34310.1.3/4をbootstrap.migration.VideoMigrationCatalogueへ具体化する。RD MIG-DAT-003/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004/FIL-003/FIL-005、UI223/242/243/254、SS311/331/333/343。main/SUBTRACK15（Main11＋Sub4）、OVA4、opening1のlogical ID/title/category/Current相対display path/parent/表示順1..20を承認表どおり固定、静的closedデータ以外を登録する公開APIを作らない。全Main/SQLに既承認20catalogueが存在しないことをsource監査済み。実asset/root/実hash/Currentinventory/全migration/DB/HOLDは別未完。

public videos()は固定順immutable List<Video>を返す。public nested final Videoはprivate固定table専用constructorとfinal保持field、logicalId/title/category/sourceRelativePath/Optional parentLogicalId/displayOrder getter・固定redacted toStringを持つ。literal tableのinvariantは全20独立goldenで検証し、外部入力を取らないprivate constructorへ到達不能な追加validation branchを作らない。find(Nullable String)はnullを固定IAE、未知/空/大文字差/空白付与はOptional.empty、完全一致20件だけ同じimmutable値を返す。pathを解決/読取しない。

copyRows(targetIds,declaredAssets,createdAt)はUI表20件すべてに対するtarget IDと、VIDEO20件だけのAssetMigrationManifestを借用しsnapshotする。null引数/Map count≠20/各既知keyの値null・正N12外・target重複は固定catalogue IAE。size20と全20既知keyのnonnullにより未知/欠落keyも拒否し、同じ意味の到達不能な重複keyset branchを追加しない。manifest件数≠20/VIDEO以外/各固定Current pathの欠落（同件数の未知path含む）は固定IAE、fuzzy/case変換/補完/再試行0。宣言済みEntryのkind/path/metadata不変契約を再利用し、実fileを観測済みとはしない。

固定順で新MediaAssetCopyRowの十七列を生成する。idは入力mapの正N12、logical/title/category/display path/parent/orderはUI表、section/pair key/pair roleはnull、media_type VIDEO/mime video/mp4、storageはEntry.targetPath、file_nameはCurrent sourceRelativePathの最後の名、size/shaはEntry宣言値、created_atは共通引数。MediaRowの現行型/NFC/path/拡張子/size/sha/time契約を再検査し、その固定IAEを伝播。target ID大小/manifest入力順/Map入力順で表示順を変更しない。List/Rowはimmutable、Map/manifest所有やDB/transaction/公開を取得しない。共有Rowのchecked NoSuchAlgorithmExceptionは宣言のまま上位へ伝播、VIDEOで不要なprovider操作/fallbackを追加しない。

PT-MIG-VIDEO001..024: 固定全20metadata独立golden、全20lookup、両端lookup、unknown/case/空白/空/null、件数/category15-4-1、四parent全対応、表示順1..20、immutable/再取得/二classredaction、全20十七列COPY独立golden、manifest/Map再順序とID非単調、target欠落/余剰/未知/nullkey/nullvalue/非正/MAXN12/超過/重複、manifest欠落/余剰/同件数未知/case差/三wrong kind、Entry size0/正N12超過/正常MAX、created_at null/不正/共通µs、返却Rows/byte所有、宣言metadata異常後の正常入力不変、finite8worker64task/Future5/finallyshutdownNow-await10。実Masterを使わず全fileをsynthetic abc/既知SHA/宣言3byteで表す。期待metadata TSVはUI223の表を別Python parserで採取、COPY goldenは独立したfixture宣言/DDL field順から生成しProduction getter/factoryでexpectedを作らない。

新Catalogue24＋必要AssetManifest12＋MediaRow20＋MusicID12＋codec12=whole80、全5Main/10physicalを同source/一exec/Root通常静的/NullAway/lintWerror/独立CRC-init/XML/四100/実Code差で照合。新nested Videoは手書きgetterで新生成filterなし、旧Manifest record/enumの既定生成差は別/global451未承認として保持する。新定義24だけ、旧成功再演/別source合算0。追加不足1.9/5.7/11.4未較正を詳細+PG24 1.2/3.6/7.2cap8と必要normal80 .7/2.1/4.2cap5へ分離。元費用/SV上限保持・専有費/実token null。実20file/素材hash/DB/ETL/Rootnative/CHR/全451/ITST/HOLDは未受入。
