# 音声COPY行・独立16仕様

NK-MIG-001/MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI254、SS311/331/34310.1.4 SSC354、WBS-P01903.02。

SS34310.1.4・SS331/V002・UI242のaudio_files十二列の宣言COPY行をbootstrap.migration.AudioFileCopyRowに具体化する。RD MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI227/242/254、WBS-P01903.02。実Current抽出/素材採取/全件数/対応ID/link/game/FK・DB/COPY SDK/全migrationは別でHOLD解除しない。非秘密synthetic metadataだけを受ける純値であり、実素材やDB/鍵/Root/FS/permitを操作しない。

列順はid,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at。id/byte_sizeはcanonical正N12 1..999999999999、game1/2、duration nullable canonical0..999999999999。必須textはNFC/正UTF8/ISO control無しでstorage/display1..512byte、file_name1..256、basename1..255、audio_role1..8byte。audio_roleにDDL未指定のenumを追加しない。storageは相対POSIXで先頭/末尾slash/backslash/空segment/dot/dotdotを拒否する。containerはnullable、空保持、varchar16 Unicode codepoint以内（byte上限へ変更しない）、他text同様NFC/正UTF8/control無し。sha256はlowerhex64、時刻はUTC canonical Instant.toString・0001..9999/µs精度・全共通transaction時刻の合意は上位batch責務。値をtrim/正規化/再採番/欠落補完しない。

constructorはNullable List/nullable要素を受け、null入力/12列以外/必須null/不正値を固定IAEで拒否。private deep list snapshotと変更不能返却、columnNames固定immutable。copyBytesはnonnull既PostgresCopyTextEncoder.encodeRowへ委譲し毎回byte別所有、nullencoder固定IAE。診断/toStringにpath/本文/生値を入れない。既codec/Scenario各Main/Testの全byte・外部値を変えない。

PT-MIG-AUDIOROW001..016: 001手書き十二列全golden、002二nullable/空container/zero duration、003id/game正N12の境界とgrammar、004storageのUTF8byte境界/危険path、005各必須text byte上下、006container Unicode codepoint0/16/17とUTF8多byte、007duration0/MAX/grammar/overflow、008size1/MAX/zero/grammar、009sha lower64の異常、010canonical時刻年/µs/offset/不正形式、011全textのNFC/Unicode/control、012null入力/列長/必須要素/encoder・固定例外、013入力/返却Listとbyte所有、014SQL風literalもCOPY dataで独立escape、015finite8worker64task/Future5/finallyshutdownNow-await10、016redactionと拒否後独立正常。expectedはDDL/手書きASCII・UTF8 literalと算術、Production/Current generatorによるexpected生成0。

新Row1＋必要codec1の全2Main/2physical、新16＋支援codec12=whole28を同source/一exec・Root通常静的/NullAway/lintWerror・独立CRC-init/XML/四100/実Code一致で確認。旧成功12の確認再演でなく新接続に必要なscope。追加不足1.25/3.75/7.5未較正を、詳細+PG16 .85/2.55/5.1cap6、必要normal28 .4/1.2/2.4cap3に分離、元費用/SV上限保持・専有費/実token null。全Root/native/Actual4/aru/実DB/全ETL/CHR/global451/ITST/HOLDを閉じない。
