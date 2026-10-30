# 2790 ProtocolCarrier不足境界六件結果

2026-10-30 22:32 JST、Production6b53/normal14216固定、branch dev-foundation。新規六method/1 suite/own一JVMはlint/compile/実行0、F/E/S0。新execのみでFieldValue全5physicalとFieldValueSetを測定し、旧execとのunionなし。2798等の歴史成果・元31は再実行していない。

|測定|missed / covered|
|---|---:|
|LINE|0 / 28|
|METHOD|0 / 13|
|CLASS|0 / 5|
|BRANCH|0 / 10|

FieldValueSetは四counter100、FieldValueは非空L/M/C100・B自然0/0 N/A。その他五interface Sourceは真NoCode N/A。全7Source11physical、Code5/metadata6、未達Source0、厳格全Source四100は1（N/Aを100%にせず全体strict exit1）。既151protocol Sourceとの非重複7候補が揃ったが、現registry280へ未結合であり158Source全体の結合認定は未実施。

## Test ID・実結果・証跡

PT-OPS-2789-01～06は全PASS。固定redaction/UTF16長/long極値/flag/enum、空/未知/null、順序と元map分離/names不変、null map/key/value/四種blank、equals全条件/独立hash82/83、own2reader/4result/finally停止を確認。期待値は2789と全公開新Test bodyに固定。実OS/JDK、source、開始終端、終了code、command、input/Test hashes、独立exec、XML6は下記manifestに保存。

- PG14868 raw SHA256 `7dce0ee6ffd042a498ae7bfcbf20d9f2d5a0ce0f82d3e9e8ed716e6211a0bd55`、entry `44aaaac87b5151abff35d2f7fb2c6928dec911e17000018784dde9af8516ed50`、session20042真正0。
- PG14871 v2 post SHA256 `87d29dc4e02b03e422270d4f9ebfc5a8b68456804f837c1c338ba1d8b8986696`、entry `27faa697a61c20b576025f6986ada91fca5f6b443c8b33a0ffd20b865099b8c3`、session65317真正0。
- PG14872独立 SHA256 `12915c28abce5e6e951ac923a4bdf5ec7373bdae449317689f036a6fe4f9c78f`、entry `7da273ee1166c5a9abbc0a4b70fe6b6eb26187064c3feba0f0cdbf9de2b98a1b`、真正0。22意味反例、全XML/11class Code/CRC/Source分類・counter全合計・新6非重複、owner namespace二正常二異常を確認。

全pathは `evidence/provisional/<PG番号の上記run名>/manifest.json`。新Test hash bd1da8b0、launcher5132d007。原src Main/Test/normalのbyteは変更せず、追加PTはtools/quality/architecture配下で独立保存。論理artifact/cost ownerを推定せずUNKNOWNを保持する。

## BUG2114 / YKT1861（工具scope限定完了）

旧14870/effb718aはsrc限定owner APIへのtools Test path混入でbody1、SLOT/OUT作成前。原6試験は成功のまま、再実行0。修正前915/916起票後、新14871v2で正確な一tools TestだけUNKNOWN、src正本APIは凍結不変更。新独立14872で正本ownerの正常/工具UNKNOWN/未知工具拒否/alias拒否を確認した。

横展開対象：旧14870は失敗凍結、新14871は是正確認、共有trace_owner_joinはsrc限定の正しい契約で非該当（元invocationのhash不変）、原14862は全Main/Testがsrcなので非該当（元独立14864とhash保持）、runner14868はowner API不使用・原6真正0で非該当。実XML/全closure/新execを確認し検索だけで完了にしていない。修正commitは本結果・台帳を含む最初、完了日2026-10-30、工具限定で全体品質の合格ではない。

生成draftはliteral安全helperで14862から作成し、未実行draft段階で新Test hashのnormal外保存を明示したが、owner namespace差の反映漏れは上記BUGとして保持。旧工具は編集・再実行せず、製品再演なし。

現正式1964/53・旧17/190・工数null・QA051final・F03/451/G07/外部HOLD不変。現registry908/131・280Source354physical、候補は914/132・287Source365physical・61JVM994method。新六は準備済みだがregistryへ未結合、当小群受入/工程完了0。実VM/DB/JMS/Graph/鍵/Root/native操作0。
