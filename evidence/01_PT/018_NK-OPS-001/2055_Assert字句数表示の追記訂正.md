# assert字句数の表示訂正（BUG1821/YKT1572）

2026-10-26 15:35 JST。原tool/manifest/eventは不変のまま、PG10349原a9546154434952712380f83b4752af700ca0d62895bcfc9b5537ba9d8527e811でqualified normal snapshot/source SHAへ再照合した。

|元manifest/field|原報告値|正しい意味|実assertion呼出し数|
|---|---:|---|---|
|PG10287.originalAssertionCounts|75/33、計108|コメントを除くLEX tokenのうちassertで始まる字句。static import/helper名等を含む|未計測null|
|PG10304.assertionCounts|75/33、計108|同上、source4cの値|未計測null|
|PG10339.assertionCounts|129/35/78/61/113、計416|同上、source2e1の値|未計測null|

正式labelはASSERT_PREFIX_TOKEN_OCCURRENCES_NOT_ASSERTION_INVOCATIONS。元108/416を「assertion件数」とする関連説明は本訂正を優先する。Query010011/2052～53、456460の歴史説明、event2350/2360のmeasured.originalAssertionsPreservedという数値field及び開始2361の文言が確認済み訂正対象。event2362へ原を残す追記訂正を保存、予算/原開始見積りを変えない。event2344等は確認候補であり数値誤fieldの存在を断定しない。

元全source token復元一致とallOriginalAssertionsPreserved=trueの根拠は有効で、保持を否定する訂正ではない。実呼出し数の独立計測は行っておらず、tokenから推定しない。JUnit XMLのPT件数/coverage/正式1964PT・53scope/既17・190/工数null/全予算/実費へ変更なし。assert字句数を製品PT/受入へ加算した実績はない。

PG10349のsourceはmulti-source metadata訂正としてnull、各rowに原source/manifest path/hashと元値を保持する。原Root/DB/key/PTを再演しない。誤label/実呼出し数の捏造/別countの三変異をactual guardで拒否した。新PG10348は正しいfield名と実呼出し数nullを使用し、将来の表示へ誤semanticを持ち越さない。費用配賦や品質条件の緩和ではない。
