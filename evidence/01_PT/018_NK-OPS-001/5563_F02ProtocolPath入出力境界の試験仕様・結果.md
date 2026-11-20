# F02のProtocol Path依存境界

SS311 §2～4、WBS-F02-a、BUG-3454、YKT-2758。工具 `ModuleDependencyAudit.protocolFilesystem` はProtocolから実ファイルを照会するPath操作を検出する。tool source `939a666fe7fc7aefe6440ccf1ca04ea9ee0ab8da`、製品Core `24da3b252f65f0ea56736cb791cd13165bf62c24`。JDK 25とArchUnit 1.4.2の固定入力。合成classのメソッドは呼び出さない。

| Test ID | 合成classの直接依存 | SS311に基づく期待 | 修正後 |
| --- | --- | --- | --- |
| PT-F02-PATH-IO-001 | Path.toRealPath、NOFOLLOW_LINKS | FRAMEWORK_FENCESで報告 | 一致 |
| PT-F02-PATH-IO-002 | Path.register、event配列 | 同上 | 一致 |
| PT-F02-PATH-IO-003 | Path.register、event配列とmodifier | 同上 | 一致 |
| PT-F02-PATH-IO-004 | Path::toRealPath | 同上 | 一致 |
| PT-F02-PATH-IO-005 | Path.normalize | 値操作、報告なし | 一致 |
| PT-F02-PATH-IO-006 | Path.resolve | 値操作、報告なし | 一致 |
| PT-F02-PATH-IO-007 | Path型のfield | 型参照、報告なし | 一致 |
| PT-F02-PATH-IO-008 | StorageでのPath.toRealPath | Storageの担当、報告なし | 一致 |

元PG41062の工具終了0は禁止4件の見逃し。修正後PG41064の工具終了1は、意図的に禁止を含む合成入力で期待どおり。判定は8/8、旧対照82/82、合成130物理で期待57辺と実際57辺が一致。独立PG41066は期待する追加4辺を固定し、保存済みProtocol Maven JARのSHA-256・176物理inventory・製品Coreまでの当入力差0を確認した。同JAR一つと空の合成anchor五つだけを解析し、実Protocolの指摘0。元製品PT再実行0。対象は工具とProtocolのF02個別証拠。製品六JAR、Runtime、451、製品coverage、QA-056の保留範囲は未受入。

実行手順は `python3 -B evidence/01_PT/018_NK-OPS-001/input/5571_f02_protocol_path_io.py before`、同 `after`、`python3 -B evidence/01_PT/018_NK-OPS-001/input/5572_f02_protocol_path_independent.py`。元runごとの入力・コマンド・終了値・出力ハッシュは証票に保存。元scanのSHA-256は公開証票に保持し、合成classの型名とハッシュを二項目の配列にして公開した。

[修正前](evidence/PG41062-f02-protocol-path-io-before-v1/receipt.json) [修正後](evidence/PG41064-f02-protocol-path-io-after-v1/manifest.json) [独立・実Protocol JAR照合](evidence/PG41066-f02-protocol-path-io-independent-v1/manifest.json)
