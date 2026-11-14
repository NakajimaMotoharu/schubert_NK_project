# MediaAsset十七列・独立20仕様

NK-MIG-001/MIG-DAT-003/MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI254、SS311/331/34310.1.4 SSC357、WBS-P01903.02。

SS34310.1.4・SS331/V002＋V029（SSC340）・UI242§5/SS333§5のmedia_assets十七列の宣言COPY値をbootstrap.migration.MediaAssetCopyRowへ具体化。RD MIG-DAT-003/MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI223/242/243/254。最新V029のTRUE確定済みpair制約を正とし、旧V002 nullable CHECKを再修正/再起票しない。V001～029 byte/checksum・role/grant・table/indexを変更しない。

列順id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at。id/sizeはcanonical正N12、logicalID1..64byte、media_type VIDEO/MUSIC、title1..256/category1..64、section nullable0..128、storage/display1..512、file_name1..256、sha lowerhex64、display_order canonical1..9999、UTC canonical0001..9999/µs。全textはNFC/正UTF8/control無し、storageは相対POSIX/空・dot・dotdot/先頭末尾slash/backslash拒否。parent nullable、非null1..64byte。宣言値をtrim/補完/再採番しない。

VIDEOはpair_key/pair_role双方nullのみ。MUSICはrole NNでM/I/N。M/Iはkey NNで1..256 UTF8byte・NFC/control無し、Nはkey null。MUSIC logical_idは既MusicLogicalId.fromDisplayPathの固定prefix/NFC/SHA256と全値一致を要求する。NoSuchAlgorithmExceptionは上位へ伝播、provider設定/fallback変更0。VIDEO固定20catalogue/parent実在/category/pair結果/全表示順/一意性/Current ID対応・collisionは別dataset/ETL条件で、この単行では代用しない。

SS333のtype/拡張子/MIME対応を同じ宣言値で確認: VIDEO .mp4/video/mp4、MUSIC .m4a/audio/mp4 .mp3/audio/mpeg .ogg/audio/ogg .wav/audio/wav .flac/audio/flac。case/別名を推測しない。実file/hash/containerの再認証やdescriptor実配信は別未完。nullable List/要素を明示契約とし、null入力/列数/必須null/不正値は固定IAE、private深いList snapshot/変更不能getter、copyBytesはnonnull既encoderへ委譲し毎回byte別所有、toString固定redacted。

PT-MIG-MEDIAROW001..020: VIDEO十七列全手書きgolden、MUSIC安定IDと全golden、id/size/order各上下とgrammar、logical/parent byte境界とMusic ID不一致、type/role閉集合、title/category/name byte境界、nullable section byte0/128/129、storage/display512と危険path、全六MIME/拡張子の対応とunknown/欠落/大文字/別名、VIDEO/MUSIC全pair/null/長さ組合せ、sha grammar、時刻canonical年/µs境界、全text Unicode/NFC/control、null入力/列数/必須要素/encoder、immutable入力/返却byte所有、日本語Music ID独立固定vector、pair key UTF8byte境界、SQL風literalの独立COPY escape、finite8worker64task/Future5/finallyshutdownNow-await10、fixedredaction/拒否後独立正常。期待hashはPython hashlibで先に固定、expectedをproductionで計算0。

新20＋必要MusicID12＋codec12=whole44、全3Main/3physicalを同source/単一exec・Root通常静的/NullAway/lintWerror・独立CRC-init/XML/四100/実Code一致で確認。旧成功の確認再演/別source合算0。追加不足1.65/4.95/9.9未較正を詳細+PG20 1.05/3.15/6.3cap7と必要normal44 .6/1.8/3.6cap4へ分離。元費用/SV上限保持、専有費/実token null。小metadataのみ、実素材/DB/V029適用/全migration/Rootnative/CHR/global451/ITST/HOLD解除0。
