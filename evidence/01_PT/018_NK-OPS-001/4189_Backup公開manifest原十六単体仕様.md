# Backup公開manifest原十六単体仕様

NK-BAT-001 / BackupManifest/BackupVersions/BackupFileDigest/BackupManifestCodec、依存BatchRun/BatchStep/BatchStepAttempt、RD BAK/BKO/OPS009・UI251・SS3313416.43435.3351352/SSC058。原whole BackupManifestValuesTest8（BAT178..185）＋BackupManifestCodecTest8（BAT186..193）、元Fixture helperは不変更・抜出し無し・新定義0。BUG2742二workerは8thread/64taskのFuture5/finally shutdownNow-await10、逆変換旧本文一致とGJF全token一致で全期待値保持。

値8: 713total/712config/二step固定bindingとJSTディレクトリ文字列、digest正数/longmax/64小文字hex・総和overflow、token128/schema001-999/000拒否、step列挙全種類・skip/id/run不一致、時間順/microsecond/年1-9999/JST年跨ぎと1887LMT/1948DST/1952標準時の固定literal/null全field/redaction/record不変性/64並行。

Codec8: 手書golden965byteの固定SHA256 733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e・生産encode出力完全byte一致、全field最大長1873byte/longmax合計/99attempt、golden全965位置×~ NUL FFの構造変異・BOM/CRLF/日本語/末尾改行、非canonical数/UUID/日時/閏日/精度/大文字hash/重複id/schema000、missing/unknown/duplicate/order/null各field、0/1/4095/4096/4097/null、caller入出力防御copy/返却64配列identityを独立literal/既golden resourceから検証。生産decode/encodeをexpected生成に用いず、元goldenとfixtureを使用する。

全Main7はJDK/JSpecifyのみ、TestsはJUnitのみ。既CodecTestの出力は新run cwd/target/backup-manifest-tracesの公開synthetic claims JSONであり、実dump/config/credentials/原本DB/鍵/署名を生成・読取しない。Root25 NullAway/fullPMD-security-concurrency/CS-SB-GJF/同source一exec・全physicalCRC・全source四counterを独立確認し、helper未網羅はfull7に保持、独自除外/旧exec合算無し。command・環境・source/branch・exit/XML/input/expected/actual/hashはPG28156/58/60/64/66、結果4190へ。P01705親実Backup/commit/prune/所有/native・CHR/451全体の受入ではない。旧PG495のsourceFilesSha256はaggregate文字列で個別byte一致不明、BUG2741/PG28143を保存しnullのまま転用0。
