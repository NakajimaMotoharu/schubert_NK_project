# F03 現Main保存指摘・review参照結合 結果

2026-10-31 13:05 JST / PG-D973 / 群3381。3046は着手仮説を保持し、**962不変/三変更という仮説はBUG2152で不成立**。実物は全965Main中954不変/11変更。対応する8は保存13505/13534、query三は14226で同byte確認でき、原解析の再演なし。製造Mainだけの現source保存指摘ledgerを作った。現在のauxiliary全体を再解析したものではない。

原global PG13253 `751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf` のMain1502から変更11の旧指摘を外し、PG13505 `aaa38f93d84f57a9ef670699063e6f290fc863326badd2db9d7a4592730929bf` の現byte四、PG13534 `36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda` の現byte四、PG14226 `0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293` の三をXML/findings全hashで結合。全965MainのGit/worktree byte一致を独立確認。Test856・CHR四は対象外、旧raw1491という歴史集計と今回の現path-byte照合を区別する。

- 新15930/f99d963d、`PG15930-f03-current-main-review-join-v2/manifest.json` SHA256 `7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983`、真正0。全1491raw/選択review参照283/選択未参照1208、元重複occurrenceを保持。965全source、1491全row、未参照queue、入力67のpath/hashを保存。
- 独立15933/64df3b27、`PG15933-f03-current-main-review-post-v2/manifest.json` SHA256 `e624a558bcfcbdc56b7a6eaead17a52adbaa525e72fc0159a74f34929d600e17`、真正0。別のXML再構成・全965byte・全67input/row対応と24変異拒否。BUG2152の三変更偽装、raw欠落・重複/誤byte・座標/レビューPASS・PT免除・旧runtime・偽参照・queue欠落を拒否。
- 公開pathは全て `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 配下。実行commandは3046同様checked Python entry、新scanner/元PT/VM/DB/鍵/Root/cohort/外部0。

BUG2152/YKT1899：旧15928/ff7c6b8bは実11に対し三を要求しguard/body1・OUT前、誤結果/WBS更新なし。旧toolを凍結、全11の四＋四＋三証跡と三偽装の拒否で有限対象を是正した。

BUG2153/YKT1900：旧独立15932/35771d62は67中一つの別schemaへrowsを要求しKeyError/body1・OUT前。新版は全67のschemaと元row数を照合、`PG13044-reference-identity-context-v2` は当loader未対応dictで**0row・未適用**と明示。未知schemaからの虚偽参照はhash/厳密row結合・false-ref変異で拒否。対応する有効参照を補う後続は別作業であり、当未適用を合格にしない。両旧失敗は新manifest/公開prior-failure.safe.jsonで保存、元解析/受入不変更。修正commitは次保存後に台帳追記する。

67inputは全既存F03レビューを網羅する一覧ではない。283は今回のfamily名/review.json/rows形式に限った厳密参照数、1208は当選択で未参照という意味だけ。source不一致や別schema、contexts/dispositions形式の既レビューを未レビュー/違反へ断定しない。参照があっても適用性未確定・PT免除False・actualViolation null、F03/451/正式1964-53/歴史17/工数null/QA051final/外部HOLDは保持。

着手0.5/2/5共有pp cap10固定、開始50→13:05 fresh50、実費/N-Tnull。修正前仮説の是正はTOOL手戻り、元計画消化/新受入にしない。次は当1208のうち既存別schema/contexts/dispositionsの照合可能部分を整理し、必要な個別source-methodレビューと厳密trace補完へ進む。通常小群/commitで停止しない。
