# Artemis配置雛形の現候補schema検証

Program NK-MSG-001。WBS-P005-01/2、PT-JMS-001の配置雛形の範囲、RD MQ-001～005、UI231、SS321 §3～5。PG43574の固定source `a2e709c214485d9cb9e678b1d6ba169860b1bc36`。JDK25.0.4と記録済みArtemis 2.56.0の四XSDを使い、現在の追跡broker.xmlを隔離先で照合した。

- 実ファイルに対するschema検証成功。メモリ内でdurableを真偽値以外に変えた独立負例は拒否。
- 六つの固定Addressと明示ANYCAST Queueが独立設計表に一致。Queueのdurable要素は未記載で、採用schemaのqueueTypeはdefault=true。persistence-enabledは明示true。
- 開始・終端、JDK実体と四XSD、対象のhashはmanifestで固定。JDK解析のみで、製品PT・coverageの追加0。

実Brokerの配備時durable／routing、権限、実配送・paging・Expiry、C04／P002-03と451は未認定。この結果は局所設定の証拠として使う。

- manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG43574-broker-template-durable-offline-current-v1/manifest.json`
- SHA-256 `6503b229e6eda954a6a1a5bbad1fc2f4b3121b6b5f382d5182983e24e46f9f06`
