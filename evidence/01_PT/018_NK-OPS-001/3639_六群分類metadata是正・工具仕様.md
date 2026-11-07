# 六群分類metadata是正・工具仕様

BUG2418/YKT2163、WBS-G13.07、487。対象6群12event/着手139～149の奇数6件。元events/見積/実費/実source/試験oracleは不変。誤った補助ラベルと参照説明を追記で対応付ける。QA054のSSC337参照は別LogCleanupであり既030/031の訂正を維持する。

工具pmo_group_context.build_context/validate_context。群固有labelはgroup_idから生成、event writer所有groupIdを返さない。明示work分類/活動種別/実scope/公開MD・JSON参照のhash必須。ファイルアクセス、実行許可、受入、費用配賦は行わない。実hash/source照合は別検証が担当。

| Tool Test ID | 入力・期待値（独立根拠） |
|---|---|
| PT-TOOL-CONTEXT001 | 同群context一致、別群/旧labelを拒否、writer groupIdなし |
| 002 | 必須引数と空参照を拒否 |
| 003 | 絶対/親/非正規/private/held/非MD・JSON pathを拒否 |
| 004 | 不正group/category/kind/空・過長scopeを拒否 |
| 005 | 不正hash/source/余分schemaを拒否 |
| 006 | 同path/source重複を拒否、明示した異なる歴史sourceは保持 |
| 007 | 入力参照を変更せず、返却値の変更も入力へ伝播しない |

全て有限host純Python、ネットワーク/VM/DB/業務processなし。Product試験件数/coverage/451へ加算しない。実行環境は当host既存python3、commandは実行結果manifest、pre-run HEAD48a7b81/dirty工具二sourceをhashで固定。null・欠落・未知・unsafe・重複観点は上表、並行/再送・DB・JMSは対象外（I/Oなし）。
