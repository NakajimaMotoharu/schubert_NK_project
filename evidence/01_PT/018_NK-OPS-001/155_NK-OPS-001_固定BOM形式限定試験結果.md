# 155 固定BOM形式・限定試験結果

018153 / NK-OPS-001 / SS343 §11.1 / SSC096 / PG-D313。PT-OPS-BOMPROFILE-001～016は独立literal JSON・固定六列行・path/数字/集合/並行fixtureを期待値とし、Production encodeや実DBからoracleを生成しない。

2026-09-28 04:03:44 JST、JDK25.0.4/Maven3.9.12/Linux7.0.0-34、branch dev-foundation/source base691f661fe。実command・変更source/POM個別hash・全selected JUnit・coverage・static XMLのhashは `evidence/provisional/PG313-bomprofile-2/manifest.json`。ResourceScope8＋Approval8＋Signature8＋Profile16＝40 PT、exit0、failed/error/skipped0、SpotBugs0。非clean限定runの古い他suiteは合格に算入しない。

Profile/Artifact/Dependencyの3classはline242/method29/class3/branch102、全6counter missed0。初回40 PT成功時の末尾比較1branch未網羅はPG-D313に固定Gson STRICT bytecode根拠を記録し、`peek()`の末尾検査そのものを残して二重比較だけを削除した。異常trailing literalの拒否期待は不変更。旧XML/coverageと当時source hashは `PG313-bomprofile-1/manifest.json` に分離した。coverage除外は追加していない。

独立collector preflight: Approval8/Reader8/Signature8/Profile16のclass・method・owner・PT prefixを022/019へ登録。BUG290/YKT223の旧Batch件数を221 deployment＋287専用＝508へ更新、旧500を拒否する負caseも追加。105canary全成功（exit0）。全6 source固定回帰は本保存commitから開始予定であり、現時点では未合格。

ここで認定したのはclaims parserと署名primitiveの限定PTのみ。固定root keyの実読取/発行、同一held scopeの全payload/ZIP/SQL CRC/platform照合、opaque root proof、MorningDB begin前schema、業務main/R2/実NK CHR/R3は未完了。正式run24/1964PT/53scope/48.3%を更新しない。秘密key/credential/token/DB dumpは格納していない。
