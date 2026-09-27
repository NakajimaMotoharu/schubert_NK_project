# PG313 署名・BOM・schema結線PT（実装前）

NK-OPS-001/DAT009/SYS002004/OPS009/UI212251253/SS34311.1/SSC096、D02/04/05。配備主体は既存信頼済みtoolchain、候補release jarを検証/承認発行者にしない。固定Ed25519・pinned Ed25519 X509 DER公開鍵のみを使用、原manifest byteへ署名検証。原本へ任意algorithm/key/pathを入れず、通常材料catalog不変更。検証component自体のpublic入力を承認能力としない。全BOMとM/A・全停止・INVALID・固定原本atomic発行が未結線ならfullgate false。

PT-OPS-SIGN001～008: RFC8032§7.1 TEST1/2の公開key/message/signature固定literal正常、message/signature/別公開keyの1byte改変、DER prefix/44byte/NULL/未知algorithm型拒否、signature0/63/64/65byte・manifest0/1048576/1048577境界、入力防御copy・finally所有buffer消去、既知GeneralSecurityExceptionは固定IOExceptionでcause無し、未知Runtime/Errorのidentity保持と非正常化、真正4thread/8call並行でprovider状態不共有、native Ed25519 malformed point/signatureの固定拒否。秘密key/vectorのprivate部分は格納/使用しない。expectedは公開RFC literalでありProduction signer/verifyを呼んで作らない。署名を再serialize JSONやmanifest SHAだけへかけない。

BOM後続PT: fixed strict profileの全key/型/重複/null/境界/UTF8/末尾・相対path/順/重複/祖先衝突、3thinjar/全dependency配置/shared SHA一致、保持directory子集合完全一致/未知file-dir/symlink/metadata/RO/current/原本前後置換、API同梱SQLの名前/byteと外置きSQL一致、原SQL固定Flyway13.4の独立CRC vector、SHA256SUMS自己除外/manifest原byte/全payload列一致。根拠source/全Test ID/各class/method/command/OS-JDK-tools/sourcehash/結果/4coverage/BUG/証跡は実装確定時154以降へ追記し、未実装・未実行を加算しない。

line/method/class/branch100%、null契約/静的/全例外・並行・独立oracleを維持。途中限定greenでは全scope認定しない。署名publisher/native固定key/原本/root fullBOM/schema/親beginの実経路完成時に実Unit/同source security横断回帰を実施する。

PT-OPS-BOMPROFILE001～016/ReleaseInventoryTest: 001literal13payload/3shareddependency/SCHEMA0+SQL1と全metadata getter、002全固定key/順/duplicate/unknown/型/末尾、003null/0byte/1MiB/1MiB+1/不正UTF8/BOM、004厳密十進/Long/Javafeature境界、005全ASCII相対path/Artifact constructor null/size/hash、006Dependency coordinate/path/list/null/defensive copy、007固定必須payload/昇順重複、008管理file自己hash/祖先file衝突、009全lib登録集合/共通sizeSHA/二重所属、0103sharedversion/固定role一配置、011SQL名前全集合/rank/schema/失敗/欠落、012checksum signedint/nullable限定/六列型、013原byte防御copy/全collection不変、014payload2048/2049・dependency512/513・migration1000/1001とpaths3/4、015全metadata scalar/null/空/非ASCII、016真正4thread同時parse。Fixtureはtest内literalJSON部品と独立TreeMapで作り、Production encode/getterや運用DBからexpectedを作らない。入力shape検査だけで実BOM/署名/SQL CRC/DB gate成功を主張しない。

新parser依存は既存API/Webと同じGson2.14.0、Maven Central取得済み正本 `https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.14.0/`、jarSHA256 `2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f`。JDK25.0.4/Maven3.9.12/offline固定repositoryで再現する。Bootstrap compile追加に伴うruntime classpath/全security回帰はbundle完成時に実行、既存full結果へ混在しない。
