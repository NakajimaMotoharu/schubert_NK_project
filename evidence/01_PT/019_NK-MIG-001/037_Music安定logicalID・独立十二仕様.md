# Music安定logicalID・独立12仕様

NK-MIG-001/MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI254、SS311/331/34310.1.4 SSC356、WBS-P01903.02。

UI242§5のMusic logical IDをbootstrap.migration.MusicLogicalIdで生成する。RD MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004、UI223/242/254、SS311/331/34310.1.3、WBS-P01903.02。CurrentのBase64URL→NK logical ID対応manifestとcollision0・129実file一致・pair/order・実DB/全ETLは後続独立条件。全Mainに固定prefix SCHUBERT-NK:MUSIC:のProduction処理が未存在であることをsource監査済み。既Row/Batch/codec/外部UI仕様は変更しない。

stateless final classのfromDisplayPath(Nullable String)はJava25必須SHA-256の新MessageDigestを毎回取得、固定ASCII prefix SCHUBERT-NK:MUSIC:のUTF8 byteを先にupdateし、その後NFC化したdisplay path UTF8のdigestをHexFormatで小文字64hexにする。NFC以外のcase変換/trim/区切り置換/filename削除/extension変更をしない。pathは既sanitized display metadataであり、実file解決・storage path認証を担当しない。null/孤立surrogate/ISOcontrol/NFC後UTF8 byte0又は513以上を固定IAE、制御診断・toStringは固定redactedでpathを保持しない。NFC前768byteでもNFC後512byteなら許容する。

JDK標準NoSuchAlgorithmExceptionは直接callerへ伝播し、別algorithm/provider選択/fallback/成功への変換を追加しない。qualified Java25でSHA-256の存在を実行positiveで確認する。provider欠落を作るためのSecurity provider登録変更/削除・権限変更は行わない。環境不整合時の起動処理側の対処は別の未検証条件として保持し、checked例外をcatchして正常扱いしない。依存はJava標準/JSpecifyだけ、DB/秘密key/署名/Root/native/FS/aruを操作しない。

PT-MIG-MUSICID001..012: 001ASCII固定vector、002日本語UTF8固定vector、003NFC/NFDの同一固定vector、004null/空、005孤立surrogate/正pair、006全ISOcontrol negative、007ASCII1/512/513境界、008NFD768→NFC512/514境界、009supplementary128文字512byte/129文字516byte、010case/空白/区切り/句読点を保持する各固定vector、011fixedredaction/拒否後独立正常、012finite8worker64task/Future5/finallyshutdownNow-await10。期待値はJava productionを呼ばずPython標準hashlibの独立計算で事前固定、canonical NFCには手書きéを用い入力NFDはe+combiningを別fixtureとする。秘密/masterをfixtureへ入れない。

全1Main/1physical/whole12を同source/単一exec・Root通常静的/NullAway/lintWerror・独立CRC-init/XML/四100/実Codeで照合。旧成功の確認再演/別source合算0。追加不足.7/2.1/4.2未較正を、詳細+PG12 .45/1.35/2.7cap3、必要normal12 .25/.75/1.5cap2へ分離、元費用/SV上限保持・専有費/実token null。実129file/Current対応/全migration/DB/Rootnative/CHR/global451/ITST/HOLDを当pure hash成功で閉じない。
