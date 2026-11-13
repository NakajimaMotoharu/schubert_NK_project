# NK-CHR-001 QA054相関ログ全source通常十一仕様

対象CorrelatedLogEvidenceValidator全source325行・全17method、WBS-P020-01。QA054/UI264/SSC336/SS351/355、451。元9whole通常試験はbyte期待値を保持し、追加2定義（予定whole11）で未測定の独立条件を確認する。Production src/Main98と当ToolMainは変更予定なし。

PT-CHR-LOG-COR-010: 独立固定ACTION current menu/log_searchとNK MENU_VIEWED/LOG_SEARCHEDを同operationで各一件作る。MENUはNK GET / 200・N12=0、LOCAL/OUTBOX両stage・同event/全HTTP値を明記、API側LOG_SEARCHEDへWeb witnessを要求しない。異operationの同pairも各一件で分離。期待validate failures空。片側欠落、両側二重初回成功、NK MENUのPOST/別path/201は固定PAIR又はEXPECTED_PAYLOADの具体failureを要求する。未知ACTIONの一般免除を導入しない。

PT-CHR-LOG-COR-011: 任意responseBytesはtext/負数/1000000000000/long超過を拒否。集合sizeを同じに保ち必須fieldだけ別名へ置換してもshapeを拒否。単に別の失敗に頼らず、固定EXPECTED_PAYLOAD等の対象diagnosticをassertする。JSON fixtureは固定literalから作成し、production validatorの戻り値でexpectedを作らない。ログ実採取/DB後条件の代替ではない。

安全範囲はpureJSONとJUnit所有worker既2だけ。実DB/VM/Root/HTTP/Browser/native/credential/原本/拒否PT操作0。通常wholeclassを使用し、method抽出・approval代用なし。RootJava25offline compile、全Main5/physical10を保持した実測からCorrelated全source四coverage100と独立postを確認予定。全工具bundleのGateCli whole12容量HOLD・他source未網羅を除外しない。元46成功の確認再演はせず、変更後Correlated whole11のみ新規必要試験。

各source/hash/固定Testsource/run/実日時/command/exit/XML/coverage/静的適用性は実行manifestへ保存。元費用・前群残価格・正式1964PT/53scope/原190新0・工数率nullは維持、予測1.35ppは実費でも受入率でもない。
